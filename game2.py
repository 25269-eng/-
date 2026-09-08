import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="장애물 피하기",
    page_icon="🏃",
    layout="centered"
)

st.markdown(
    """
    <h1 style="text-align:center;">🏃 장애물 피하기</h1>
    <p style="text-align:center;">PC: ← → &nbsp;&nbsp;|&nbsp;&nbsp; 모바일: 버튼을 눌러 이동</p>
    """,
    unsafe_allow_html=True
)

html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
* {
    box-sizing: border-box;
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
}

body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: Arial, sans-serif;
}

#game {
    width: min(400px, 95vw);
    height: min(600px, 75vh);
    min-height: 500px;
    margin: auto;
    position: relative;
    overflow: hidden;

    background:
        linear-gradient(
            to bottom,
            #87CEEB 0%,
            #dff6ff 65%,
            #69b34c 65%,
            #69b34c 100%
        );

    border: 5px solid #222;
    border-radius: 18px;
}

#road {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 13%;
    right: 13%;
    background: #555;
}

.roadLine {
    position: absolute;
    width: 5px;
    height: 55px;
    background: white;
    opacity: 0.65;
}

#score {
    position: absolute;
    top: 10px;
    left: 12px;
    color: white;
    font-size: 19px;
    font-weight: bold;
    z-index: 10;
    text-shadow: 2px 2px 3px black;
}

#player {
    position: absolute;
    width: 45px;
    height: 50px;
    font-size: 40px;
    z-index: 5;
    text-align: center;
}

.object {
    position: absolute;
    width: 45px;
    height: 45px;
    font-size: 36px;
    text-align: center;
    z-index: 4;
}

.coin {
    position: absolute;
    width: 40px;
    height: 40px;
    font-size: 30px;
    text-align: center;
    z-index: 3;
}

.screen {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.78);
    color: white;
    z-index: 20;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    text-align: center;
}

#gameOver {
    display: none;
}

.screen h1 {
    font-size: 42px;
    margin: 8px;
}

.screen h2 {
    margin: 5px;
}

.screen p {
    font-size: 16px;
}

.startButton {
    border: none;
    border-radius: 12px;
    padding: 13px 28px;
    font-size: 20px;
    font-weight: bold;
    background: #ffd21f;
}

#controls {
    width: min(400px, 95vw);
    margin: 12px auto 0;
    display: flex;
    justify-content: space-between;
    gap: 15px;
}

.control {
    flex: 1;
    height: 70px;

    border: none;
    border-radius: 18px;

    font-size: 35px;
    font-weight: bold;

    background: #eeeeee;
    box-shadow: 0 4px 0 #aaa;

    touch-action: none;
}

.control:active {
    transform: translateY(3px);
    box-shadow: 0 1px 0 #aaa;
}

.tip {
    text-align: center;
    margin-top: 8px;
    color: #555;
    font-size: 13px;
}
</style>
</head>

<body>

<div id="game">

    <div id="road"></div>

    <div id="score">
        점수: 0 🪙 0
    </div>

    <div id="player">
        🏃
    </div>

    <div id="startScreen" class="screen">
        <h1>🏃</h1>
        <h2>장애물 피하기</h2>
        <p>장애물을 피하고 코인을 모으세요!</p>
        <button class="startButton" onclick="startGame()">
            게임 시작
        </button>
    </div>

    <div id="gameOver" class="screen">
        <h1>💥</h1>
        <h2>GAME OVER</h2>
        <p id="finalScore"></p>

        <button class="startButton" onclick="startGame()">
            다시 하기
        </button>
    </div>

</div>

<div id="controls">

    <button
        class="control"
        id="leftButton"
    >
        ◀️
    </button>

    <button
        class="control"
        id="rightButton"
    >
        ▶️
    </button>

</div>

<div class="tip">
    💡 버튼을 누르고 있으면 계속 이동합니다.
</div>


<script>

const game = document.getElementById("game");
const player = document.getElementById("player");

const scoreText = document.getElementById("score");

const startScreen =
    document.getElementById("startScreen");

const gameOver =
    document.getElementById("gameOver");

