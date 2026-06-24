"""
Agent Service — Multi-step game generation using MiniMax API.

Workflow:
  Step 1: creative_analysis  — Parse user input into structured game concept
  Step 2: game_design        — Generate detailed game design document
  Step 3: code_generation    — Generate runnable HTML/JS game file
  Step 4: upload             — Upload artifact to MinIO, update game record
"""

import uuid
import json
import httpx
import traceback
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.game import Game
from app.models.agent_log import AgentLog
from app.services.storage_service import upload_html_content

settings = get_settings()

# ---- Step definitions ----

STEPS = [
    {
        "name": "creative_analysis",
        "order": 1,
        "prompt_template": """You are a game design analyst. Analyze the following creative input and extract structured game concepts.

User's creative idea:
{user_prompt}

Respond in the following JSON format ONLY (no extra text):
{{
  "gameplay": "brief description of core gameplay mechanics",
  "style": "visual/art style (e.g. pixel art, minimalist, cartoon)",
  "characters": ["list of character names or roles"],
  "win_condition": "how the player wins",
  "lose_condition": "how the player loses",
  "game_type": "category (e.g. puzzle, adventure, action, trivia)",
  "mood": "overall mood/tone of the game"
}}""",
    },
    {
        "name": "game_design",
        "order": 2,
        "prompt_template": """You are a game designer. Based on the following game concept, create a CONCISE game design document. Keep descriptions short — this will be used to generate code, not a design bible.

Game Concept:
{creative_analysis}

Respond in the following JSON format ONLY (no extra text):
{{
  "title": "short game title",
  "description": "one sentence description",
  "gameplay_rules": ["3-5 core rules, each one sentence"],
  "interaction_model": "controls (keyboard/click/touch)",
  "scoring": "brief scoring rule"
}}""",
    },
    {
        "name": "code_generation",
        "order": 3,
        "prompt_template": """You are an expert web game developer. Generate a complete, runnable HTML file for a simple browser game based on the following design.

Game Design:
{game_design}

Requirements:
1. SINGLE self-contained HTML file, all CSS and JS inline
2. Focus on CORE GAMEPLAY only — implement the basic mechanics, skip fancy visual effects, particles, music
3. Use Canvas for rendering
4. Clean, minimal UI with score display and game-over screen with restart
5. Simple but polished visual style (solid colors, no complex animations)
6. Keep the code SHORT — aim for under 500 lines total
7. No external dependencies or CDN links
8. Must be immediately playable

Output ONLY the complete HTML code starting with <!DOCTYPE html>. No explanations.""",
    },
    {
        "name": "upload",
        "order": 4,
        "prompt_template": "",  # No LLM call needed for upload
    },
]


