import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벽돌 깨기",
    page_icon="🧱",
    layout="centered"
)

st.title("🧱 벽돌 깨기")
st.caption("← → 방향키 또는 마우스로 패들을 움직이세요!")

game = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">

<style>
    body {
        margin: 0;
        padding: 0;
        background: transparent;
        display: flex;
        justify-content: center;
        font-family: Arial, sans-serif;
    }

    #gameWrapper {
        text-align: center;
    }

    canvas {
        background: #111827;
        border-radius: 12px;
        border: 3px solid #374151;
        display: block;
        margin: auto;
        max-width: 100%;
    }

    #info {
        color: #333;
        font-size: 18px;
        margin: 10px;
        font-weight: bold;
    }

    button {
        padding: 10px 22px;
        border: none;
        border-radius: 8px;
        background: #2563eb;
        color: white;
        font-size: 16px;
        cursor: pointer;
    }

    button:hover {
        background: #1d4ed8;
    }
</style>
</head>

<body>

<div id="gameWrapper">

    <canvas id="gameCanvas" width="600" height="500"></canvas>

    <div id="info">
        점수: <span id="score">0</span>
        &nbsp;&nbsp;
        목숨: <span id="lives">3</span>
    </div>

    <button onclick="restartGame()">다시 시작</button>

</div>

<script>

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

const scoreText = document.getElementById("score");
const livesText = document.getElementById("lives");

let score = 0;
let lives = 3;
let gameRunning = true;

const ball = {
    x: canvas.width / 2,
    y: canvas.height - 60,
    dx: 4,
    dy: -4,
    radius: 8
};

const paddle = {
    width: 100,
    height: 12,
    x: canvas.width / 2 - 50,
    speed: 7
};

let rightPressed = false;
let leftPressed = false;

const brickRows = 5;
const brickCols = 8;
const brickWidth = 60;
const brickHeight = 20;
const brickPadding = 10;
const brickOffsetTop = 50;
const brickOffsetLeft = 35;

let bricks = [];

function createBricks() {
    bricks = [];

    for (let r = 0; r < brickRows; r++) {
        bricks[r] = [];

        for (let c = 0; c < brickCols; c++) {
            bricks[r][c] = {
                x: c * (brickWidth + brickPadding) + brickOffsetLeft,
                y: r * (brickHeight + brickPadding) + brickOffsetTop,
                alive: true
            };
        }
    }
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
    ctx.fillStyle = "#facc15";
    ctx.fill();
    ctx.closePath();
}

function drawPaddle() {
    ctx.fillStyle = "#60a5fa";

    ctx.beginPath();
    ctx.roundRect(
        paddle.x,
        canvas.height - 30,
        paddle.width,
        paddle.height,
        6
    );
    ctx.fill();
}

function drawBricks() {

    for (let r = 0; r < brickRows; r++) {

        for (let c = 0; c < brickCols; c++) {

            const brick = bricks[r][c];

            if (brick.alive) {

                ctx.fillStyle = [
                    "#ef4444",
                    "#f97316",
                    "#eab308",
                    "#22c55e",
                    "#3b82f6"
                ][r];

                ctx.beginPath();

                ctx.roundRect(
                    brick.x,
                    brick.y,
                    brickWidth,
                    brickHeight,
                    4
                );

                ctx.fill();
            }
        }
    }
}

function collisionDetection() {

    for (let r = 0; r < brickRows; r++) {

        for (let c = 0; c < brickCols; c++) {

            const brick = bricks[r][c];

            if (!brick.alive) continue;

            if (
                ball.x > brick.x &&
                ball.x < brick.x + brickWidth &&
                ball.y > brick.y &&
                ball.y < brick.y + brickHeight
            ) {

                ball.dy = -ball.dy;
                brick.alive = false;

                score++;
                scoreText.textContent = score;

                if (score === brickRows * brickCols) {
                    gameRunning = false;

                    setTimeout(() => {
                        alert("🎉 모든 벽돌을 깼습니다!");
                    }, 100);
                }
            }
        }
    }
}

function draw() {

    if (!gameRunning) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawBricks();
    drawBall();
    drawPaddle();

    collisionDetection();

    // 벽 충돌
    if (
        ball.x + ball.dx > canvas.width - ball.radius ||
        ball.x + ball.dx < ball.radius
    ) {
        ball.dx = -ball.dx;
    }

    if (ball.y + ball.dy < ball.radius) {
        ball.dy = -ball.dy;
    }

    // 패들 충돌
    if (
        ball.y + ball.radius >= canvas.height - 30 &&
        ball.x >= paddle.x &&
        ball.x <= paddle.x + paddle.width &&
        ball.dy > 0
    ) {

        ball.dy = -Math.abs(ball.dy);

        // 패들 위치에 따라 공의 방향 변경
        let hitPosition =
            (ball.x - paddle.x) / paddle.width;

        ball.dx = (hitPosition - 0.5) * 10;
    }

    // 공이 아래로 떨어짐
    if (ball.y + ball.dy > canvas.height - ball.radius) {

        lives--;
        livesText.textContent = lives;

        if (lives <= 0) {

            gameRunning = false;

            setTimeout(() => {
                alert("게임 오버! 😢");
            }, 100);

        } else {

            ball.x = canvas.width / 2;
            ball.y = canvas.height - 60;

            ball.dx = 4;
            ball.dy = -4;

            paddle.x = canvas.width / 2 - paddle.width / 2;
        }

    } else {

        ball.x += ball.dx;
        ball.y += ball.dy;
    }

    // 키보드 이동
    if (rightPressed) {
        paddle.x += paddle.speed;
    }

    if (leftPressed) {
        paddle.x -= paddle.speed;
    }

    // 패들이 화면 밖으로 나가지 않도록
    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > canvas.width) {
        paddle.x = canvas.width - paddle.width;
    }

    requestAnimationFrame(draw);
}

// 키보드
document.addEventListener("keydown", function(e) {

    if (e.key === "Right" || e.key === "ArrowRight") {
        rightPressed = true;
    }

    if (e.key === "Left" || e.key === "ArrowLeft") {
        leftPressed = true;
    }
});

document.addEventListener("keyup", function(e) {

    if (e.key === "Right" || e.key === "ArrowRight") {
        rightPressed = false;
    }

    if (e.key === "Left" || e.key === "ArrowLeft") {
        leftPressed = false;
    }
});

// 마우스
canvas.addEventListener("mousemove", function(e) {

    const rect = canvas.getBoundingClientRect();

    const mouseX =
        e.clientX - rect.left;

    paddle.x =
        mouseX - paddle.width / 2;

    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > canvas.width) {
        paddle.x = canvas.width - paddle.width;
    }
});

// 터치
canvas.addEventListener("touchmove", function(e) {

    e.preventDefault();

    const rect = canvas.getBoundingClientRect();

    const touchX =
        e.touches[0].clientX - rect.left;

    paddle.x =
        touchX - paddle.width / 2;

    if (paddle.x < 0) {
        paddle.x = 0;
    }

    if (paddle.x + paddle.width > canvas.width) {
        paddle.x = canvas.width - paddle.width;
    }

}, { passive: false });


function restartGame() {

    score = 0;
    lives = 3;
    gameRunning = true;

    scoreText.textContent = score;
    livesText.textContent = lives;

    ball.x = canvas.width / 2;
    ball.y = canvas.height - 60;

    ball.dx = 4;
    ball.dy = -4;

    paddle.x =
        canvas.width / 2 - paddle.width / 2;

    createBricks();

    draw();
}

createBricks();
draw();

</script>

</body>
</html>
"""

components.html(game, height=600, scrolling=False)