const finalScore =
    document.getElementById("finalScore");

const leftButton =
    document.getElementById("leftButton");

const rightButton =
    document.getElementById("rightButton");


let playerX = 0;

let obstacles = [];
let coins = [];

let score = 0;
let coinScore = 0;

let speed = 3.5;

let running = false;

let moveLeft = false;
let moveRight = false;

let obstacleTimer;
let coinTimer;
let scoreTimer;
let animation;


/* -----------------------------
   게임 크기 계산
----------------------------- */

function setPlayerPosition() {

    const roadLeft =
        game.clientWidth * 0.13;

    const roadRight =
        game.clientWidth * 0.87;

    const maxX =
        roadRight - 45;

    if (playerX < roadLeft) {
        playerX = roadLeft;
    }

    if (playerX > maxX) {
        playerX = maxX;
    }

    player.style.left = playerX + "px";

    player.style.bottom =
        Math.max(20, game.clientHeight * 0.04) + "px";
}


/* -----------------------------
   조작
----------------------------- */

document.addEventListener("keydown", function(e) {

    if (!running) return;

    if (e.key === "ArrowLeft") {
        moveLeft = true;
        e.preventDefault();
    }

    if (e.key === "ArrowRight") {
        moveRight = true;
        e.preventDefault();
    }
});


document.addEventListener("keyup", function(e) {

    if (e.key === "ArrowLeft") {
        moveLeft = false;
    }

    if (e.key === "ArrowRight") {
        moveRight = false;
    }
});


function buttonDown(direction) {

    if (!running) return;

    if (direction === "left") {
        moveLeft = true;
    }

    if (direction === "right") {
        moveRight = true;
    }
}


function buttonUp(direction) {

    if (direction === "left") {
        moveLeft = false;
    }

    if (direction === "right") {
        moveRight = false;
    }
}


/* 모바일 터치 */

leftButton.addEventListener(
    "touchstart",
    function(e) {
        e.preventDefault();
        buttonDown("left");
    },
    {passive:false}
);

leftButton.addEventListener(
    "touchend",
    function(e) {
        e.preventDefault();
        buttonUp("left");
    },
    {passive:false}
);


rightButton.addEventListener(
    "touchstart",
    function(e) {
        e.preventDefault();
        buttonDown("right");
    },
    {passive:false}
);

rightButton.addEventListener(
    "touchend",
    function(e) {
        e.preventDefault();
        buttonUp("right");
    },
    {passive:false}
);


/* PC 마우스도 지원 */

leftButton.addEventListener(
    "mousedown",
    () => buttonDown("left")
);

leftButton.addEventListener(
    "mouseup",
    () => buttonUp("left")
);

rightButton.addEventListener(
    "mousedown",
    () => buttonDown("right")
);

rightButton.addEventListener(
    "mouseup",
    () => buttonUp("right")
);


/* -----------------------------
   게임 시작
----------------------------- */

function startGame() {

    obstacles.forEach(
        o => o.element.remove()
    );

    coins.forEach(
        c => c.element.remove()
    );

    obstacles = [];
    coins = [];

    score = 0;
    coinScore = 0;

    speed = 3.5;

    moveLeft = false;
    moveRight = false;

    playerX =
        game.clientWidth / 2 - 22;

    setPlayerPosition();

    scoreText.innerText =
        "점수: 0 🪙 0";

    startScreen.style.display =
        "none";

    gameOver.style.display =
        "none";

    running = true;

    clearInterval(obstacleTimer);
    clearInterval(coinTimer);
    clearInterval(scoreTimer);

    cancelAnimationFrame(animation);


    obstacleTimer =
        setInterval(
            createObstacle,
            850
        );


    coinTimer =
        setInterval(
            createCoin,
            1100
        );


    scoreTimer =
        setInterval(function() {

            score++;

            if (score % 100 === 0) {
                speed += 0.5;
            }

            scoreText.innerText =
                "점수: " +
                score +
                " 🪙 " +
                coinScore;

        }, 100);


    animation =
        requestAnimationFrame(update);
}