async def call_llm(system_prompt: str, user_message: str, timeout: float = 120.0, stream: bool = False) -> str:
    """Call Mimo LLM API (OpenAI compatible) and return the assistant's response text."""
    headers = {
        "Authorization": f"Bearer {settings.MIMO_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
    }

    if stream:
        return await _call_llm_streaming(headers, payload, timeout)

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{settings.MIMO_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        if resp.status_code != 200:
            raise ValueError(f"LLM API error {resp.status_code}: {resp.text[:500]}")
        data = resp.json()

    # OpenAI-compatible response format
    choices = data.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return ""


async def _call_llm_streaming(headers: dict, payload: dict, timeout: float) -> str:
    """Stream LLM response using SSE to avoid read timeouts on long generations."""
    payload["stream"] = True
    content_parts = []

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=30.0, read=timeout, write=30.0, pool=30.0)) as client:
        async with client.stream(
            "POST",
            f"{settings.MIMO_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        ) as resp:
            if resp.status_code != 200:
                body = await resp.aread()
                raise ValueError(f"LLM API error {resp.status_code}: {body.decode()[:500]}")
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    content = delta.get("content")
                    if content:
                        content_parts.append(content)
                except (json.JSONDecodeError, IndexError, KeyError):
                    continue

    return "".join(content_parts)


def create_agent_logs(db: Session, game_id: int):
    """Initialize agent log entries for all steps."""
    for step in STEPS:
        log = AgentLog(
            game_id=game_id,
            step_name=step["name"],
            step_order=step["order"],
            status="pending",
        )
        db.add(log)
    db.commit()


def update_log(db: Session, log: AgentLog, status: str, output: dict = None, error: str = ""):
    """Update an agent log entry."""
    log.status = status
    if status == "running":
        log.started_at = datetime.utcnow()
    elif status in ("success", "failed"):
        log.finished_at = datetime.utcnow()
    if output is not None:
        log.output_data = output
    if error:
        log.error_message = error
    db.commit()


async def run_generation(db: Session, game_id: int):
    """
    Run the full Agent generation pipeline for a game.
    This is called as a background task.
    """
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        return

    logs = db.query(AgentLog).filter(AgentLog.game_id == game_id).order_by(AgentLog.step_order).all()
    log_map = {log.step_name: log for log in logs}

    context = {"user_prompt": game.user_prompt}

    try:
        # Step 1: Creative Analysis
        log1 = log_map["creative_analysis"]
        update_log(db, log1, "running", output={})
        try:
            prompt1 = STEPS[0]["prompt_template"].format(user_prompt=game.user_prompt)
            result1 = await call_llm("You are a game design analyst.", prompt1)
            # Try to parse JSON from response
            creative_data = extract_json(result1)
            update_log(db, log1, "success", output=creative_data)
            context["creative_analysis"] = json.dumps(creative_data, ensure_ascii=False)
        except Exception as e:
            update_log(db, log1, "failed", error=f"{type(e).__name__}: {e}")
            game.status = "failed"
            db.commit()
            return

        # Step 2: Game Design
        log2 = log_map["game_design"]
        update_log(db, log2, "running", output={})
        try:
            prompt2 = STEPS[1]["prompt_template"].format(creative_analysis=context["creative_analysis"])
            result2 = await call_llm("You are a game designer.", prompt2)
            design_data = extract_json(result2)
            update_log(db, log2, "success", output=design_data)
            context["game_design"] = json.dumps(design_data, ensure_ascii=False)
            game.design_doc = design_data
            game.title = design_data.get("title", game.title)
            game.description = design_data.get("description", game.description)
            game.game_type = design_data.get("game_type", creative_data.get("game_type", ""))
            db.commit()
        except Exception as e:
            update_log(db, log2, "failed", error=f"{type(e).__name__}: {e}")
            game.status = "failed"
            db.commit()
            return

        # Step 3: Code Generation
        log3 = log_map["code_generation"]
        update_log(db, log3, "running", output={})
        try:
            prompt3 = STEPS[2]["prompt_template"].format(game_design=context["game_design"])
            html_content = await call_llm("You are an expert web game developer.", prompt3, timeout=600.0, stream=True)
            # Clean up: extract HTML if wrapped in markdown code block
            html_content = clean_html(html_content)
            if not html_content or "<html" not in html_content.lower():
                raise ValueError(f"LLM did not return valid HTML. Got: {html_content[:300]}")
            update_log(db, log3, "success", output={"html_length": len(html_content)})
            context["html_content"] = html_content
        except Exception as e:
            update_log(db, log3, "failed", error=f"{type(e).__name__}: {e}")
            game.status = "failed"
            db.commit()
            return

        # Step 4: Upload
        log4 = log_map["upload"]
        update_log(db, log4, "running", output={})
        try:
            import asyncio as _asyncio
            filename = f"{uuid.uuid4().hex}.html"
            # Run blocking upload in a thread to avoid blocking the event loop
            remote_url = await _asyncio.to_thread(upload_html_content, context["html_content"], filename)
            game.remote_url = remote_url
            game.status = "draft"  # Ready for preview, not yet published
            update_log(db, log4, "success", output={"remote_url": remote_url})
            db.commit()
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            print(f"[Agent] Step 4 upload failed: {error_msg}")  # server-side log
            try:
                update_log(db, log4, "failed", error=error_msg)
                game.status = "failed"
                db.commit()
            except Exception:
                pass
            return

    except Exception as e:
        # Mark the last running step as failed so the frontend can show the error
        error_detail = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        try:
            for log in logs:
                if log.status == "running":
                    update_log(db, log, "failed", error=error_detail[:1000])
                    break
            game.status = "failed"
            db.commit()
        except Exception:
            # Last resort: ensure game is marked failed even if log update fails
            try:
                game.status = "failed"
                db.commit()
            except Exception:
                pass


def extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    text = text.strip()
    # Remove markdown code block if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (```json and ```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise ValueError(f"Could not parse JSON from response: {text[:200]}")


def clean_html(html: str) -> str:
    """Clean HTML output from LLM, removing markdown wrappers."""
    html = html.strip()
    if html.startswith("```"):
        lines = html.split("\n")
        # Remove first line (```html or ```)
        if lines[0].strip().startswith("```"):
            lines = lines[1:]
        # Remove last line (```)
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        html = "\n".join(lines)
    return html.strip()
