```python
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
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "human_score": 0,
    "ai_score": 0,
    "rounds": 0,
    "captcha_text": "",
    "captcha_image": None,
    "result": "",
    "ai_answer": "",
    "api_key": "",
    "connected": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# LOAD API KEY FROM SECRETS
# =========================================================

try:
    secret_key = st.secrets.get("GROQ_API_KEY", "")

    if secret_key and not st.session_state.api_key:
        st.session_state.api_key = secret_key
        st.session_state.connected = True

except Exception:
    secret_key = ""


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
    ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(75, 120, 255, 0.10),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 20%,
                rgba(255, 174, 70, 0.10),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #f5f8ff 0%,
                #ffffff 48%,
                #fffaf2 100%
            );
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* =====================================================
       SIDEBAR
    ===================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #101d3d 0%,
                #172b59 55%,
                #102044 100%
            );
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    .sidebar-brand {
        text-align: center;
        padding: 12px 5px 22px 5px;
    }

    .sidebar-logo {
        font-size: 45px;
        margin-bottom: 4px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 900;
        letter-spacing: 0.3px;
    }

    .sidebar-subtitle {
        font-size: 12px;
        opacity: 0.70;
        margin-top: 5px;
    }

    .sidebar-section {
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.2px;
        opacity: 0.65;
        margin-top: 22px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    .connection-box {
        padding: 14px;
        border-radius: 14px;
        margin-top: 10px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.13);
    }

    .connected {
        color: #67e8b1 !important;
        font-weight: 800;
    }

    .not-connected {
        color: #ff9aaa !important;
        font-weight: 800;
    }

    /* =====================================================
       TOP HEADER
    ===================================================== */

    .top-header {
        background:
            linear-gradient(
                105deg,
                #101f46 0%,
                #18366f 52%,
                #24529c 100%
            );

        padding: 18px 28px;
        border-radius: 20px;

        color: white;

        display: flex;
        justify-content: space-between;
        align-items: center;

        margin-bottom: 30px;

        box-shadow:
            0 15px 35px rgba(18, 45, 95, 0.20);
    }

    .brand {
        font-size: 25px;
        font-weight: 900;
    }

    .brand-small {
        font-size: 12px;
        opacity: 0.65;
        margin-top: 2px;
    }

    .student-info {
        font-size: 14px;
        font-weight: 700;
        text-align: right;
        opacity: 0.95;
    }

    /* =====================================================
       HERO
    ===================================================== */

    .hero-badge {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 30px;
        background: #e8f0ff;
        color: #2453a6;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 58px;
        line-height: 1.05;
        font-weight: 950;
        color: #14285b;
        margin-bottom: 8px;
    }

    .hero-gradient {
        background: linear-gradient(
            90deg,
            #16377d,
            #3478dc,
            #d36a4e
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 24px;
        font-weight: 800;
        color: #2859a5;
        margin-bottom: 16px;
    }

    .hero-description {
        font-size: 17px;
        color: #50617f;
        line-height: 1.75;
        max-width: 850px;
    }

    .hero-card {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.95),
                rgba(242,247,255,0.88)
            );

        border: 1px solid #dce7f8;
        border-radius: 25px;

        padding: 28px;

        box-shadow:
            0 18px 45px rgba(35, 68, 120, 0.10);
    }

    .hero-icon {
        font-size: 65px;
        text-align: center;
        margin-bottom: 5px;
    }

    .hero-card-title {
        color: #172d63;
        text-align: center;
        font-size: 20px;
        font-weight: 900;
    }

    .hero-card-text {
        color: #60708c;
        text-align: center;
        line-height: 1.6;
        font-size: 14px;
    }

    /* =====================================================
       SECTION TITLES
    ===================================================== */

    .section-title {
        color: #152c61;
        font-size: 26px;
        font-weight: 900;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .section-caption {
        color: #71809a;
        font-size: 14px;
        margin-top: -8px;
        margin-bottom: 18px;
    }

    /* =====================================================
       SCOREBOARD
    ===================================================== */

    .score-card {
        background: rgba(255,255,255,0.95);
        border-radius: 22px;
        padding: 21px;
        text-align: center;

        border: 1px solid #dce6f4;

        box-shadow:
            0 10px 28px rgba(30, 65, 120, 0.08);

        transition: 0.2s ease;
    }

    .score-card:hover {
        transform: translateY(-3px);
        box-shadow:
            0 14px 34px rgba(30, 65, 120, 0.13);
    }

    .score-icon {
        font-size: 26px;
        margin-bottom: 4px;
    }

    .score-number {
        font-size: 40px;
        font-weight: 950;
        color: #153e8c;
        line-height: 1.1;
    }

    .score-label {
        font-size: 12px;
        font-weight: 800;
        color: #73809a;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .human-title {
        color: #119669;
        font-size: 14px;
        font-weight: 900;
        letter-spacing: 1px;
    }

    .ai-title {
        color: #df5267;
        font-size: 14px;
        font-weight: 900;
        letter-spacing: 1px;
    }

    .round-title {
        color: #a36a00;
        font-size: 14px;
        font-weight: 900;
        letter-spacing: 1px;
    }

    /* =====================================================
       MAIN CARDS
    ===================================================== */

    .card {
        background: rgba(255,255,255,0.94);
        border: 1px solid #dce6f4;
        border-radius: 22px;
        padding: 25px;

        box-shadow:
            0 9px 28px rgba(25, 55, 100, 0.075);
    }

    .card-title {
        color: #18346f;
        font-size: 21px;
        font-weight: 900;
    }

    .card-description {
        color: #697892;
        line-height: 1.65;
        font-size: 14px;
    }

    /* =====================================================
       CAPTCHA AREA
    ===================================================== */

    .captcha-header {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #17366f;
        font-size: 22px;
        font-weight: 900;
    }

    .captcha-note {
        color: #697892;
        font-size: 14px;
        line-height: 1.6;
    }

    /* =====================================================
       FEATURE CARDS
    ===================================================== */

    .feature-card {
        background: white;
        border: 1px solid #dce6f4;
        border-radius: 20px;
        padding: 23px;
        min-height: 175px;

        box-shadow:
            0 8px 25px rgba(30, 65, 120, 0.07);
    }

    .feature-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }

    .feature-title {
        font-size: 18px;
        color: #1a356d;
        font-weight: 900;
        margin-bottom: 7px;
    }

    .feature-text {
        font-size: 13px;
        color: #71809a;
        line-height: 1.6;
    }

    /* =====================================================
       STEPS
    ===================================================== */

    .step-card {
        background: white;
        border: 1px solid #e0e8f4;
        border-radius: 15px;
        padding: 15px 18px;
        margin-bottom: 9px;

        box-shadow:
            0 4px 15px rgba(30, 65, 120, 0.045);
    }

    .step-number {
        display: inline-flex;
        width: 30px;
        height: 30px;
        align-items: center;
        justify-content: center;

        background: #eaf1ff;
        color: #2453a6;

        border-radius: 50%;

        font-size: 13px;
        font-weight: 900;

        margin-right: 8px;
    }

    .step-text {
        color: #4e607d;
        font-size: 14px;
        font-weight: 600;
    }

    /* =====================================================
       INFO CARDS
    ===================================================== */

    .info-title {
        color: #18366f;
        font-size: 21px;
        font-weight: 900;
        margin-bottom: 18px;
    }

    .info-row {
        padding: 9px 0;
        border-bottom: 1px solid #edf1f7;
        color: #52627d;
        font-size: 14px;
    }

    .info-label {
        color: #1d3972;
        font-weight: 800;
    }

    /* =====================================================
       FOOTER
    ===================================================== */

    .footer {
        background:
            linear-gradient(
                105deg,
                #101f46,
                #1b3974,
                #244e91
            );

        color: white;
        text-align: center;

        padding: 28px;

        border-radius: 22px;
        margin-top: 35px;

        box-shadow:
            0 12px 30px rgba(20, 50, 100, 0.18);
    }

    .footer-title {
        font-size: 20px;
        font-weight: 900;
    }

    .footer-text {
        font-size: 13px;
        opacity: 0.75;
        margin-top: 8px;
    }

    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 12px !important;
        font-weight: 800 !important;
        min-height: 45px !important;
        border: 1px solid #d6e1f0 !important;
    }

    /* =====================================================
       INPUT
       ===================================================== */

    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #cfdced !important;
        min-height: 45px !important;
    }

    /* =====================================================
       DIVIDER
       ===================================================== */

    hr {
        border-color: #e5ebf4 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR — GROQ CONFIGURATION
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">🧠</div>

            <div class="sidebar-title">
                Human × AI
            </div>

            <div class="sidebar-subtitle">
                Visual Intelligence Challenge
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-section">AI Configuration</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            font-size:13px;
            line-height:1.6;
            opacity:0.75;
            margin-bottom:12px;
        ">
        Enter your Groq API key to enable the
        AI vision challenge.
        </div>
        """,
        unsafe_allow_html=True
    )

    api_input = st.text_input(
        "Groq API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_...",
        help="Your API key is kept in the current Streamlit session."
    )

    connect = st.button(
        "🔌 Connect Groq AI",
        use_container_width=True,
        type="primary"
    )

    if connect:

        if api_input.strip():

            st.session_state.api_key = api_input.strip()
            st.session_state.connected = True

            st.success("Groq AI connected!")

        else:

            st.session_state.connected = False

            st.error("Please enter a valid API key.")

    if st.session_state.connected:

        st.markdown(
            """
            <div class="connection-box">
                <div class="connected">
                    🟢 AI Connected
                </div>
                <div style="
                    font-size:12px;
                    opacity:0.65;
                    margin-top:5px;
                ">
                    Groq Vision is ready
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <div class="connection-box">
                <div class="not-connected">
                    🔴 AI Not Connected
                </div>
                <div style="
                    font-size:12px;
                    opacity:0.65;
                    margin-top:5px;
                ">
                    Enter API key above
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="sidebar-section">Game Controls</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "🔄 Reset Scoreboard",
        use_container_width=True
    ):

        st.session_state.human_score = 0
        st.session_state.ai_score = 0
        st.session_state.rounds = 0
        st.session_state.result = ""
        st.session_state.ai_answer = ""

        st.rerun()

    st.markdown(
        '<div class="sidebar-section">Project</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            font-size:13px;
            line-height:1.7;
            opacity:0.75;
        ">
            <b>CF Name</b><br>
            Jahangeer Ali<br><br>

            <b>ID</b><br>
            MRBICF2003<br><br>

            <b>Technology</b><br>
            Python • Streamlit • Groq
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.caption("🔐 API keys are never displayed as plain text.")


# =========================================================
# GROQ CLIENT
# =========================================================

client = None

if st.session_state.api_key:

    try:

        client = Groq(
            api_key=st.session_state.api_key
        )

    except Exception:

        client = None


# =========================================================
# TOP HEADER
# =========================================================

st.markdown(
    """
    <div class="top-header">

        <div>
            <div class="brand">
                🤖 Can AI Beat You?
            </div>

            <div class="brand-small">
                Human vs Artificial Intelligence Challenge
            </div>
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

hero_left, hero_right = st.columns(
    [1.55, 0.75],
    gap="large"
)

with hero_left:

    st.markdown(
        """
        <div class="hero-badge">
            HUMAN × AI • VISUAL CHALLENGE
        </div>

        <div class="hero-title">
            Can <span class="hero-gradient">AI Beat You?</span>
        </div>

        <div class="hero-subtitle">
            The Human vs AI Challenge
        </div>

        <div class="hero-description">

        CAPTCHA-style visual challenges are designed
        to test whether a user can recognize information
        that automated systems may find difficult.

        <br><br>

        Solve the challenge yourself, then give the
        <b>same image</b> to an AI vision model.

        <br><br>

        <b>Will human intelligence win — or will AI?</b>

        </div>
        """,
        unsafe_allow_html=True
    )

with hero_right:

    status_text = (
        "Groq Vision Ready"
        if st.session_state.connected
        else "Connect Groq AI"
    )

    status_icon = (
        "🟢"
        if st.session_state.connected
        else "🔴"
    )

    st.markdown(
        f"""
        <div class="hero-card">

            <div class="hero-icon">
                🤖
            </div>

            <div class="hero-card-title">
                AI Vision Engine
            </div>

            <div class="hero-card-text">
                Compare human visual recognition
                with an AI vision model.
            </div>

            <hr>

            <div style="
                text-align:center;
                font-weight:800;
                color:#53637f;
            ">
                {status_icon} {status_text}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SCOREBOARD
# =========================================================

st.write("")

st.markdown(
    '<div class="section-title">📊 Live Scoreboard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-caption">'
    'Track the performance of humans and AI in real time.'
    '</div>',
    unsafe_allow_html=True
)

s1, s2, s3 = st.columns(3, gap="medium")


with s1:

    st.markdown(
        f"""
        <div class="score-card">

            <div class="score-icon">
                👤
            </div>

            <div class="human-title">
                HUMAN
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

            <div class="score-icon">
                🤖
            </div>

            <div class="ai-title">
                AI
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

            <div class="score-icon">
                🎮
            </div>

            <div class="round-title">
                ROUNDS
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

    width = 520
    height = 180

    image = Image.new(
        "RGB",
        (width, height),
        "#eef6ff"
    )

    draw = ImageDraw.Draw(image)

    # Background waves
    for _ in range(12):

        x1 = random.randint(0, width)
        y1 = random.randint(0, height)

        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line(
            (x1, y1, x2, y2),
            fill=random.choice(
                [
                    "#b7cbe2",
                    "#c7d8eb",
                    "#9fb7d2"
                ]
            ),
            width=random.randint(1, 3)
        )

    # Noise dots
    for _ in range(230):

        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)

        radius = random.randint(1, 2)

        draw.ellipse(
            (
                x,
                y,
                x + radius,
                y + radius
            ),
            fill="#8ea7c2"
        )

    # Font
    try:

        font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            62
        )

    except:

        font = ImageFont.load_default()

    # CAPTCHA characters
    start_x = 75

    for char in text:

        y = random.randint(45, 65)

        draw.text(
            (start_x, y),
            char,
            fill=random.choice(
                [
                    "#173e7a",
                    "#c33f57",
                    "#16835d",
                    "#a36b00"
                ]
            ),
            font=font
        )

        start_x += 82

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

st.write("")

left, right = st.columns(
    [1.55, 0.75],
    gap="large"
)


# =========================================================
# HUMAN SIDE
# =========================================================

with left:

    st.markdown(
        """
        <div class="card">

            <div class="captcha-header">
                🧩 Solve the CAPTCHA
            </div>

            <div class="captcha-note">
                Carefully read the characters in the image
                and enter your answer below.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    st.image(
        st.session_state.captcha_image,
        use_container_width=True
    )

    answer = st.text_input(
        "Your Answer",
        placeholder="Enter the 5 characters...",
        key="captcha_input"
    )

    c1, c2 = st.columns(2)

    with c1:

        verify = st.button(
            "✅ Verify My Answer",
            use_container_width=True,
            type="primary"
        )

    with c2:

        regenerate = st.button(
            "🔄 Generate New",
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
                "Excellent! Your answer is correct."
            )

        else:

            st.session_state.result = (
                "wrong",
                "Incorrect. Try the next challenge!"
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
# AI SIDE
# =========================================================

with right:

    st.markdown(
        """
        <div class="card">

            <div class="ai-title">
                🤖 Ask AI
            </div>

            <div class="card-description">

            Give the same CAPTCHA image to the
            AI vision model and see whether it
            can recognize the characters.

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.session_state.connected:

        ask_ai = st.button(
            "🤖 Let AI Solve",
            use_container_width=True,
            type="primary"
        )

    else:

        st.warning(
            "Connect Groq AI from the sidebar first."
        )

        ask_ai = False


    if ask_ai:

        if client is None:

            st.error(
                "Unable to initialize Groq client."
            )

        else:

            with st.spinner(
                "AI is analyzing the image..."
            ):

                try:

                    # Convert image to bytes
                    buffer = io.BytesIO()

                    st.session_state.captcha_image.save(
                        buffer,
                        format="PNG"
                    )

                    image_bytes = buffer.getvalue()

                    image_base64 = base64.b64encode(
                        image_bytes
                    ).decode("utf-8")


                    # Groq Vision request
                    response = client.chat.completions.create(

                        model=(
                            "meta-llama/"
                            "llama-4-scout-17b-16e-instruct"
                        ),

                        messages=[
                            {
                                "role": "user",

                                "content": [

                                    {
                                        "type": "text",

                                        "text": (
                                            "Read the CAPTCHA "
                                            "characters in the image. "
                                            "Return ONLY the characters "
                                            "you see. Do not explain. "
                                            "Do not add spaces."
                                        )
                                    },

                                    {
                                        "type": "image_url",

                                        "image_url": {
                                            "url":
                                            (
                                                "data:image/png;base64,"
                                                + image_base64
                                            )
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


                    # Clean AI response
                    cleaned_ai = "".join(
                        c
                        for c in ai_text.upper()
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


                    st.caption(
                        "AI response has been compared "
                        "with the hidden CAPTCHA answer."
                    )


                except Exception as e:

                    st.error(
                        f"Groq API error: {str(e)}"
                    )


# =========================================================
# FEATURES
# =========================================================

st.write("")
st.write("")

st.markdown(
    '<div class="section-title">✨ Project Features</div>',
    unsafe_allow_html=True
)

f1, f2, f3 = st.columns(
    3,
    gap="medium"
)


with f1:

    st.markdown(
        """
        <div class="feature-card">

            <div class="feature-icon">
                🧩
            </div>

            <div class="feature-title">
                Interactive CAPTCHA
            </div>

            <div class="feature-text">
                A new randomized visual CAPTCHA
                is generated for every challenge.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with f2:

    st.markdown(
        """
        <div class="feature-card">

            <div class="feature-icon">
                ⚔️
            </div>

            <div class="feature-title">
                Human vs AI
            </div>

            <div class="feature-text">
                Compare human performance with
                an AI vision model using the
                same visual challenge.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with f3:

    st.markdown(
        """
        <div class="feature-card">

            <div class="feature-icon">
                ⚡
            </div>

            <div class="feature-title">
                Groq Vision AI
            </div>

            <div class="feature-text">
                A vision-capable Groq model analyzes
```
