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
    page_title="Can AI Beat You? | Human vs AI Challenge",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS & STYLING
# =========================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 50%, #fef6ee 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .top-header {
        background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
        padding: 20px 30px;
        border-radius: 16px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .brand {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    .student-info {
        font-size: 15px;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.15);
        padding: 6px 15px;
        border-radius: 30px;
        backdrop-filter: blur(5px);
    }

    .hero-title {
        font-size: 48px;
        font-weight: 900;
        color: #102a43;
        margin-bottom: 0;
    }

    .hero-subtitle {
        font-size: 22px;
        font-weight: 700;
        color: #334e68;
        margin-top: 5px;
    }

    .hero-description {
        font-size: 16px;
        color: #486581;
        line-height: 1.6;
        margin-top: 15px;
    }

    .card {
        background: white;
        border: 1px solid #d9e2ec;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 6px 20px rgba(16, 42, 67, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 15px;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(16, 42, 67, 0.1);
    }

    .score-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid #d9e2ec;
        box-shadow: 0 4px 15px rgba(16, 42, 67, 0.05);
    }

    .score-number {
        font-size: 42px;
        font-weight: 900;
        color: #0f2027;
        margin: 5px 0;
    }

    .score-label {
        font-weight: 700;
        color: #627d98;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .human-title {
        color: #107c41;
        font-size: 18px;
        font-weight: 800;
    }

    .ai-title {
        color: #d64545;
        font-size: 18px;
        font-weight: 800;
    }

    .section-title {
        color: #102a43;
        font-size: 24px;
        font-weight: 800;
        margin: 25px 0 15px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .footer {
        background: #0f2027;
        color: white;
        text-align: center;
        padding: 25px;
        border-radius: 16px;
        margin-top: 40px;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

defaults = {
    "human_score": 0,
    "ai_score": 0,
    "rounds": 0,
    "captcha_text": "",
    "captcha_image": None,
    "result": "",
    "ai_answer": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =========================================================
# SIDEBAR - API CONFIGURATION
# =========================================================

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("Enter your **Groq API Key** below or configure it in Streamlit secrets.")
    
    # Try fetching from secrets first
    secret_key = ""
    try:
        secret_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass

    api_key_input = st.text_input(
        "Groq API Key", 
        value=secret_key, 
        type="password",
        placeholder="gsk_..."
    )
    
    st.markdown("---")
    st.markdown("### 👨‍🎓 Developer Details")
    st.markdown("**CF Name:** Jahangeer Ali")
    st.markdown("**ID:** MRBICF2003")
    
    st.markdown("---")
    st.info("💡 **Tip:** Generate a new CAPTCHA and test your visual perception against Groq Vision AI!")

# Initialize Groq Client
client = None
groq_available = False

if api_key_input:
    try:
        client = Groq(api_key=api_key_input)
        groq_available = True
    except Exception:
        client = None
        groq_available = False

# =========================================================
# HEADER SECTION
# =========================================================

st.markdown(
    """
    <div class="top-header">
        <div class="brand">🤖 Can AI Beat You?</div>
        <div class="student-info">CF Name: Jahangeer Ali &nbsp;|&nbsp; ID: MRBICF2003</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HERO SECTION
# =========================================================

hero_left, hero_right = st.columns([1.35, 1], gap="large")

with hero_left:
    st.markdown(
        """
        <div class="hero-title">Can AI Beat You?</div>
        <div class="hero-subtitle">The Ultimate Human vs AI Challenge</div>
        <div class="hero-description">
            CAPTCHA challenges are designed to distinguish humans from automated systems by testing visual cognitive perception.<br><br>
            In this interactive project, solve dynamic challenges yourself, then challenge a high-performance Vision AI model to beat your score!<br><br>
            <b>Who will reign supreme — Human intuition or Artificial Intelligence?</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with hero_right:
    st.markdown(
        """
        <div class="card">
            <h3 style="color:#102a43; margin-top:0;">🔐 AI Connection Status</h3>
        """,
        unsafe_allow_html=True
    )
    
    if groq_available:
        st.success("🟢 Groq API Connected Successfully!")
    else:
        st.warning("⚠️ Please provide your Groq API key in the sidebar to activate AI solver.")
        
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# SCOREBOARD
# =========================================================

st.markdown('<div class="section-title">📊 Live Scoreboard</div>', unsafe_allow_html=True)

s1, s2, s3 = st.columns(3, gap="medium")

with s1:
    st.markdown(
        f"""
        <div class="score-card">
            <div class="human-title">👤 HUMAN SCORE</div>
            <div class="score-number">{st.session_state.human_score}</div>
            <div class="score-label">Correct Answers</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with s2:
    st.markdown(
        f"""
        <div class="score-card">
            <div class="ai-title">🤖 AI SCORE</div>
            <div class="score-number">{st.session_state.ai_score}</div>
            <div class="score-label">Correct Answers</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with s3:
    st.markdown(
        f"""
        <div class="score-card">
            <div style="color:#b7791f; font-size:18px; font-weight:800;">🎮 TOTAL ROUNDS</div>
            <div class="score-number">{st.session_state.rounds}</div>
            <div class="score-label">Challenges Played</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# CAPTCHA GENERATOR FUNCTION
# =========================================================

def create_captcha():
    characters = string.ascii_uppercase + string.digits
    text = "".join(random.choice(characters) for _ in range(5))

    width, height = 440, 160
    image = Image.new("RGB", (width, height), "#f0f4f8")
    draw = ImageDraw.Draw(image)

    # Background noise dots
    for _ in range(250):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.ellipse((x, y, x + 2, y + 2), fill="#bcccdc")

    # Background noise lines
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line((x1, y1, x2, y2), fill="#9fb3c8", width=2)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
    except:
        font = ImageFont.load_default()

    x = 45
    for char in text:
        y = random.randint(35, 60)
        draw.text(
            (x, y),
            char,
            fill=random.choice(["#102a43", "#9b2c2c", "#276749", "#b7791f"]),
            font=font
        )
        x += 70

    return text, image

def new_captcha():
    text, image = create_captcha()
    st.session_state.captcha_text = text
    st.session_state.captcha_image = image
    st.session_state.result = ""
    st.session_state.ai_answer = ""

if st.session_state.captcha_image is None:
    new_captcha()

# =========================================================
# INTERACTIVE GAME SECTION
# =========================================================

st.markdown('<div class="section-title">🧩 Challenge Arena</div>', unsafe_allow_html=True)

game_left, game_right = st.columns([1.3, 1], gap="large")

with game_left:
    st.markdown(
        """
        <div class="card">
            <h3 style="color:#102a43; margin-top:0;">Your Turn (Human)</h3>
            <p>Inspect the generated CAPTCHA code below, type what you see, and verify your answer.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.image(st.session_state.captcha_image, use_container_width=True)

    answer = st.text_input(
        "Enter CAPTCHA Code",
        placeholder="Type the 5 characters...",
        key="captcha_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        verify = st.button("✅ Verify Answer", use_container_width=True, type="primary")
    with col2:
        regenerate = st.button("🔄 New Challenge", use_container_width=True)

    if regenerate:
        new_captcha()
        st.rerun()

    if verify:
        st.session_state.rounds += 1
        if answer.strip().upper() == st.session_state.captcha_text:
            st.session_state.human_score += 1
            st.session_state.result = ("correct", "Brilliant! Your answer is absolutely correct.")
        else:
            st.session_state.result = ("wrong", f"Oops! Incorrect. The correct code was {st.session_state.captcha_text}.")

    if st.session_state.result:
        res_type, res_msg = st.session_state.result
        if res_type == "correct":
            st.success("🎉 " + res_msg)
        else:
            st.error("❌ " + res_msg)

with game_right:
    st.markdown(
        """
        <div class="card">
            <h3 style="color:#d64545; margin-top:0;">🤖 AI's Turn</h3>
            <p>Send the active CAPTCHA image to Groq Vision model and check if AI can read it accurately.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    ask_ai = st.button("🤖 Let AI Solve Challenge", use_container_width=True, type="secondary")

    if ask_ai:
        if not groq_available:
            st.error("Groq API key is missing! Please input it in the sidebar.")
        else:
            with st.spinner("Groq Vision AI is analyzing the CAPTCHA image..."):
                try:
                    buffer = io.BytesIO()
                    st.session_state.captcha_image.save(buffer, format="PNG")
                    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Read the text in this CAPTCHA image precisely. Return ONLY the 5 alphanumeric characters you see without any extra explanation."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        temperature=0
                    )

                    ai_text = response.choices[0].message.content.strip()
                    st.session_state.ai_answer = ai_text

                    cleaned_ai = "".join(c for c in ai_text.upper() if c.isalnum())
                    
                    if cleaned_ai == st.session_state.captcha_text:
                        st.session_state.ai_score += 1
                        st.success(f"🤖 AI Solved It Correctly! Answer: **{ai_text}**")
                    else:
                        st.error(f"🤖 AI Answered: **{ai_text}** (Target was {st.session_state.captcha_text})")

                except Exception as e:
                    st.error(f"API Error encountered: {str(e)}")

# =========================================================
# FEATURES & PROJECT INFO SECTION
# =========================================================

st.markdown('<div class="section-title">✨ Key Features & Architecture</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3, gap="medium")

with f1:
    st.markdown(
        """
        <div class="card">
            <h3>🧩 Dynamic CAPTCHA</h3>
            <p>Random characters, variable colors, line filters, and noise patterns generated on-the-fly for every round.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with f2:
    st.markdown(
        """
        <div class="card">
            <h3>⚖️ Real-Time Metrics</h3>
            <p>Live session tracking comparing human accuracy against automated vision intelligence.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with f3:
    st.markdown(
        """
        <div class="card">
            <h3>⚡ Groq Vision AI</h3>
            <p>High-speed multimodal inference powered by state-of-the-art vision models via Groq API.</p>
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
        🤖 <b>Can AI Beat You?</b> — Human vs AI Cognitive Challenge<br><br>
        <b>CF Name:</b> Jahangeer Ali &nbsp;|&nbsp; <b>ID:</b> MRBICF2003<br>
        Built with Python, Streamlit, and Groq Vision API
    </div>
    """,
    unsafe_allow_html=True
)
