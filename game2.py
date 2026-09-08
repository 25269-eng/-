import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="장애물 피하기",
    page_icon="🏃",
    layout="centered"
)

st.title("🏃 장애물 피하기")
st.caption("← → 방향키로 캐릭터를 움직이세요!")

game = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {
        box-sizing: border-box;
        user-select: none;
    }

    body {
        margin: 0;
        background: transparent;
        font-family: Arial, sans-serif;
        text-align: center;
    }

    #game {
        width: 400px;
        height: 600px;
        margin: auto;
        position: relative;
        overflow: hidden;
        background: linear-gradient(#87CEEB 0%, #dff6ff 70%, #78c850 70%);
        border: 5px solid #222;
        border-radius: 15px;
    }

    #road {
        position: absolute;
        left: 50px;
        right: 50px;
        top: 0;
        bottom: 0;
        background: #555;
    }

    .lane {
        position: absolute;
        width: 5px;
        height: 50px;
        background: #eee;
        opacity: 0.7;
    }

    #player {
        position: absolute;
        width: 45px;
        height: 55px;
        bottom: 25px;
        left: 177px;
        font-size: 42px;
        z-index: 5;
    }

    .obstacle {
        position: absolute;
        width: 45px;
        height: 45px;
        font-size: 38px;
        z-index: 4;
    }

    .coin {
        position: absolute;
        font-size: 30px;
        z-index: 3;
    }

    #score {
        position: absolute;
        top: 10px;
        left: 15px;
        color: white;
        font-size: 22px;
        font-weight: bold;
        z-index: 10;
        text-shadow: 2px 2px 3px black;
    }

    #startScreen, #gameOver {
        position: absolute;
        inset: 0;
        background: rgba(0,0,0,0.75);
        color: white;
        z-index: 20;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    #gameOver {
        display: none;
    }

    h1 {
        font-size: 40px;
        margin: 10px;
    }

    button {
        padding: 13px 30px;
        font-size: 20px;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        background: #ffcc00;
        font-weight: bold;
    }

    button:hover {
        transform: scale(1.05);
    }

    #hint {
        margin-top: 15px;
        font-size: 15px;
        color: #ddd;
    }
</style>
</head>

<body>

<div id="game">

    <div id="road"></div>

    <div id="score">점수: 0</div>

    <div id="player">🏃</div>

    <div id="startScreen">
        <h1>🏃</h1>
        <h2>장애물 피하기</h2>
        <p>← → 방향키로 이동하세요!</p>
        <button onclick="startGame()">게임 시작</button>
    </div>

    <div id="gameOver">
        <h1>💥</h1>
        <h2>GAME OVER</h2>
        <p id="finalScore">점수: 0</p>
        <button onclick="startGame()">다시 하기</button>
    </div>

</div>

<script>

const game = document.getElementById("game");
const player = document.getElementById("player");
const scoreText = document.getElementById("score");
const startScreen = document.getElementById("startScreen");
const gameOverScreen = document.getElementById("gameOver");
const finalScore = document.getElementById("finalScore");

let playerX = 177;
let obstacles = [];
let coins = [];

let score = 0;
let coinScore = 0;
let speed = 4;
let gameRunning = false;

let obstacleTimer;
let coinTimer;
let gameLoop;
let scoreTimer;

const roadLeft = 50;
const roadRight = 305;


// 방향키
document.addEventListener("keydown", function(e) {

    if (!gameRunning) return;

    if (e.key === "ArrowLeft") {
        e.preventDefault();
        playerX -= 25;
    }

    if (e.key === "ArrowRight") {
        e.preventDefault();
        playerX += 25;
    }

    // 도로 밖으로 못 나가게
    if (playerX < roadLeft) {
        playerX = roadLeft;
    }

    if (playerX > roadRight) {
        playerX = roadRight;
    }

    player.style.left = playerX + "px";
});


