import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

st.set_page_config(
    page_title="가나디 장애물 피하기",
    page_icon="🐑",
    layout="centered"
)

# 가나디 이미지 불러오기
IMAGE_PATH = Path(
    "assets/2AF52792-26A2-4DA1-BF46-15EA171CFFBA.PNG"
)

if not IMAGE_PATH.exists():
    st.error("❌ 가나디 이미지 파일을 찾을 수 없습니다.")
    st.stop()

with open(IMAGE_PATH, "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

image_url = f"data:image/png;base64,{image_data}"

st.markdown(
    """
    <h1 style="text-align:center;">
        🐑 가나디 장애물 피하기
    </h1>
    <p style="text-align:center;">
        장애물을 피하면서 최대한 오래 살아남으세요!
    </p>
    """,
    unsafe_allow_html=True
)

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta name="viewport"
      content="width=device-width,
               initial-scale=1.0,
               maximum-scale=1.0,
               user-scalable=no">

<style>

* {{
    box-sizing: border-box;
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
}}

body {{
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background: transparent;
}}

#game {{
    position: relative;
    width: min(400px, 94vw);
    height: 600px;
    margin: auto;

    overflow: hidden;

    border: 5px solid #222;
    border-radius: 18px;

    background:
        linear-gradient(
            #8ed6ff 0%,
            #dff7ff 65%,
            #75c94c 65%,
            #75c94c 100%
        );
}}

/* 도로 */

#road {{
    position: absolute;
    top: 0;
    bottom: 0;

    left: 12%;
    right: 12%;

    background: #555;
}}

/* 도로 중앙선 */

.line {{
    position: absolute;

    width: 5px;
    height: 50px;

    background: white;
    opacity: 0.6;
}}

/* 점수 */

#score {{
    position: absolute;

    top: 10px;
    left: 12px;

    color: white;
    font-size: 19px;
    font-weight: bold;

    z-index: 10;

    text-shadow:
        2px 2px 3px black;
}}

/* 가나디 */

#player {{
    position: absolute;

    width: 58px;
    height: 65px;

    z-index: 5;

    object-fit: contain;

    pointer-events: none;
}}

/* 장애물 */

.obstacle {{
    position: absolute;

    width: 48px;
    height: 48px;

    font-size: 38px;

    display: flex;
    align-items: center;
    justify-content: center;

    z-index: 4;
}}

/* 코인 */

.coin {{
    position: absolute;

    width: 42px;
    height: 42px;

    font-size: 30px;

    display: flex;
    align-items: center;
    justify-content: center;

    z-index: 3;
}}

/* 시작/종료 화면 */

.screen {{
    position: absolute;

    inset: 0;

    background: rgba(0,0,0,0.78);

    color: white;

    z-index: 20;

    display: flex;
    flex-direction: column;

    align-items: center;
    justify-content: center;

    text-align: center;
}}

#gameOver {{
    display: none;
}}

.screen h1 {{
    font-size: 48px;
    margin: 5px;
}}

.screen h2 {{
    margin: 5px;
}}

.screen p {{
    font-size: 16px;
}}

.startButton {{
    border: none;

    padding: 13px 28px;

    border-radius: 12px;

    background: #ffd21f;

    font-size: 20px;
    font-weight: bold;
}}

/* 모바일 조작 */

#controls {{
    width: min(400px, 94vw);

    margin: 12px auto 0;

    display: flex;

    gap: 15px;
}}

.control {{
    flex: 1;

    height: 70px;

    border: none;
    border-radius: 18px;

    background: #eeeeee;

    font-size: 35px;

    box-shadow:
        0 4px 0 #aaa;

    touch-action: none;
}}

.control:active {{
    transform: translateY(3px);

    box-shadow:
        0 1px 0 #aaa;
}}

.tip {{
    text-align: center;

    margin-top: 8px;

    font-size: 13px;
    color: #666;
}}

</style>
</head>

<body>

