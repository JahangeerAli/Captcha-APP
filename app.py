import streamlit as st
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import base64


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Can AI Beat You?",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            linear-gradient(
                135deg,
                #f5fbff 0%,
                #ffffff 50%,
                #fff8ed 100%
            );
    }

    .top-header {
        background: linear-gradient(
            90deg,
            #142957,
            #203d78
        );

        padding: 16px 28px;
        border-radius: 0 0 18px 18px;

        color: white;

        display: flex;
        justify-content: space-between;
        align-items: center;

        margin-bottom: 25px;
    }

    .brand {
        font-size: 25px;
        font-weight: 800;
    }

    .student-info {
        font-size: 15px;
        font-weight: 600;
    }

    .hero-title {
        font-size: 52px;
        font-weight: 900;
        color: #17285b;
        margin-bottom: 0;
    }

    .hero-subtitle {
        font-size: 24px;
        font-weight: 700;
        color: #2453a6;
    }

    .hero-description {
        font-size: 17px;
        color: #35446d;
        line-height: 1.7;
    }

    .card {
        background: white;
        border: 1px solid #dce7f5;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 7px 25px rgba(25, 55, 100, 0.08);
    }

    .score-card {
        background: white;
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        border: 1px solid #dce7f5;
        box-shadow: 0 5px 18px rgba(30, 70, 120, 0.08);
    }

    .score-number {
        font-size: 38px;
        font-weight: 900;
        color: #153e8c;
    }

    .score-label {
        font-weight: 700;
        color: #52627f;
    }

    .human-title {
        color: #149a68;
        font-size: 22px;
        font-weight: 800;
    }

    .ai-title {
        color: #e84d62;
        font-size: 22px;
        font-weight: 800;
    }

    .section-title {
        color: #162b61;
        font-size: 25px;
        font-weight: 850;
    }

    .success-box {
        background: #e9fff4;
        border: 1px solid #8ce3bb;
        border-radius: 15px;
        padding: 15px;
        color: #13764f;
        font-weight: 700;
    }

    .error-box {
        background: #fff0f2;
        border: 1px solid #ff9aaa;
        border-radius: 15px;
        padding: 15px;
        color: #b02a42;
        font-weight: 700;
    }

    .footer {
        background: #142957;
        color: white;
        text-align: center;
        padding: 20px;
        border-radius: 18px;
        margin-top: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "human_score" not in st.session_state:
    st.session_state.human_score = 0

if "ai_score" not in st.session_state:
    st.session_state.ai_score = 0

if "rounds" not in st.session_state:
    st.session_state.rounds = 0

if "captcha_text" not in st.session_state:
    st.session_state.captcha_text = ""

if "captcha_image" not in st.session_state:
    st.session_state.captcha_image = None

if "result" not in st.session_state:
    st.session_state.result = ""

if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = ""


# =========================================================
# GROQ CLIENT
# =========================================================

try:

    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

    client = Groq(
        api_key=GROQ_API_KEY
    )

    groq_available = True

except Exception:

    client = None
    groq_available = False


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="top-header">

        <div class="brand">
            🤖 Can AI Beat You?
        </div>

        <div class="student-info">
            CF Name: Jahangeer Ali
            &nbsp;&nbsp; | &nbsp;&nbsp;
            ID: MRBICF2003
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO SECTION
# =========================================================

hero_left, hero_right = st.columns([1.35, 1])

with hero_left:

    st.markdown(
        """
        <div class="hero-title">
            Can AI Beat You?
        </div>

        <div class="hero-subtitle">
            The Human vs AI Challenge
        </div>

        <div class="hero-description">

        CAPTCHA challenges are designed to distinguish
        humans from automated systems.

        <br><br>

        In this project, you can solve challenges yourself
        and then ask an AI model to solve the same challenge.

        <br><br>

        <b>Who will perform better — Human or AI?</b>

        </div>
        """,
        unsafe_allow_html=True
    )

with hero_right:

    st.markdown(
        """
        <div class="card">

        <h2 style="color:#18367a;">
        🔐 AI Configuration
        </h2>

        <p>
        Groq AI is connected through a secure
        Streamlit secret.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    if groq_available:

        st.success("🟢 Groq AI is connected")

    else:

        st.warning(
            "⚠️ Groq API key is not configured yet."
        )


# =========================================================
# SCOREBOARD
# =========================================================

st.markdown(
    '<div class="section-title">📊 Live Scoreboard</div>',
    unsafe_allow_html=True
)

s1, s2, s3 = st.columns(3)

with s1:

    st.markdown(
        f"""
        <div class="score-card">

        <div class="human-title">
        👤 HUMAN
        </div>

        <div class="score-number">
        {st.session_state.human_score}
        </div>

        <div class="score-label">
        Correct Answers
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with s2:

    st.markdown(
        f"""
        <div class="score-card">

        <div class="ai-title">
        🤖 AI
        </div>

        <div class="score-number">
        {st.session_state.ai_score}
        </div>

        <div class="score-label">
        Correct Answers
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

with s3:

    st.markdown(
        f"""
        <div class="score-card">

        <div style="color:#a36a00;font-size:22px;font-weight:800;">
        🎮 ROUNDS
        </div>

        <div class="score-number">
        {st.session_state.rounds}
        </div>

        <div class="score-label">
        Challenges Played
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# =========================================================
# CAPTCHA GENERATOR
# =========================================================

def create_captcha():

    characters = (
        string.ascii_uppercase +
        string.digits
    )

    text = "".join(
        random.choice(characters)
        for _ in range(5)
    )

    width = 420
    height = 150

    image = Image.new(
        "RGB",
        (width, height),
        "#edf6ff"
    )

    draw = ImageDraw.Draw(image)

    # Noise dots
    for _ in range(180):

        x = random.randint(0, width)
        y = random.randint(0, height)

        draw.ellipse(
            (x, y, x + 2, y + 2),
            fill="#9bb1c8"
        )

    # Noise lines
    for _ in range(8):

        x1 = random.randint(0, width)
        y1 = random.randint(0, height)

        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line(
            (x1, y1, x2, y2),
            fill="#7c94ad",
            width=2
        )

    # Text
    try:

        font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            55
        )

    except:

        font = ImageFont.load_default()

    x = 55

    for char in text:

        y = random.randint(40, 65)

        draw.text(
            (x, y),
            char,
            fill=random.choice(
                [
                    "#183c76",
                    "#c53c54",
                    "#17815a",
                    "#a36a00"
                ]
            ),
            font=font
        )

        x += 62

    return text, image


# =========================================================
# NEW CAPTCHA
# =========================================================

def new_captcha():

    text, image = create_captcha()

    st.session_state.captcha_text = text
    st.session_state.captcha_image = image

    st.session_state.result = ""
    st.session_state.ai_answer = ""


if st.session_state.captcha_image is None:

    new_captcha()


# =========================================================
# CAPTCHA SECTION
# =========================================================

left, right = st.columns([1.55, 0.75])

with left:

    st.markdown(
        """
        <div class="card">

        <div class="section-title">
        🧩 Solve the CAPTCHA
        </div>

        <p>
        Enter the characters shown in the image.
        Then compare your answer with AI.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(
        st.session_state.captcha_image,
        width=420
    )

    answer = st.text_input(
        "Your Answer",
        placeholder="Enter CAPTCHA text...",
        key="captcha_input"
    )

    c1, c2 = st.columns(2)

    with c1:

        verify = st.button(
            "✅ Verify Human Answer",
            use_container_width=True
        )

    with c2:

        regenerate = st.button(
            "🔄 New CAPTCHA",
            use_container_width=True
        )

    if regenerate:

        new_captcha()
        st.rerun()

    if verify:

        st.session_state.rounds += 1

        if (
            answer.strip().upper()
            == st.session_state.captcha_text
        ):

            st.session_state.human_score += 1

            st.session_state.result = (
                "correct",
                "Excellent! Your CAPTCHA answer is correct."
            )

        else:

            st.session_state.result = (
                "wrong",
                f"Incorrect. Correct answer was "
                f"{st.session_state.captcha_text}."
            )

    if st.session_state.result:

        result_type, message = st.session_state.result

        if result_type == "correct":

            st.success(
                "🎉 " + message
            )

        else:

            st.error(
                "❌ " + message
            )


# =========================================================
# AI SECTION
# =========================================================

with right:

    st.markdown(
        """
        <div class="card">

        <div class="ai-title">
        🤖 Ask AI
        </div>

        <p>
        Send the CAPTCHA image to Groq Vision
        and let AI attempt the challenge.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    ask_ai = st.button(
        "🤖 Let AI Solve",
        use_container_width=True,
        type="primary"
    )

    if ask_ai:

        if not groq_available:

            st.error(
                "Groq API key is not configured."
            )

        else:

            with st.spinner(
                "AI is analyzing the CAPTCHA..."
            ):

                try:

                    # Convert image to base64

                    buffer = io.BytesIO()

                    st.session_state.captcha_image.save(
                        buffer,
                        format="PNG"
                    )

                    image_bytes = buffer.getvalue()

                    image_base64 = base64.b64encode(
                        image_bytes
                    ).decode("utf-8")

                    response = client.chat.completions.create(

                        model="meta-llama/llama-4-scout-17b-16e-instruct",

                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": (
                                            "Read the CAPTCHA image. "
                                            "Return ONLY the five "
                                            "characters you see. "
                                            "Do not explain."
                                        )
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url":
                                            f"data:image/png;base64,"
                                            f"{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],

                        temperature=0
                    )

                    ai_text = (
                        response
                        .choices[0]
                        .message
                        .content
                        .strip()
                    )

                    st.session_state.ai_answer = ai_text

                    cleaned_ai = "".join(
                        c for c in ai_text.upper()
                        if c.isalnum()
                    )

                    correct = (
                        cleaned_ai
                        == st.session_state.captcha_text
                    )

                    if correct:

                        st.session_state.ai_score += 1

                        st.success(
                            f"🤖 AI got it right: {ai_text}"
                        )

                    else:

                        st.error(
                            f"🤖 AI answered: {ai_text}"
                        )

                except Exception as e:

                    st.error(
                        f"Groq API error: {str(e)}"
                    )


# =========================================================
# FEATURES
# =========================================================

st.write("")

st.markdown(
    '<div class="section-title">✨ Project Features</div>',
    unsafe_allow_html=True
)

f1, f2, f3 = st.columns(3)

with f1:

    st.markdown(
        """
        <div class="card">

        <h3>🧩 Interactive CAPTCHA</h3>

        <p>
        Random CAPTCHA challenges are generated
        for every round.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

with f2:

    st.markdown(
        """
        <div class="card">

        <h3>👤 vs 🤖 Comparison</h3>

        <p>
        Human and AI scores are tracked
        throughout the session.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

with f3:

    st.markdown(
        """
        <div class="card">

        <h3>⚡ Groq Vision AI</h3>

        <p>
        Groq's vision-capable model analyzes
        the CAPTCHA image.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HOW IT WORKS
# =========================================================

st.write("")

st.markdown(
    '<div class="section-title">🔬 How Does It Work?</div>',
    unsafe_allow_html=True
)

steps = [
    "A random CAPTCHA is generated.",
    "The human enters the visible characters.",
    "The answer is verified.",
    "The same image is sent to the AI model.",
    "AI's answer is compared with the correct answer.",
    "The Human vs AI scoreboard is updated."
]

for i, step in enumerate(steps, 1):

    st.markdown(
        f"""
        <div class="card" style="margin-bottom:8px;padding:14px;">

        <b style="color:#2453a6;">
        {i}.
        </b>

        &nbsp; {step}

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.write("")

info1, info2 = st.columns(2)

with info1:

    st.markdown(
        """
        <div class="card">

        <h2>📌 Project Information</h2>

        <b>CF Name:</b> Jahangeer Ali<br><br>

        <b>ID:</b> MRBICF2003<br><br>

        <b>Technology:</b> Python + Streamlit<br><br>

        <b>AI:</b> Groq Vision API<br><br>

        <b>Deployment:</b> GitHub + Streamlit Community Cloud

        </div>
        """,
        unsafe_allow_html=True
    )


with info2:

    st.markdown(
        """
        <div class="card">

        <h2>🎯 Project Objective</h2>

        <p>
        This project demonstrates how AI vision models
        can interact with visual CAPTCHA-style challenges
        and compares their performance with a human user.
        </p>

        <p>
        The project is designed as an interactive
        AI literacy and Human-vs-AI demonstration.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

    🤖 <b>Can AI Beat You?</b>

    <br><br>

    CF Name: Jahangeer Ali
    &nbsp; | &nbsp;
    ID: MRBICF2003

    <br>

    Built with Python • Streamlit • Groq AI

    </div>
    """,
    unsafe_allow_html=True
)
