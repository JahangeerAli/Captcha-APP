import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
import random
import string
import io
import base64
import re
import os


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Can AI Beat You?",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

GROQ_MODEL = "qwen/qwen3.6-27b"


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "human_score": 0,
    "ai_score": 0,
    "round_count": 0,

    "captcha_text": None,
    "captcha_image": None,
    "captcha_human_done": False,
    "captcha_ai_done": False,

    "animal_grid": None,
    "animal_target": None,
    "animal_correct": [],
    "animal_human_done": False,
    "animal_ai_done": False,

    "api_tested": False,
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* ================================
       GENERAL
       ================================ */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(99, 102, 241, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at top right,
                rgba(168, 85, 247, 0.10),
                transparent 30%
            ),
            #f8fafc;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ================================
       SIDEBAR
       ================================ */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #111827 0%,
                #1e1b4b 100%
            );
    }

    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] input {
        background: #ffffff !important;
        color: #111827 !important;
        border-radius: 10px !important;
    }


    /* ================================
       HERO
       ================================ */

    .hero {
        position: relative;
        overflow: hidden;

        padding: 42px 45px;

        border-radius: 28px;

        background:
            linear-gradient(
                135deg,
                #4f46e5 0%,
                #7c3aed 55%,
                #9333ea 100%
            );

        box-shadow:
            0 20px 50px rgba(79, 70, 229, 0.25);

        color: white;

        margin-bottom: 28px;
    }

    .hero::after {
        content: "";
        position: absolute;

        width: 260px;
        height: 260px;

        right: -90px;
        top: -90px;

        border-radius: 50%;

        background: rgba(255,255,255,0.10);
    }

    .hero-badge {
        display: inline-block;

        padding: 7px 14px;

        border-radius: 50px;

        background: rgba(255,255,255,0.16);

        font-size: 13px;
        font-weight: 700;

        margin-bottom: 15px;

        letter-spacing: 0.4px;
    }

    .hero-title {
        font-size: 46px;
        font-weight: 850;

        line-height: 1.1;

        margin-bottom: 12px;

        position: relative;
        z-index: 2;
    }

    .hero-subtitle {
        font-size: 18px;

        line-height: 1.65;

        max-width: 760px;

        color: rgba(255,255,255,0.90);

        position: relative;
        z-index: 2;
    }


    /* ================================
       INFORMATION CARDS
       ================================ */

    .info-card {
        background: rgba(255,255,255,0.92);

        border: 1px solid #e5e7eb;

        border-radius: 18px;

        padding: 20px;

        box-shadow:
            0 8px 25px rgba(15,23,42,0.06);

        min-height: 105px;
    }

    .info-label {
        color: #64748b;

        font-size: 12px;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 1px;

        margin-bottom: 7px;
    }

    .info-value {
        color: #111827;

        font-size: 19px;

        font-weight: 750;
    }


    /* ================================
       SCORE CARDS
       ================================ */

    .score-card {
        background: white;

        border-radius: 20px;

        padding: 22px;

        border: 1px solid #e5e7eb;

        box-shadow:
            0 8px 25px rgba(15,23,42,0.07);

        text-align: center;

        transition: transform 0.2s ease;
    }

    .score-card:hover {
        transform: translateY(-3px);
    }

    .score-icon {
        font-size: 27px;

        margin-bottom: 5px;
    }

    .score-label {
        color: #64748b;

        font-size: 13px;

        font-weight: 700;

        text-transform: uppercase;

        letter-spacing: 1px;
    }

    .score-number {
        color: #111827;

        font-size: 36px;

        font-weight: 850;

        margin-top: 4px;
    }

    .human-card {
        border-top: 5px solid #4f46e5;
    }

    .ai-card {
        border-top: 5px solid #9333ea;
    }

    .round-card {
        border-top: 5px solid #0ea5e9;
    }


    /* ================================
       SECTION
       ================================ */

    .section-title {
        color: #111827;

        font-size: 27px;

        font-weight: 800;

        margin-top: 30px;

        margin-bottom: 8px;
    }

    .section-description {
        color: #64748b;

        font-size: 15px;

        margin-bottom: 20px;
    }


    /* ================================
       CHALLENGE CARD
       ================================ */

    .challenge-card {
        background: white;

        border: 1px solid #e5e7eb;

        border-radius: 24px;

        padding: 28px;

        box-shadow:
            0 12px 35px rgba(15,23,42,0.07);

        margin-top: 12px;
    }

    .challenge-heading {
        color: #111827;

        font-size: 24px;

        font-weight: 800;

        margin-bottom: 6px;
    }

    .challenge-description {
        color: #64748b;

        font-size: 15px;

        margin-bottom: 18px;
    }


    /* ================================
       TARGET BADGE
       ================================ */

    .target-box {
        background:
            linear-gradient(
                135deg,
                #eef2ff,
                #f5f3ff
            );

        border: 1px solid #c7d2fe;

        border-radius: 16px;

        padding: 15px 20px;

        color: #3730a3;

        font-weight: 750;

        margin: 15px 0;
    }


    /* ================================
       HOME STEPS
       ================================ */

    .step-card {
        background: white;

        border: 1px solid #e5e7eb;

        border-radius: 18px;

        padding: 20px;

        height: 100%;

        box-shadow:
            0 7px 22px rgba(15,23,42,0.05);
    }

    .step-number {
        width: 38px;
        height: 38px;

        display: flex;

        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background: #eef2ff;

        color: #4f46e5;

        font-weight: 800;

        margin-bottom: 12px;
    }

    .step-title {
        font-size: 16px;

        font-weight: 750;

        color: #111827;

        margin-bottom: 5px;
    }

    .step-text {
        font-size: 14px;

        color: #64748b;

        line-height: 1.5;
    }


    /* ================================
       FOOTER
       ================================ */

    .footer {
        margin-top: 45px;

        padding: 28px;

        text-align: center;

        border-radius: 22px;

        background:
            linear-gradient(
                135deg,
                #111827,
                #312e81
            );

        color: white;

        box-shadow:
            0 15px 40px rgba(15,23,42,0.18);
    }

    .footer-title {
        font-size: 20px;

        font-weight: 800;

        margin-bottom: 8px;
    }

    .footer-text {
        color: rgba(255,255,255,0.72);

        font-size: 14px;

        line-height: 1.7;
    }


    /* ================================
       BUTTONS
       ================================ */

    .stButton > button {
        border-radius: 12px !important;

        min-height: 45px !important;

        font-weight: 700 !important;

        border: 1px solid #e5e7eb !important;

        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);

        box-shadow:
            0 8px 18px rgba(79,70,229,0.15);
    }


    /* ================================
       TABS
       ================================ */

    button[data-baseweb="tab"] {
        font-weight: 700 !important;

        font-size: 15px !important;
    }


    /* ================================
       MOBILE
       ================================ */

    @media (max-width: 768px) {

        .hero {
            padding: 30px 25px;
        }

        .hero-title {
            font-size: 34px;
        }

        .hero-subtitle {
            font-size: 15px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_font(size, bold=False):

    possible_fonts = []

    if bold:
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "arialbd.ttf",
        ]

    else:
        possible_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "arial.ttf",
        ]

    for font_path in possible_fonts:

        if os.path.exists(font_path):

            try:
                return ImageFont.truetype(
                    font_path,
                    size
                )

            except:
                pass

    return ImageFont.load_default()


