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
        "prompt_template": """You are a game designer. Based on the following game concept, create a detailed game design document.

Game Concept:
{creative_analysis}

Respond in the following JSON format ONLY (no extra text):
{{
  "title": "game title",
  "description": "one-paragraph game description for players",
  "ui_layout": "description of screen layout and UI elements",
  "gameplay_rules": ["list of rules"],
  "levels": ["list of level descriptions or stages"],
  "assets_needed": ["list of visual/audio assets needed"],
  "interaction_model": "how the player interacts (click, keyboard, drag, etc.)",
  "scoring": "how scoring works",
  "difficulty_curve": "how difficulty progresses"
}}""",
    },
    {
        "name": "code_generation",
        "order": 3,
        "prompt_template": """You are an expert web game developer. Generate a complete, runnable HTML file for an interactive browser game based on the following design.

Game Design:
{game_design}

Requirements:
1. The output must be a SINGLE self-contained HTML file with all CSS and JS inline
2. The game must be fully playable in a browser
3. Use Canvas or DOM manipulation for rendering
4. Include clear instructions for the player
5. Include a score/progress system
6. Include a game over screen with option to restart
7. Make it visually appealing with CSS styling
8. The game should be fun and engaging
9. Keep the code clean and well-structured
10. Do NOT use any external dependencies or CDN links

Output ONLY the complete HTML code starting with <!DOCTYPE html>. No explanations before or after.""",
    },
]


async def call_minimax(system_prompt: str, user_message: str) -> str:
    """Call MiniMax API and return the assistant's response text."""
    headers = {
        "Authorization": f"Bearer {settings.MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.MINIMAX_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(settings.MINIMAX_API_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # MiniMax response format
    choices = data.get("choices", [])
    if choices:
        return choices[0].get("message", {}).get("content", "")
    return ""


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
            result1 = await call_minimax("You are a game design analyst.", prompt1)
            # Try to parse JSON from response
            creative_data = extract_json(result1)
            update_log(db, log1, "success", output=creative_data)
            context["creative_analysis"] = json.dumps(creative_data, ensure_ascii=False)
        except Exception as e:
            update_log(db, log1, "failed", error=str(e))
            game.status = "failed"
            db.commit()
            return

        # Step 2: Game Design
        log2 = log_map["game_design"]
        update_log(db, log2, "running", output={})
        try:
            prompt2 = STEPS[1]["prompt_template"].format(creative_analysis=context["creative_analysis"])
            result2 = await call_minimax("You are a game designer.", prompt2)
            design_data = extract_json(result2)
            update_log(db, log2, "success", output=design_data)
            context["game_design"] = json.dumps(design_data, ensure_ascii=False)
            game.design_doc = design_data
            game.title = design_data.get("title", game.title)
            game.description = design_data.get("description", game.description)
            game.game_type = design_data.get("game_type", context.get("creative_analysis", {}).get("game_type", ""))
            db.commit()
        except Exception as e:
            update_log(db, log2, "failed", error=str(e))
            game.status = "failed"
            db.commit()
            return

        # Step 3: Code Generation
        log3 = log_map["code_generation"]
        update_log(db, log3, "running", output={})
        try:
            prompt3 = STEPS[2]["prompt_template"].format(game_design=context["game_design"])
            html_content = await call_minimax("You are an expert web game developer.", prompt3)
            # Clean up: extract HTML if wrapped in markdown code block
            html_content = clean_html(html_content)
            update_log(db, log3, "success", output={"html_length": len(html_content)})
            context["html_content"] = html_content
        except Exception as e:
            update_log(db, log3, "failed", error=str(e))
            game.status = "failed"
            db.commit()
            return

        # Step 4: Upload
        log4 = log_map["upload"]
        update_log(db, log4, "running", output={})
        try:
            filename = f"{uuid.uuid4().hex}.html"
            remote_url = upload_html_content(context["html_content"], filename)
            game.remote_url = remote_url
            game.status = "draft"  # Ready for preview, not yet published
            update_log(db, log4, "success", output={"remote_url": remote_url})
            db.commit()
        except Exception as e:
            update_log(db, log4, "failed", error=str(e))
            game.status = "failed"
            db.commit()
            return

    except Exception as e:
        game.status = "failed"
        db.commit()


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