/* -----------------------------
   장애물
----------------------------- */

function createObstacle() {

    if (!running) return;

    const obstacle =
        document.createElement("div");

    obstacle.className = "object";

    const types = [
        "🚗",
        "🪨",
        "🚧",
        "💣",
        "🛢️"
    ];

    obstacle.innerText =
        types[
            Math.floor(
                Math.random() * types.length
            )
        ];


    const roadLeft =
        game.clientWidth * 0.13;

    const roadRight =
        game.clientWidth * 0.87;


    const maxX =
        roadRight - 45;


    const x =
        roadLeft +
        Math.random() *
        (maxX - roadLeft);


    obstacle.style.left =
        x + "px";

    obstacle.style.top =
        "-50px";


    game.appendChild(obstacle);


    obstacles.push({
        element: obstacle,
        x: x,
        y: -50
    });
}


/* -----------------------------
   코인
----------------------------- */

function createCoin() {

    if (!running) return;

    const coin =
        document.createElement("div");

    coin.className = "coin";

    coin.innerText = "🪙";


    const roadLeft =
        game.clientWidth * 0.13;

    const roadRight =
        game.clientWidth * 0.87;


    const maxX =
        roadRight - 40;


    const x =
        roadLeft +
        Math.random() *
        (maxX - roadLeft);


    coin.style.left =
        x + "px";

    coin.style.top =
        "-40px";


    game.appendChild(coin);


    coins.push({
        element: coin,
        x: x,
        y: -40
    });
}


/* -----------------------------
   충돌
----------------------------- */

function collision(a, b) {

    return (
        a.x < b.x + 40 &&
        a.x + 40 > b.x &&
        a.y < b.y + 40 &&
        a.y + 40 > b.y
    );
}


/* -----------------------------
   게임 진행
----------------------------- */

function update() {

    if (!running) return;


    /* 플레이어 이동 */

    if (moveLeft) {
        playerX -= 6;
    }

    if (moveRight) {
        playerX += 6;
    }

    setPlayerPosition();


    const playerY =
        game.clientHeight - 85;


    /* 장애물 */

    for (
        let i = obstacles.length - 1;
        i >= 0;
        i--
    ) {

        const o = obstacles[i];

        o.y += speed;

        o.element.style.top =
            o.y + "px";


        if (
            collision(
                {
                    x: playerX,
                    y: playerY
                },
                {
                    x: o.x,
                    y: o.y
                }
            )
        ) {

            endGame();
            return;
        }


        if (
            o.y >
            game.clientHeight + 50
        ) {

            o.element.remove();

            obstacles.splice(i, 1);
        }
    }


    /* 코인 */

    for (
        let i = coins.length - 1;
        i >= 0;
        i--
    ) {

        const c = coins[i];

        c.y += speed;

        c.element.style.top =
            c.y + "px";


        if (
            collision(
                {
                    x: playerX,
                    y: playerY
                },
                {
                    x: c.x,
                    y: c.y
                }
            )
        ) {

            coinScore += 10;

            c.element.remove();

            coins.splice(i, 1);

            scoreText.innerText =
                "점수: " +
                score +
                " 🪙 " +
                coinScore;

            continue;
        }


        if (
            c.y >
            game.clientHeight + 50
        ) {

            c.element.remove();

            coins.splice(i, 1);
        }
    }


    animation =
        requestAnimationFrame(update);
}


/* -----------------------------
   게임 종료
----------------------------- */

function endGame() {

    running = false;

    moveLeft = false;
    moveRight = false;

    clearInterval(obstacleTimer);
    clearInterval(coinTimer);
    clearInterval(scoreTimer);

    cancelAnimationFrame(animation);

    finalScore.innerText =
        "점수: " +
        score +
        "  |  코인: " +
        coinScore;

    gameOver.style.display =
        "flex";
}


/* 화면 크기 변경 */

window.addEventListener(
    "resize",
    function() {
        setPlayerPosition();
    }
);

setTimeout(
    setPlayerPosition,
    100
);

</script>

</body>
</html>
"""

components.html(
    html,
    height=760,
    scrolling=False
)
