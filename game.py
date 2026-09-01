import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="💣 폭탄 벽돌 깨기",
    page_icon="💣",
    layout="centered"
)

st.title("💣 폭탄 벽돌 깨기")
st.caption("← → 방향키 / 마우스 / 터치로 패들을 움직이세요!")

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
    touch-action: none;
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

const brickRows = 6;
const brickCols = 8;

const brickWidth = 60;
const brickHeight = 20;
const brickPadding = 10;

const brickOffsetTop = 50;
const brickOffsetLeft = 35;

let bricks = [];

// 폭탄이 들어갈 위치
const bombPositions = [
    [1, 2],
    [2, 5],
    [4, 1],
    [4, 6]
];

function isBombPosition(row, col) {

    return bombPositions.some(
        position =>
            position[0] === row &&
            position[1] === col
    );
}

function createBricks() {

    bricks = [];

    for (let r = 0; r < brickRows; r++) {

        bricks[r] = [];

        for (let c = 0; c < brickCols; c++) {

            bricks[r][c] = {

                x: c * (brickWidth + brickPadding) + brickOffsetLeft,

                y: r * (brickHeight + brickPadding) + brickOffsetTop,

                alive: true,

                bomb: isBombPosition(r, c)
            };
        }
    }
}

function drawBall() {

    ctx.beginPath();

    ctx.arc(
        ball.x,
        ball.y,
        ball.radius,
        0,
        Math.PI * 2
    );

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

            if (!brick.alive) continue;

            // 폭탄 벽돌
            if (brick.bomb) {

                ctx.fillStyle = "#dc2626";

                ctx.beginPath();

                ctx.roundRect(
                    brick.x,
                    brick.y,
                    brickWidth,
                    brickHeight,
                    4
                );

                ctx.fill();

                // 폭탄 표시
                ctx.font = "16px Arial";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";

                ctx.fillStyle = "white";

                ctx.fillText(
                    "💣",
                    brick.x + brickWidth / 2,
                    brick.y + brickHeight / 2
                );

            } else {

                const rowColors = [
                    "#ef4444",
                    "#f97316",
                    "#eab308",
                    "#22c55e",
                    "#3b82f6",
                    "#8b5cf6"
                ];

                ctx.fillStyle = rowColors[r];

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


// 일반 벽돌 파괴
function destroyBrick(row, col) {

    const brick = bricks[row][col];

    if (!brick.alive) return;

    brick.alive = false;
    score++;

    // 폭탄이면 주변 벽돌도 폭발
    if (brick.bomb) {

        explode(row, col);
    }

    scoreText.textContent = score;
}


// 폭탄 폭발
function explode(row, col) {

    for (let r = row - 1; r <= row + 1; r++) {

        for (let c = col - 1; c <= col + 1; c++) {

            // 자기 자신은 이미 파괴됨
            if (r === row && c === col) continue;

            // 게임판 안에 있는지 확인
            if (
                r >= 0 &&
                r < brickRows &&
                c >= 0 &&
                c < brickCols
            ) {

                const nearbyBrick = bricks[r][c];

                if (nearbyBrick.alive) {

                    nearbyBrick.alive = false;

                    score++;
                }
            }
        }
    }

    scoreText.textContent = score;

    // 폭발 효과
    drawExplosion(
        bricks[row][col].x + brickWidth / 2,
        bricks[row][col].y + brickHeight / 2
    );
}


// 폭발 효과
function drawExplosion(x, y) {

    ctx.save();

    ctx.font = "40px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    ctx.fillText("💥", x, y);

    ctx.restore();

    setTimeout(() => {

        if (gameRunning) {
            ctx.clearRect(
                x - 30,
                y - 30,
                60,
                60
            );
        }

    }, 150);
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

                destroyBrick(r, c);

                return;
            }
        }
    }
}


function checkWin() {

    let remaining = 0;

    for (let r = 0; r < brickRows; r++) {

        for (let c = 0; c < brickCols; c++) {

            if (bricks[r][c].alive) {
                remaining++;
            }
        }
    }

    if (remaining === 0) {

        gameRunning = false;

        setTimeout(() => {

            alert("🎉 모든 벽돌을 깼습니다!");

        }, 100);
    }
}


function draw() {

    if (!gameRunning) return;

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    drawBricks();
    drawBall();
    drawPaddle();

    collisionDetection();

    checkWin();

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

        const hitPosition =
            (ball.x - paddle.x) / paddle.width;

        ball.dx =
            (hitPosition - 0.5) * 10;
    }


    // 공이 아래로 떨어짐
    if (
        ball.y + ball.dy >
        canvas.height - ball.radius
    ) {

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

            paddle.x =
                canvas.width / 2 -
                paddle.width / 2;
        }

    } else {

        ball.x += ball.dx;
        ball.y += ball.dy;
    }


    // 패들 이동
    if (rightPressed) {

        paddle.x += paddle.speed;
    }

    if (leftPressed) {

        paddle.x -= paddle.speed;
    }


    // 화면 밖으로 나가지 않게
    if (paddle.x < 0) {

        paddle.x = 0;
    }

    if (
        paddle.x + paddle.width >
        canvas.width
    ) {

        paddle.x =
            canvas.width - paddle.width;
    }


    requestAnimationFrame(draw);
}


// 키보드
document.addEventListener("keydown", function(e) {

    if (
        e.key === "Right" ||
        e.key === "ArrowRight"
    ) {

        rightPressed = true;
    }

    if (
        e.key === "Left" ||
        e.key === "ArrowLeft"
    ) {

        leftPressed = true;
    }
});


document.addEventListener("keyup", function(e) {

    if (
        e.key === "Right" ||
        e.key === "ArrowRight"
    ) {

        rightPressed = false;
    }

    if (
        e.key === "Left" ||
        e.key === "ArrowLeft"
    ) {

        leftPressed = false;
    }
});


// 마우스
canvas.addEventListener(
    "mousemove",
    function(e) {

        const rect =
            canvas.getBoundingClientRect();

        const mouseX =
            e.clientX - rect.left;

        paddle.x =
            mouseX - paddle.width / 2;

        if (paddle.x < 0) {

            paddle.x = 0;
        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {

            paddle.x =
                canvas.width - paddle.width;
        }
    }
);


// 터치
canvas.addEventListener(
    "touchmove",
    function(e) {

        e.preventDefault();

        const rect =
            canvas.getBoundingClientRect();

        const touchX =
            e.touches[0].clientX - rect.left;

        paddle.x =
            touchX - paddle.width / 2;

        if (paddle.x < 0) {

            paddle.x = 0;
        }

        if (
            paddle.x + paddle.width >
            canvas.width
        ) {

            paddle.x =
                canvas.width - paddle.width;
        }

    },
    { passive: false }
);


// 다시 시작
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
        canvas.width / 2 -
        paddle.width / 2;

    createBricks();

    draw();
}


createBricks();
draw();

</script>

</body>
</html>
"""

components.html(
    game,
    height=600,
    scrolling=False
)