<div id="game">

    <div id="road"></div>

    <div id="score">
        점수: 0 🪙 0
    </div>

    <img
        id="player"
        src="{image_url}"
    >

    <!-- 시작 화면 -->

    <div
        id="startScreen"
        class="screen"
    >

        <h1>🐑</h1>

        <h2>
            가나디 장애물 피하기
        </h2>

        <p>
            장애물을 피하고<br>
            🪙 코인을 모으세요!
        </p>

        <button
            class="startButton"
            onclick="startGame()"
        >
            게임 시작
        </button>

    </div>


    <!-- 게임 오버 -->

    <div
        id="gameOver"
        class="screen"
    >

        <h1>💥</h1>

        <h2>
            GAME OVER
        </h2>

        <p id="finalScore">
        </p>

        <button
            class="startButton"
            onclick="startGame()"
        >
            다시 하기
        </button>

    </div>

</div>


<!-- 모바일 버튼 -->

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
    📱 버튼을 누르고 있으면 가나디가 계속 이동합니다.
</div>


<script>

/* =========================
   기본 설정
========================= */

const game =
    document.getElementById("game");

const player =
    document.getElementById("player");

const scoreText =
    document.getElementById("score");

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

let speed = 4;

let running = false;

let moveLeft = false;
let moveRight = false;

let obstacleTimer;
let coinTimer;
let scoreTimer;
let animation;


/* =========================
   가나디 위치
========================= */

function setPlayerPosition() {{

    const roadLeft =
        game.clientWidth * 0.12;

    const roadRight =
        game.clientWidth * 0.88;

    const maxX =
        roadRight - 58;


    if (playerX < roadLeft) {{
        playerX = roadLeft;
    }}

    if (playerX > maxX) {{
        playerX = maxX;
    }}


    player.style.left =
        playerX + "px";

    player.style.bottom =
        "25px";
}}


/* =========================
   PC 키보드
========================= */

document.addEventListener(
    "keydown",
    function(e) {{

        if (!running) return;


        if (e.key === "ArrowLeft") {{

            moveLeft = true;

            e.preventDefault();
        }}


        if (e.key === "ArrowRight") {{

            moveRight = true;

            e.preventDefault();
        }}

    }}
);


document.addEventListener(
    "keyup",
    function(e) {{

        if (e.key === "ArrowLeft") {{
            moveLeft = false;
        }}

        if (e.key === "ArrowRight") {{
            moveRight = false;
        }}

    }}
);


/* =========================
   모바일 버튼
========================= */

function startMove(direction) {{

    if (!running) return;

    if (direction === "left") {{
        moveLeft = true;
    }}

    if (direction === "right") {{
        moveRight = true;
    }}
}}


function stopMove(direction) {{

    if (direction === "left") {{
        moveLeft = false;
    }}

    if (direction === "right") {{
        moveRight = false;
    }}
}}


/* 왼쪽 */

leftButton.addEventListener(
    "touchstart",
    function(e) {{

        e.preventDefault();

        startMove("left");

    }},
    {{passive:false}}
);


leftButton.addEventListener(
    "touchend",
    function(e) {{

        e.preventDefault();

        stopMove("left");

    }},
    {{passive:false}}
);


/* 오른쪽 */

rightButton.addEventListener(
    "touchstart",
    function(e) {{

        e.preventDefault();

        startMove("right");

    }},
    {{passive:false}}
);


rightButton.addEventListener(
    "touchend",
    function(e) {{

        e.preventDefault();

        stopMove("right");

    }},
    {{passive:false}}
);


/* =========================
   게임 시작
========================= */

function startGame() {{

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

    speed = 4;


    moveLeft = false;
    moveRight = false;


    playerX =
        game.clientWidth / 2 - 29;

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


    /* 장애물 생성 */

    obstacleTimer =
        setInterval(
            createObstacle,
            800
        );


    /* 코인 생성 */

    coinTimer =
        setInterval(
            createCoin,
            1200
        );


    /* 점수 */

    scoreTimer =
        setInterval(
            function() {{

                score++;


                /* 100점마다 속도 증가 */

                if (score % 100 === 0) {{
                    speed += 0.5;
                }}


                scoreText.innerText =
                    "점수: " +
                    score +
                    " 🪙 " +
                    coinScore;

            }},
            100
        );


    animation =
        requestAnimationFrame(update);
}}


