"""
Seed script: insert sample games and upload game HTML files to MinIO.

Usage:
    python seed.py
"""

import uuid
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.game import Game
from app.utils.security import hash_password
from app.services.storage_service import upload_html_content

# Sample game HTML templates
SAMPLE_GAMES = [
    {
        "title": "Dragon's Quest: Text Adventure",
        "description": "Embark on an epic text-based adventure to defeat the dragon and save the kingdom. Make choices that affect your destiny!",
        "tags": ["adventure", "text-based", "fantasy"],
        "cover_url": "https://picsum.photos/seed/dragon/400/300",
        "game_type": "text_adventure",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dragon's Quest</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Georgia', serif; background: #1a1a2e; color: #eee; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
.game-container { max-width: 600px; padding: 30px; background: #16213e; border-radius: 12px; box-shadow: 0 0 30px rgba(0,0,0,0.5); }
h1 { color: #e94560; margin-bottom: 20px; text-align: center; }
#story { line-height: 1.8; margin-bottom: 20px; min-height: 100px; }
.choices { display: flex; flex-direction: column; gap: 10px; }
.choice-btn { padding: 12px 20px; background: #0f3460; border: 2px solid #e94560; color: #eee; border-radius: 8px; cursor: pointer; font-size: 16px; transition: all 0.2s; }
.choice-btn:hover { background: #e94560; }
#stats { margin-top: 20px; padding: 10px; background: #0f3460; border-radius: 8px; text-align: center; }
</style>
</head>
<body>
<div class="game-container">
<h1>🐉 Dragon's Quest</h1>
<div id="story"></div>
<div id="choices" class="choices"></div>
<div id="stats"></div>
</div>
<script>
const scenes = {
start: { text: "You stand at the entrance of a dark cave. Smoke rises from within. A sword lies on the ground nearby.", choices: [{ text: "🗡️ Pick up the sword and enter the cave", next: "cave_with_sword" }, { text: "🏃 Enter the cave unarmed", next: "cave_no_sword" }, { text: "🚶 Walk away", next: "walk_away" }] },
cave_with_sword: { text: "With sword in hand, you venture deeper. A dragon appears! Its eyes glow red.", choices: [{ text: "⚔️ Fight the dragon!", next: "fight_dragon" }, { text: "🗣️ Try to talk to the dragon", next: "talk_dragon" }] },
cave_no_sword: { text: "You enter the dark cave. A dragon appears! You have no weapon.", choices: [{ text: "🏃 Run away!", next: "run_away" }, { text: "🧎 Surrender", next: "surrender" }] },
fight_dragon: { text: "You charge at the dragon with your sword! After an epic battle, you strike the final blow. The dragon falls! You find a treasure chest behind it.", choices: [{ text: "🏆 Open the treasure chest", next: "victory" }] },
talk_dragon: { text: "The dragon listens to your words. 'Brave mortal,' it says, 'I am cursed. Find the golden key in the forest to free me.'", choices: [{ text: "🔑 Search the forest", next: "forest" }, { text: "⚔️ Attack while it talks", next: "fight_dragon" }] },
forest: { text: "You find the golden key hidden in an ancient tree. You return to the cave and free the dragon. The curse breaks! A grateful dragon reveals a hidden treasure.", choices: [{ text: "🏆 Claim the treasure", next: "victory" }] },
surrender: { text: "The dragon sniffs you and laughs. 'You're not worth eating.' It lets you go. You escape with your life but no glory.", choices: [{ text: "🔄 Try again", next: "start" }] },
run_away: { text: "You sprint out of the cave! The dragon's fire singes your back but you survive. You live to fight another day.", choices: [{ text: "🔄 Try again", next: "start" }] },
walk_away: { text: "You walk away from adventure. Some say the cave still holds its treasures... Game Over.", choices: [{ text: "🔄 Try again", next: "start" }] },
victory: { text: "🎉 CONGRATULATIONS! You have conquered the Dragon's Quest! Your name will be remembered in legends!", choices: [{ text: "🔄 Play again", next: "start" }] }
};
let currentScene = "start";
function render() {
    const scene = scenes[currentScene];
    document.getElementById("story").innerHTML = "<p>" + scene.text + "</p>";
    const choicesDiv = document.getElementById("choices");
    choicesDiv.innerHTML = "";
    scene.choices.forEach(c => {
        const btn = document.createElement("button");
        btn.className = "choice-btn";
        btn.textContent = c.text;
        btn.onclick = () => { currentScene = c.next; render(); };
        choicesDiv.appendChild(btn);
    });
    document.getElementById("stats").textContent = "Scene: " + currentScene;
}
render();
</script>
</body>
</html>""",
    },
    {
        "title": "Memory Card Match",
        "description": "Test your memory! Flip cards and find matching pairs. How few moves can you complete it in?",
        "tags": ["puzzle", "memory", "casual"],
        "cover_url": "https://picsum.photos/seed/memory/400/300",
        "game_type": "puzzle",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Memory Card Match</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
.game { text-align: center; }
h1 { color: white; margin-bottom: 10px; font-size: 2em; }
.stats { color: white; margin-bottom: 20px; font-size: 1.1em; }
.grid { display: grid; grid-template-columns: repeat(4, 90px); gap: 10px; justify-content: center; }
.card { width: 90px; height: 90px; background: rgba(255,255,255,0.2); border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 36px; transition: all 0.3s; perspective: 1000px; }
.card.flipped { background: white; transform: rotateY(180deg); }
.card.matched { background: #4ade80; transform: scale(0.95); }
.btn { margin-top: 20px; padding: 12px 30px; background: #e94560; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
.btn:hover { background: #c73e54; }
</style>
</head>
<body>
<div class="game">
<h1>🃏 Memory Match</h1>
<div class="stats">Moves: <span id="moves">0</span> | Pairs: <span id="pairs">0</span>/8</div>
<div class="grid" id="grid"></div>
<button class="btn" onclick="initGame()">🔄 New Game</button>
</div>
<script>
const emojis = ['🎮','🎲','🎯','🎨','🎭','🎪','🎤','🎧'];
let cards = [], flipped = [], matched = [], moves = 0, canFlip = true;
function shuffle(a) { for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
function initGame() {
    cards = shuffle([...emojis, ...emojis]);
    flipped = []; matched = []; moves = 0; canFlip = true;
    render();
}
function render() {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';
    cards.forEach((emoji, i) => {
        const card = document.createElement('div');
        card.className = 'card' + (flipped.includes(i)||matched.includes(i) ? ' flipped' : '') + (matched.includes(i) ? ' matched' : '');
        card.textContent = (flipped.includes(i)||matched.includes(i)) ? emoji : '?';
        card.onclick = () => flipCard(i);
        grid.appendChild(card);
    });
    document.getElementById('moves').textContent = moves;
    document.getElementById('pairs').textContent = matched.length / 2;
}
function flipCard(i) {
    if (!canFlip || flipped.includes(i) || matched.includes(i)) return;
    flipped.push(i);
    if (flipped.length === 2) {
        moves++;
        canFlip = false;
        if (cards[flipped[0]] === cards[flipped[1]]) {
            matched.push(...flipped);
            flipped = [];
            canFlip = true;
            if (matched.length === cards.length) setTimeout(() => alert('🎉 You won in ' + moves + ' moves!'), 300);
        } else {
            setTimeout(() => { flipped = []; canFlip = true; render(); }, 800);
        }
    }
    render();
}
initGame();
</script>
</body>
</html>""",
    },
    {
        "title": "Space Shooter",
        "description": "Defend Earth from alien invaders! Use arrow keys to move and spacebar to shoot. How long can you survive?",
        "tags": ["action", "shooter", "space"],
        "cover_url": "https://picsum.photos/seed/space/400/300",
        "game_type": "action",
        "html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Space Shooter</title>
<style>
* { margin: 0; padding: 0; }
body { background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; overflow: hidden; }
canvas { border: 1px solid #333; }
</style>
</head>
<body>
<canvas id="game" width="480" height="640"></canvas>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
let player = { x: 220, y: 580, w: 40, h: 20, speed: 5 };
let bullets = [], enemies = [], score = 0, gameOver = false, frame = 0;
let keys = {};
document.addEventListener('keydown', e => { keys[e.key] = true; if (e.key === ' ') e.preventDefault(); });
document.addEventListener('keyup', e => keys[e.key] = false);

function spawnEnemy() {
    enemies.push({ x: Math.random() * (canvas.width - 30), y: -30, w: 30, h: 30, speed: 1 + Math.random() * 2 });
}

function update() {
    if (gameOver) return;
    if (keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
    if (keys['ArrowRight'] && player.x < canvas.width - player.w) player.x += player.speed;
    if (keys[' '] && frame % 10 === 0) bullets.push({ x: player.x + player.w/2 - 2, y: player.y, w: 4, h: 10, speed: 7 });
    bullets.forEach(b => b.y -= b.speed);
    bullets = bullets.filter(b => b.y > 0);
    enemies.forEach(e => e.y += e.speed);
    enemies = enemies.filter(e => e.y < canvas.height + 10);
    enemies.forEach(e => {
        if (e.y + e.h > player.y && e.x < player.x + player.w && e.x + e.w > player.x) gameOver = true;
    });
    bullets.forEach((b, bi) => {
        enemies.forEach((e, ei) => {
            if (b.x < e.x + e.w && b.x + b.w > e.x && b.y < e.y + e.h && b.y + b.h > e.y) {
                bullets.splice(bi, 1); enemies.splice(ei, 1); score += 10;
            }
        });
    });
    if (frame % 60 === 0) spawnEnemy();
    frame++;
}

function draw() {
    ctx.fillStyle = '#0a0a2a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    // Stars
    for (let i = 0; i < 50; i++) { ctx.fillStyle = 'rgba(255,255,255,' + (0.3 + Math.random()*0.7) + ')'; ctx.fillRect((i*97+frame*0.5)%canvas.width, (i*53+frame)%canvas.height, 1, 1); }
    // Player
    ctx.fillStyle = '#4ade80'; ctx.fillRect(player.x, player.y, player.w, player.h);
    ctx.fillStyle = '#22c55e'; ctx.fillRect(player.x + 15, player.y - 10, 10, 10);
    // Bullets
    ctx.fillStyle = '#fbbf24'; bullets.forEach(b => ctx.fillRect(b.x, b.y, b.w, b.h));
    // Enemies
    ctx.fillStyle = '#ef4444'; enemies.forEach(e => { ctx.fillRect(e.x, e.y, e.w, e.h); ctx.fillStyle = '#dc2626'; ctx.fillRect(e.x+5, e.y+5, 20, 20); ctx.fillStyle = '#ef4444'; });
    // Score
    ctx.fillStyle = 'white'; ctx.font = '20px sans-serif'; ctx.fillText('Score: ' + score, 10, 30);
    if (gameOver) { ctx.fillStyle = 'rgba(0,0,0,0.7)'; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = '#ef4444'; ctx.font = '48px sans-serif'; ctx.fillText('GAME OVER', canvas.width/2-120, canvas.height/2); ctx.fillStyle = 'white'; ctx.font = '24px sans-serif'; ctx.fillText('Score: ' + score, canvas.width/2-50, canvas.height/2+40); ctx.fillText('Press R to restart', canvas.width/2-80, canvas.height/2+80); }
}

document.addEventListener('keydown', e => { if (e.key === 'r' || e.key === 'R') { player = {x:220,y:580,w:40,h:20,speed:5}; bullets=[]; enemies=[]; score=0; gameOver=false; frame=0; } });

function gameLoop() { update(); draw(); requestAnimationFrame(gameLoop); }
gameLoop();
</script>
</body>
</html>""",
    },
]


def seed():
    """Insert sample data into the database and upload game files to MinIO."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Create a demo user
        existing_user = db.query(User).filter(User.email == "demo@aigame.com").first()
        if not existing_user:
            demo_user = User(
                email="demo@aigame.com",
                password_hash=hash_password("demo123456"),
                nickname="Demo Creator",
                auth_provider="local",
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"✅ Created demo user: demo@aigame.com / demo123456")
        else:
            demo_user = existing_user
            print(f"ℹ️  Demo user already exists")

        # Create sample games
        for game_data in SAMPLE_GAMES:
            existing_game = db.query(Game).filter(Game.title == game_data["title"]).first()
            if existing_game:
                print(f"ℹ️  Game '{game_data['title']}' already exists, skipping")
                continue

            # Upload HTML to MinIO
            filename = f"{uuid.uuid4().hex}.html"
            try:
                remote_url = upload_html_content(game_data["html"], filename)
                print(f"  📤 Uploaded '{game_data['title']}' to {remote_url}")
            except Exception as e:
                print(f"  ⚠️  MinIO upload failed for '{game_data['title']}': {e}")
                # Fallback: save locally
                import os
                os.makedirs("static_games", exist_ok=True)
                local_path = f"static_games/{filename}"
                with open(local_path, "w", encoding="utf-8") as f:
                    f.write(game_data["html"])
                remote_url = f"http://localhost:8000/static/{filename}"
                print(f"  📁 Saved locally to {local_path}")

            game = Game(
                title=game_data["title"],
                description=game_data["description"],
                cover_url=game_data.get("cover_url", ""),
                author_id=demo_user.id,
                tags=game_data["tags"],
                status="published",
                remote_url=remote_url,
                game_type=game_data["game_type"],
                user_prompt=f"[Seed data] Create a {game_data['game_type']} game",
            )
            db.add(game)
            db.commit()
            print(f"  ✅ Created game: {game_data['title']}")

        print("\n🎉 Seed completed!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