def create_captcha():

    characters = string.ascii_uppercase + string.digits

    text = "".join(
        random.choice(characters)
        for _ in range(5)
    )

    width = 520
    height = 180

    image = Image.new(
        "RGB",
        (width, height),
        "#f8fafc"
    )

    draw = ImageDraw.Draw(image)

    # Background lines
    for _ in range(10):

        x1 = random.randint(0, width)
        y1 = random.randint(0, height)

        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line(
            (x1, y1, x2, y2),
            fill=(
                random.randint(120, 210),
                random.randint(120, 210),
                random.randint(120, 210)
            ),
            width=2
        )

    # Noise dots
    for _ in range(100):

        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        draw.ellipse(
            (x, y, x + 3, y + 3),
            fill="#94a3b8"
        )

    font = get_font(
        68,
        bold=True
    )

    # Character positions
    start_x = 70

    for index, char in enumerate(text):

        x = start_x + index * 80
        y = random.randint(45, 65)

        draw.text(
            (x, y),
            char,
            font=font,
            fill="#111827"
        )

    return image, text


def create_animal_grid():

    animals = [
        "CAT",
        "DOG",
        "FOX",
        "LION",
        "TIGER",
        "BEAR",
        "PANDA",
        "RABBIT",
        "HORSE",
        "MONKEY",
        "ZEBRA",
        "KOALA",
        "DEER",
        "WOLF",
        "FROG",
        "MOUSE"
    ]

    target = random.choice(
        [
            "CAT",
            "DOG",
            "RABBIT",
            "PANDA",
            "TIGER"
        ]
    )

    grid = animals.copy()

    positions = random.sample(
        range(16),
        3
    )

    for position in positions:

        grid[position] = target

    random.shuffle(grid)

    correct_indices = [
        i
        for i, animal in enumerate(grid)
        if animal == target
    ]

    return (
        grid,
        target,
        correct_indices
    )