/* =========================
   장애물 생성
========================= */

function createObstacle() {{

    if (!running) return;


    const obstacle =
        document.createElement("div");

    obstacle.className =
        "obstacle";


    const types = [
        "🚗",
        "🚧",
        "🪨",
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
        game.clientWidth * 0.12;

    const roadRight =
        game.clientWidth * 0.88;


    const x =
        roadLeft +
        Math.random() *
        (roadRight - roadLeft - 48);


    obstacle.style.left =
        x + "px";

    obstacle.style.top =
        "-55px";


    game.appendChild(obstacle);


    obstacles.push({{

        element: obstacle,

        x: x,

        y: -55

    }});
}}


/* =========================
   코인 생성
========================= */

function createCoin() {{

    if (!running) return;


    const coin =
        document.createElement("div");

    coin.className =
        "coin";

    coin.innerText =
        "🪙";


    const roadLeft =
        game.clientWidth * 0.12;

    const roadRight =
        game.clientWidth * 0.88;


    const x =
        roadLeft +
        Math.random() *
        (roadRight - roadLeft - 42);


    coin.style.left =
        x + "px";

    coin.style.top =
        "-45px";


    game.appendChild(coin);


    coins.push({{

        element: coin,

        x: x,

        y: -45

    }});
}}


/* =========================
   충돌 판정
========================= */

function collision(a, b) {{

    return (

        a.x < b.x + 40 &&

        a.x + 45 > b.x &&

        a.y < b.y + 40 &&

        a.y + 55 > b.y

    );
}}


/* =========================
   게임 진행
========================= */

function update() {{

    if (!running) return;


    /* 가나디 이동 */

    if (moveLeft) {{
        playerX -= 7;
    }}

    if (moveRight) {{
        playerX += 7;
    }}


    setPlayerPosition();


    const playerY =
        game.clientHeight - 90;


    /* =====================
       장애물 이동
    ===================== */

    for (
        let i = obstacles.length - 1;
        i >= 0;
        i--
    ) {{

        const o =
            obstacles[i];


        o.y += speed;


        o.element.style.top =
            o.y + "px";


        /* 충돌 */

        if (
            collision(

                {{
                    x: playerX,
                    y: playerY
                }},

                {{
                    x: o.x,
                    y: o.y
                }}

            )
        ) {{

            endGame();

            return;
        }}


        /* 화면 밖 */

        if (
            o.y >
            game.clientHeight + 60
        ) {{

            o.element.remove();

            obstacles.splice(i, 1);
        }}
    }}


    /* =====================
       코인 이동
    ===================== */

    for (
        let i = coins.length - 1;
        i >= 0;
        i--
    ) {{

        const c =
            coins[i];


        c.y += speed;


        c.element.style.top =
            c.y + "px";


        /* 코인 획득 */

        if (
            collision(

                {{
                    x: playerX,
                    y: playerY
                }},

                {{
                    x: c.x,
                    y: c.y
                }}

            )
        ) {{

            coinScore += 10;


            c.element.remove();

            coins.splice(i, 1);


            scoreText.innerText =
                "점수: " +
                score +
                " 🪙 " +
                coinScore;


            continue;
        }}


        if (
            c.y >
            game.clientHeight + 50
        ) {{

            c.element.remove();

            coins.splice(i, 1);
        }}
    }}


    animation =
        requestAnimationFrame(update);
}}


/* =========================
   게임 종료
========================= */

function endGame() {{

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
        "점  |  코인: " +
        coinScore;


    gameOver.style.display =
        "flex";
}}


/* 화면 크기 변경 */

window.addEventListener(
    "resize",
    function() {{
        setPlayerPosition();
    }}
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