// 게임 시작
function startGame() {

    // 기존 장애물 제거
    obstacles.forEach(o => o.element.remove());
    coins.forEach(c => c.element.remove());

    obstacles = [];
    coins = [];

    playerX = 177;
    player.style.left = playerX + "px";

    score = 0;
    coinScore = 0;
    speed = 4;

    scoreText.innerText = "점수: 0";

    startScreen.style.display = "none";
    gameOverScreen.style.display = "none";

    gameRunning = true;

    clearInterval(obstacleTimer);
    clearInterval(coinTimer);
    clearInterval(scoreTimer);
    cancelAnimationFrame(gameLoop);

    obstacleTimer = setInterval(createObstacle, 900);
    coinTimer = setInterval(createCoin, 1300);

    scoreTimer = setInterval(() => {

        score++;

        // 일정 점수마다 속도 증가
        if (score % 100 === 0) {
            speed += 0.7;
        }

        scoreText.innerText =
            "점수: " + score + " 🪙 " + coinScore;

    }, 100);

    gameLoop = requestAnimationFrame(update);
}


// 장애물 생성
function createObstacle() {

    if (!gameRunning) return;

    const obstacle = document.createElement("div");

    obstacle.className = "obstacle";

    const types = ["🚗", "🪨", "🚧", "💣"];

    obstacle.innerText =
        types[Math.floor(Math.random() * types.length)];

    let x = roadLeft +
        Math.floor(Math.random() * 6) * 42;

    obstacle.style.left = x + "px";
    obstacle.style.top = "-50px";

    game.appendChild(obstacle);

    obstacles.push({
        element: obstacle,
        x: x,
        y: -50
    });
}


// 코인 생성
function createCoin() {

    if (!gameRunning) return;

    const coin = document.createElement("div");

    coin.className = "coin";
    coin.innerText = "🪙";

    let x = roadLeft +
        Math.floor(Math.random() * 6) * 42;

    coin.style.left = x + "px";
    coin.style.top = "-40px";

    game.appendChild(coin);

    coins.push({
        element: coin,
        x: x,
        y: -40
    });
}


// 충돌 판정
function collision(a, b) {

    return (
        a.x < b.x + 40 &&
        a.x + 40 > b.x &&
        a.y < b.y + 40 &&
        a.y + 40 > b.y
    );
}


// 게임 업데이트
function update() {

    if (!gameRunning) return;

    // 장애물 이동
    for (let i = obstacles.length - 1; i >= 0; i--) {

        let o = obstacles[i];

        o.y += speed;

        o.element.style.top = o.y + "px";

        // 충돌
        if (
            collision(
                {
                    x: playerX,
                    y: 520
                },
                o
            )
        ) {
            endGame();
            return;
        }

        // 화면 밖 제거
        if (o.y > 650) {
            o.element.remove();
            obstacles.splice(i, 1);
        }
    }


    // 코인 이동
    for (let i = coins.length - 1; i >= 0; i--) {

        let c = coins[i];

        c.y += speed;

        c.element.style.top = c.y + "px";

        // 코인 먹기
        if (
            collision(
                {
                    x: playerX,
                    y: 520
                },
                c
            )
        ) {

            coinScore += 10;

            c.element.remove();

            coins.splice(i, 1);

            scoreText.innerText =
                "점수: " + score +
                " 🪙 " + coinScore;

            continue;
        }

        if (c.y > 650) {
            c.element.remove();
            coins.splice(i, 1);
        }
    }


    gameLoop = requestAnimationFrame(update);
}


// 게임 종료
function endGame() {

    gameRunning = false;

    clearInterval(obstacleTimer);
    clearInterval(coinTimer);
    clearInterval(scoreTimer);

    cancelAnimationFrame(gameLoop);

    finalScore.innerText =
        "점수: " + score +
        "  |  코인: " + coinScore;

    gameOverScreen.style.display = "flex";
}

</script>

</body>
</html>
"""

components.html(game, height=650, scrolling=False)

st.markdown(
    """
    <div style="text-align:center; margin-top:10px;">
    🎮 <b>TIP</b> : 장애물 사이를 빠르게 이동하면서 🪙 코인을 모으세요!
    </div>
    """,
    unsafe_allow_html=True
)