def create_animal_image(grid):

    width = 720
    height = 720

    image = Image.new(
        "RGB",
        (width, height),
        "#f8fafc"
    )

    draw = ImageDraw.Draw(image)

    number_font = get_font(
        22,
        bold=True
    )

    animal_font = get_font(
        32,
        bold=True
    )

    for i, animal in enumerate(grid):

        row = i // 4
        col = i % 4

        x = col * 180
        y = row * 180

        # Card
        draw.rounded_rectangle(
            (
                x + 8,
                y + 8,
                x + 172,
                y + 172
            ),
            radius=18,
            fill="white",
            outline="#cbd5e1",
            width=3
        )

        # Tile number
        draw.text(
            (
                x + 22,
                y + 18
            ),
            str(i + 1),
            font=number_font,
            fill="#64748b"
        )

        # Animal name
        bbox = draw.textbbox(
            (0, 0),
            animal,
            font=animal_font
        )

        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = (
            x + (180 - text_width) / 2
        )

        text_y = (
            y + (180 - text_height) / 2
        )

        draw.text(
            (
                text_x,
                text_y
            ),
            animal,
            font=animal_font,
            fill="#312e81"
        )

    return image


def image_to_base64(image):

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def ask_groq_about_image(
    image,
    prompt,
    api_key
):

    if not api_key.strip():

        return (
            None,
            "Please enter your Groq API key in the sidebar."
        )

    try:

        client = Groq(
            api_key=api_key.strip()
        )

        image_base64 = image_to_base64(
            image
        )

        response = client.chat.completions.create(

            model=GROQ_MODEL,

            messages=[
                {
                    "role": "user",

                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",

                            "image_url": {
                                "url":
                                f"data:image/png;base64,{image_base64}"
                            }
                        }

                    ]
                }
            ],

            max_completion_tokens=200,

            reasoning_effort="none"
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        return answer, None

    except Exception as e:

        return (
            None,
            str(e)
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:24px;
            font-weight:800;
            margin-bottom:5px;
        ">
            🧠 AI Challenge
        </div>

        <div style="
            color:#c7d2fe;
            font-size:13px;
            margin-bottom:25px;
        ">
            Human vs Artificial Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### 🔑 Groq API Key"
    )

    api_key = st.text_input(
        "Enter your API key",
        type="password",
        placeholder="gsk_...",
        key="groq_api_key_input"
    )

    st.caption(
        "Your key is used for the current session. "
        "Never add it directly to GitHub."
    )

    st.divider()

    st.markdown(
        "### 🤖 Vision Model"
    )

    st.code(
        GROQ_MODEL
    )

    st.caption(
        "Used to analyze the visual challenges."
    )

    st.divider()

    # TEST API
    if st.button(
        "🧪 Test API Connection",
        use_container_width=True,
        key="sidebar_test_api_button"
    ):

        if not api_key.strip():

            st.warning(
                "Please enter your Groq API key first."
            )

        else:

            try:

                client = Groq(
                    api_key=api_key.strip()
                )

                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content":
                            "Reply with exactly: API WORKING"
                        }
                    ],
                    max_completion_tokens=20,
                    reasoning_effort="none"
                )

                if response.choices:

                    st.session_state.api_tested = True

                    st.success(
                        "✓ API connection successful!"
                    )

            except Exception as error:

                st.session_state.api_tested = False

                st.error(
                    "API connection failed."
                )

                st.caption(
                    str(error)
                )

    st.divider()

    # RESET
    if st.button(
        "🔄 Reset All Scores",
        use_container_width=True,
        key="sidebar_reset_button"
    ):

        st.session_state.human_score = 0
        st.session_state.ai_score = 0
        st.session_state.round_count = 0

        st.session_state.captcha_human_done = False
        st.session_state.captcha_ai_done = False

        st.session_state.animal_human_done = False
        st.session_state.animal_ai_done = False

        st.success(
            "Scores have been reset."
        )

        st.rerun()


# =========================================================
# HERO HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-badge">
            HUMAN × AI • VISUAL CHALLENGE
        </div>

        <div class="hero-title">
            🧠 Can AI Beat You?
        </div>

        <div class="hero-subtitle">
            Play fun challenges that are easy for humans
            but difficult for AI. Test your visual skills
            against artificial intelligence.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PROJECT INFORMATION
# =========================================================

info1, info2, info3 = st.columns(3)

with info1:

    st.markdown(
        """
        <div class="info-card">

            <div class="info-label">
                CF Name
            </div>

            <div class="info-value">
                Jahangeer Ali
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with info2:

    st.markdown(
        """
        <div class="info-card">

            <div class="info-label">
                ID
            </div>

            <div class="info-value">
                MRBICF2003
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with info3:

    st.markdown(
        """
        <div class="info-card">

            <div class="info-label">
                Project
            </div>

            <div class="info-value">
                Human vs AI Challenge
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SCOREBOARD
# =========================================================

st.markdown(
    """
    <div class="section-title">
        🏆 Scoreboard
    </div>

    <div class="section-description">
        See who is winning the Human vs AI challenge.
    </div>
    """,
    unsafe_allow_html=True
)

score1, score2, score3 = st.columns(3)


with score1:

    st.markdown(
        f"""
        <div class="score-card human-card">

            <div class="score-icon">
                👤
            </div>

            <div class="score-label">
                Human
            </div>

            <div class="score-number">
                {st.session_state.human_score}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with score2:

    st.markdown(
        f"""
        <div class="score-card ai-card">

            <div class="score-icon">
                🤖
            </div>

            <div class="score-label">
                AI
            </div>

            <div class="score-number">
                {st.session_state.ai_score}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with score3:

    st.markdown(
        f"""
        <div class="score-card round-card">

            <div class="score-icon">
                🎮
            </div>

            <div class="score-label">
                Rounds
            </div>

            <div class="score-number">
                {st.session_state.round_count}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# TABS
# =========================================================

tab_home, tab_captcha, tab_animals = st.tabs(
    [
        "🏠 Home",
        "🔤 Text CAPTCHA",
        "🐾 Animal Grid"
    ]
)


# =========================================================
# HOME
# =========================================================

with tab_home:

    st.markdown(
        """
        <div class="challenge-card">

            <div class="challenge-heading">
                Welcome to the Challenge 👋
            </div>

            <div class="challenge-description">
                Can human visual intelligence beat AI?
                Try the challenges and find out.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            margin-top:25px;
            margin-bottom:15px;
            font-size:22px;
            font-weight:800;
            color:#111827;
        ">
            How it works
        </div>
        """,
        unsafe_allow_html=True
    )

    step1, step2, step3, step4 = st.columns(4)


    with step1:

        st.markdown(
            """
            <div class="step-card">

                <div class="step-number">
                    1
                </div>

                <div class="step-title">
                    Choose
                </div>

                <div class="step-text">
                    Select a visual challenge
                    from the tabs.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with step2:

        st.markdown(
            """
            <div class="step-card">

                <div class="step-number">
                    2
                </div>

                <div class="step-title">
                    Human Solves
                </div>

                <div class="step-text">
                    Complete the challenge
                    yourself.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with step3:

        st.markdown(
            """
            <div class="step-card">

                <div class="step-number">
                    3
                </div>

                <div class="step-title">
                    AI Solves
                </div>

                <div class="step-text">
                    Groq Vision AI analyzes
                    the same challenge.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with step4:

        st.markdown(
            """
            <div class="step-card">

                <div class="step-number">
                    4
                </div>

                <div class="step-title">
                    Compare
                </div>

                <div class="step-text">
                    The scoreboard shows
                    who wins the round.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    if not api_key.strip():

        st.warning(
            "🔑 Enter your Groq API key in the sidebar "
            "before using the AI buttons."
        )

    else:

        st.success(
            "✓ API key entered. Your AI challenges are ready!"
        )


# =========================================================
# TEXT CAPTCHA
# =========================================================

with tab_captcha:

    st.markdown(
        """
        <div class="challenge-card">

            <div class="challenge-heading">
                🔤 Text CAPTCHA
            </div>

            <div class="challenge-description">
                Read the distorted characters and enter
                the correct sequence.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # CREATE CAPTCHA
    # -----------------------------------------------------

    if st.session_state.captcha_text is None:

        image, text = create_captcha()

        st.session_state.captcha_image = image
        st.session_state.captcha_text = text


    image = st.session_state.captcha_image
    correct_text = st.session_state.captcha_text


    st.write("")


    captcha_image_col, captcha_info_col = st.columns(
        [1.35, 1]
    )


    with captcha_image_col:

        st.image(
            image,
            width=520
        )


    with captcha_info_col:

        st.markdown(
            """
            <div class="target-box">

                🎯 Your task

                <br><br>

                Read the five characters
                shown in the CAPTCHA.

            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Human and AI will attempt the same CAPTCHA."
        )


    human_answer = st.text_input(
        "Enter CAPTCHA characters",
        placeholder="Type the characters here...",
        key="captcha_answer_input"
    )


    captcha_button1, captcha_button2 = st.columns(2)


    # HUMAN
    with captcha_button1:

        if st.button(
            "👤 Submit Human Answer",
            use_container_width=True,
            key="captcha_human_submit"
        ):

            if st.session_state.captcha_human_done:

                st.info(
                    "You already submitted this CAPTCHA."
                )

            elif (
                human_answer.strip().upper()
                ==
                correct_text.upper()
            ):

                st.session_state.human_score += 1
                st.session_state.round_count += 1

                st.session_state.captcha_human_done = True

                st.success(
                    "🎉 Correct! Human wins this challenge."
                )

            else:

                st.session_state.round_count += 1

                st.session_state.captcha_human_done = True

                st.error(
                    "❌ Incorrect answer."
                )

                st.info(
                    f"Correct answer: {correct_text}"
                )


    # AI
    with captcha_button2:

        if st.button(
            "🤖 Ask Groq AI",
            use_container_width=True,
            key="captcha_ai_submit"
        ):

            if st.session_state.captcha_ai_done:

                st.info(
                    "AI has already attempted this CAPTCHA."
                )

            elif not api_key.strip():

                st.warning(
                    "Please enter your Groq API key "
                    "in the sidebar first."
                )

            else:

                with st.spinner(
                    "🤖 Groq AI is analyzing the CAPTCHA..."
                ):

                    prompt = """
                    This is a visual CAPTCHA.

                    Carefully read the five uppercase
                    letters and numbers.

                    Return ONLY the characters.
                    Do not explain your answer.
                    Do not add spaces or punctuation.
                    """

                    ai_answer, error = ask_groq_about_image(
                        image,
                        prompt,
                        api_key
                    )


                if error:

                    st.error(
                        "❌ AI request failed."
                    )

                    st.caption(
                        error
                    )

                else:

                    st.session_state.captcha_ai_done = True

                    st.write(
                        f"AI response: **{ai_answer}**"
                    )

                    clean_ai = re.sub(
                        r"[^A-Za-z0-9]",
                        "",
                        ai_answer or ""
                    ).upper()

                    correct = correct_text.upper()


                    if clean_ai == correct:

                        st.session_state.ai_score += 1

                        st.success(
                            "🤖 AI solved the CAPTCHA!"
                        )

                    else:

                        st.error(
                            "🤖 AI could not solve it correctly."
                        )

                        st.info(
                            f"Correct answer: {correct}"
                        )


    st.divider()


    if st.button(
        "🔄 Generate New CAPTCHA",
        use_container_width=True,
        key="captcha_new_button"
    ):

        new_image, new_text = create_captcha()

        st.session_state.captcha_image = new_image
        st.session_state.captcha_text = new_text

        st.session_state.captcha_human_done = False
        st.session_state.captcha_ai_done = False

        st.rerun()


# =========================================================
# ANIMAL GRID
# =========================================================

with tab_animals:

    st.markdown(
        """
        <div class="challenge-card">

            <div class="challenge-heading">
                🐾 Animal Grid Hunt
            </div>

            <div class="challenge-description">
                Find every tile containing the target animal.
                Then compare your answer with AI.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # CREATE GRID
    # -----------------------------------------------------

    if st.session_state.animal_grid is None:

        (
            grid,
            target,
            correct_indices
        ) = create_animal_grid()

        st.session_state.animal_grid = grid
        st.session_state.animal_target = target
        st.session_state.animal_correct = correct_indices


    grid = st.session_state.animal_grid

    target = st.session_state.animal_target

    correct_indices = st.session_state.animal_correct


    st.markdown(
        f"""
        <div class="target-box">

            🎯 Target animal:
            <strong>{target}</strong>

            <br>

            Find every tile containing
            <strong>{target}</strong>.

        </div>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # IMAGE FOR AI
    # -----------------------------------------------------

    grid_image = create_animal_image(
        grid
    )


    grid_left, grid_right = st.columns(
        [1.2, 1]
    )


    with grid_left:

        st.image(
            grid_image,
            width=620
        )


    with grid_right:

        st.markdown(
            """
            <div class="challenge-card">

                <div class="challenge-heading">
                    Select tiles
                </div>

                <div class="challenge-description">
                    Tick every tile that contains
                    the target animal.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        selected = []

        tile_columns = st.columns(2)


        for i in range(16):

            column_index = i % 2

            with tile_columns[column_index]:

                checked = st.checkbox(
                    f"Tile {i + 1}",
                    key=f"animal_checkbox_{i}"
                )

                if checked:

                    selected.append(i)


    st.write("")


    animal_button1, animal_button2 = st.columns(2)


    # HUMAN
    with animal_button1:

        if st.button(
            "👤 Submit Human Answer",
            use_container_width=True,
            key="animal_human_submit"
        ):

            if st.session_state.animal_human_done:

                st.info(
                    "You already submitted this grid."
                )

            elif (
                sorted(selected)
                ==
                sorted(correct_indices)
            ):

                st.session_state.human_score += 1
                st.session_state.round_count += 1

                st.session_state.animal_human_done = True

                st.success(
                    "🎉 Excellent! Human found all matching tiles."
                )

            else:

                st.session_state.round_count += 1

                st.session_state.animal_human_done = True

                correct_tiles = [
                    i + 1
                    for i in correct_indices
                ]

                st.error(
                    "❌ Human answer is incorrect."
                )

                st.info(
                    f"Correct tiles: {correct_tiles}"
                )


    # AI
    with animal_button2:

        if st.button(
            "🤖 Ask Groq AI",
            use_container_width=True,
            key="animal_ai_submit"
        ):

            if st.session_state.animal_ai_done:

                st.info(
                    "AI has already attempted this grid."
                )

            elif not api_key.strip():

                st.warning(
                    "Please enter your Groq API key "
                    "in the sidebar first."
                )

            else:

                with st.spinner(
                    "🤖 Groq AI is analyzing the grid..."
                ):

                    prompt = f"""
                    This is a 4 by 4 visual grid.

                    The target animal is:
                    {target}

                    Each tile is numbered from 1 to 16.

                    Identify EVERY tile containing the
                    target animal.

                    Return ONLY the tile numbers separated
                    by commas.

                    Example:
                    2, 7, 11

                    Do not explain your answer.
                    """

                    ai_answer, error = ask_groq_about_image(
                        grid_image,
                        prompt,
                        api_key
                    )


                if error:

                    st.error(
                        "❌ AI request failed."
                    )

                    st.caption(
                        error
                    )

                else:

                    st.session_state.animal_ai_done = True

                    st.write(
                        f"AI response: **{ai_answer}**"
                    )

                    numbers = re.findall(
                        r"\d+",
                        ai_answer or ""
                    )

                    ai_indices = []


                    for number in numbers:

                        number_value = int(number)

                        if 1 <= number_value <= 16:

                            ai_indices.append(
                                number_value - 1
                            )


                    ai_indices = sorted(
                        list(
                            set(ai_indices)
                        )
                    )


                    if (
                        ai_indices
                        ==
                        sorted(correct_indices)
                    ):

                        st.session_state.ai_score += 1

                        st.success(
                            "🤖 AI correctly found all matching tiles!"
                        )

                    else:

                        correct_tiles = [
                            i + 1
                            for i in correct_indices
                        ]

                        st.error(
                            "🤖 AI selected the wrong tiles."
                        )

                        st.info(
                            f"Correct tiles: {correct_tiles}"
                        )


    st.divider()


    if st.button(
        "🔄 Generate New Animal Grid",
        use_container_width=True,
        key="animal_new_button"
    ):

        (
            new_grid,
            new_target,
            new_correct
        ) = create_animal_grid()


        st.session_state.animal_grid = new_grid

        st.session_state.animal_target = new_target

        st.session_state.animal_correct = new_correct

        st.session_state.animal_human_done = False

        st.session_state.animal_ai_done = False


        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        <div class="footer-title">
            🧠 Can AI Beat You?
        </div>

        <div class="footer-text">

            Human vs Artificial Intelligence Visual Challenge

            <br><br>

            <strong>CF Name:</strong>
            Jahangeer Ali

            &nbsp;&nbsp; | &nbsp;&nbsp;

            <strong>ID:</strong>
            MRBICF2003

            <br><br>

            Built with Streamlit + Groq Vision AI

        </div>

    </div>
    """,
    unsafe_allow_html=True
)
