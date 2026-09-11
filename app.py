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
    page_title="Can AI Beat You? | Elite AI Challenge Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS & STYLING (Elite Modern Dashboard UI)
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    .top-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px 35px;
        border-radius: 20px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .brand-title {
        font-size: 28px;
        font-weight: 900;
        letter-spacing: 0.5px;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .student-badge {
        background: rgba(56, 189, 248, 0.1);
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 700;
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
    }

    .score-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 32px rgba(56, 189, 248, 0.2);
        border-color: rgba(56, 189, 248, 0.4);
    }

    .score-number {
        font-size: 44px;
        font-weight: 900;
        color: #f8fafc;
        margin: 8px 0;
        text-shadow: 0 2px 10px rgba(255, 255, 255, 0.2);
    }

    .human-arena {
        background: rgba(6, 78, 59, 0.4);
        border: 2px solid #059669;
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 8px 25px rgba(5, 150, 105, 0.2);
        backdrop-filter: blur(10px);
    }

    .ai-arena {
        background: rgba(127, 29, 29, 0.4);
        border: 2px solid #dc2626;
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.2);
        backdrop-filter: blur(10px);
    }

    /* --- PREMIUM VIBRANT BUTTONS STYLING --- */
    .stButton > button {
        font-weight: 800 !important;
        border-radius: 14px !important;
        padding: 0.7rem 1.4rem !important;
        border: none !important;
        color: white !important;
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.6) !important;
        background: linear-gradient(135deg, #0284c7 0%, #1d4ed8 100%) !important;
    }

    /* --- GORGEOUS MODERN TAB-STYLE RADIO BUTTONS --- */
    div.row-widget.stRadio > div[role="radiogroup"] {
        background: rgba(30, 41, 59, 0.8) !important;
        padding: 10px 15px !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
        display: flex !important;
        gap: 15px !important;
    }
    
    div.row-widget.stRadio label {
        font-size: 18px !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        background: rgba(255, 255, 255, 0.05) !important;
        padding: 12px 28px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div.row-widget.stRadio label:hover {
        background: rgba(56, 189, 248, 0.2) !important;
        border-color: #38bdf8 !important;
        transform: translateY(-2px);
    }

    .footer {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: #94a3b8;
        text-align: center;
        padding: 25px;
        border-radius: 20px;
        margin-top: 50px;
        box-shadow: 0 -8px 25px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
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
    "captcha_image": None, "captcha_text": "", "captcha_result": "",
    "dice_image": None, "dice_total": 0, "dice_result": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =========================================================
# SIDEBAR CONFIGURATION
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
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
    st.markdown("### 👨‍💻 Developer Details")
    st.info("**CF Name:** Jahangeer Ali\n\n**ID:** MRBICF2003")
    
    st.markdown("---")
    st.markdown("### 💡 How to Play")
    st.markdown("1. Choose your activity from the tabs above.\n2. Solve the challenge yourself.\n3. Click **Ask AI** to test Groq Vision AI's intelligence!")

client = None
groq_available = False
if api_key_input:
    try:
        client = Groq(api_key=api_key_input)
        groq_available = True
    except Exception:
        pass

# =========================================================
# TOP HEADER BANNER
# =========================================================
st.markdown(
    """
    <div class="top-banner">
        <div class="brand-title">🤖 Can AI Beat You? — Elite Dashboard</div>
        <div class="student-badge">CF Name: Jahangeer Ali &nbsp;|&nbsp; ID: MRBICF2003</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LIVE SCOREBOARD
# =========================================================
col1, col2, col3 = st.columns(3, gap="medium")
with col1:
    st.markdown(f'<div class="score-card"><div style="color:#34d399;font-size:15px;font-weight:800;">👤 HUMAN SCORE</div><div class="score-number">{st.session_state.human_score}</div><div style="color:#94a3b8;font-size:12px;font-weight:700;">CORRECT ANSWERS</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="score-card"><div style="color:#f87171;font-size:15px;font-weight:800;">🤖 AI SCORE</div><div class="score-number">{st.session_state.ai_score}</div><div style="color:#94a3b8;font-size:12px;font-weight:700;">CORRECT ANSWERS</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="score-card"><div style="color:#fbbf24;font-size:15px;font-weight:800;">🎮 TOTAL ROUNDS</div><div class="score-number">{st.session_state.rounds}</div><div style="color:#94a3b8;font-size:12px;font-weight:700;">CHALLENGES PLAYED</div></div>', unsafe_allow_html=True)

st.write("")
st.write("")

# =========================================================
# HELPER: GROQ VISION API CALL
# =========================================================
def ask_groq_vision(image, prompt):
    if not groq_available or client is None:
        return None, "Groq API key not provided in the sidebar."
    try:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                ]
            }],
            temperature=0
        )
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        return None, str(e)

# =========================================================
# ACTIVITY SELECTION TABS
# =========================================================
activity_tab = st.radio(
    "Select Activity", 
    ["🔐 CAPTCHA Visual Challenge", "🎲 Dice Dot Counter"], 
    horizontal=True, 
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# ACTIVITY 1: CAPTCHA VISUAL CHALLENGE
# =========================================================
if activity_tab == "🔐 CAPTCHA Visual Challenge":
    st.markdown("### 🔐 Advanced CAPTCHA Challenge")
    st.markdown("Inspect the generated visual challenge below, type what you see, and verify your perceptual skills against AI.")

    def generate_captcha():
        text = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        img = Image.new("RGB", (500, 260), "#1e293b")
        draw = ImageDraw.Draw(img)
        for _ in range(15):
            draw.line([random.randint(0, 500), random.randint(0, 260), random.randint(0, 500), random.randint(0, 260)], fill="#475569", width=2)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
        except:
            font = ImageFont.load_default()
        
        x = 50
        for char in text:
            draw.text((x, random.randint(60, 100)), char, fill=random.choice(["#38bdf8", "#f43f5e", "#fbbf24", "#34d399"]), font=font)
            x += 80
        return text, img

    if st.session_state.captcha_image is None:
        st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()

    c_human, c_ai = st.columns(2, gap="large")

    with c_human:
        st.markdown('<div class="human-arena"><h4 style="color:#34d399;">👤 Your Turn (Human)</h4><p style="color:#cbd5e1; font-size:14px;">Read the characters hidden behind the lines.</p>', unsafe_allow_html=True)
        st.image(st.session_state.captcha_image, use_container_width=True)
        user_input = st.text_input("Enter CAPTCHA text:", key="cap_in")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Verify Answer", key="cap_chk", use_container_width=True):
                st.session_state.rounds += 1
                if user_input.strip().upper() == st.session_state.captcha_text:
                    st.session_state.human_score += 1
                    st.session_state.captcha_result = ("correct", "Spot on! Your human vision wins.")
                else:
                    st.session_state.captcha_result = ("wrong", f"Incorrect! The code was {st.session_state.captcha_text}.")
        with col_btn2:
            if st.button("🔄 New CAPTCHA", key="cap_new", use_container_width=True):
                st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()
                st.session_state.captcha_result = ""
                st.rerun()

        if st.session_state.captcha_result:
            t, m = st.session_state.captcha_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_ai:
        st.markdown('<div class="ai-arena"><h4 style="color:#f87171;">🤖 AI\'s Turn (Groq Vision)</h4><p style="color:#cbd5e1; font-size:14px;">Let AI analyze the image and decode the characters.</p>', unsafe_allow_html=True)
        st.write("")
        st.write("")
        if st.button("🚀 Let AI Solve Challenge", key="cap_ai_btn", use_container_width=True):
            if not groq_available:
                st.error("Please provide your Groq API key in the sidebar.")
            else:
                with st.spinner("AI is analyzing visual noise..."):
                    ans, err = ask_groq_vision(
                        st.session_state.captcha_image, 
                        "Read the 5 alphanumeric characters hidden behind the lines in this image. Return ONLY the 5 characters."
                    )
                    if err:
                        st.error(err)
                    else:
                        st.info(f"**AI Output:** {ans}")
                        if st.session_state.captcha_text in ans.upper():
                            st.session_state.ai_score += 1
                            st.success("AI successfully decoded the CAPTCHA!")
                        else:
                            st.warning("AI failed or hallucinated the text!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIVITY 2: DICE DOT COUNTER
# =========================================================
elif activity_tab == "🎲 Dice Dot Counter":
    st.markdown("### 🎲 Dice Dot Counter Challenge")
    st.markdown("Count every single dot across all dice in the image. Highly challenging for computer vision!")

    def generate_dice():
        img = Image.new("RGB", (500, 260), "#1e293b")
        draw = ImageDraw.Draw(img)
        total = 0
        positions = [(50, 45), (200, 40), (110, 140), (280, 130)]
        for cx, cy in positions:
            val = random.randint(1, 6)
            total += val
            draw.rectangle([cx, cy, cx+75, cy+75], fill="#0f172a", outline="#475569", width=3)
            r = 4  # Dot radius helper
            
            # Center dot
            if val in [1, 3, 5]: 
                draw.ellipse([cx+37-r, cy+37-r, cx+37+r, cy+37+r], fill="#38bdf8")
            # Top-left & Bottom-right dots
            if val >= 2:
                draw.ellipse([cx+20-r, cy+20-r, cx+20+r, cy+20+r], fill="#38bdf8")
                draw.ellipse([cx+55-r, cy+55-r, cx+55+r, cy+55+r], fill="#38bdf8")
            # Top-right & Bottom-left dots
            if val >= 4:
                draw.ellipse([cx+55-r, cy+20-r, cx+55+r, cy+20+r], fill="#38bdf8")
                draw.ellipse([cx+20-r, cy+55-r, cx+20+r, cy+55+r], fill="#38bdf8")
            # Middle-left & Middle-right dots (for 6)
            if val == 6:
                draw.ellipse([cx+20-r, cy+37-r, cx+20+r, cy+37+r], fill="#38bdf8")
                draw.ellipse([cx+55-r, cy+37-r, cx+55+r, cy+37+r], fill="#38bdf8")
        return total, img

    if st.session_state.dice_image is None:
        st.session_state.dice_total, st.session_state.dice_image = generate_dice()

    c_human, c_ai = st.columns(2, gap="large")

    with c_human:
        st.markdown('<div class="human-arena"><h4 style="color:#34d399;">👤 Your Turn (Human)</h4><p style="color:#cbd5e1; font-size:14px;">Count the total dots on all four dice.</p>', unsafe_allow_html=True)
        st.image(st.session_state.dice_image, use_container_width=True)
        dice_guess = st.number_input("Total dot count?", min_value=1, max_value=30, value=10, key="dice_in")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Check Dot Count", key="dice_chk", use_container_width=True):
                st.session_state.rounds += 1
                if int(dice_guess) == st.session_state.dice_total:
                    st.session_state.human_score += 1
                    st.session_state.dice_result = ("correct", f"Correct! Total dots were {st.session_state.dice_total}.")
                else:
                    st.session_state.dice_result = ("wrong", f"Incorrect! Total dots were actually {st.session_state.dice_total}.")
        with col_btn2:
            if st.button("🔄 New Dice", key="dice_new", use_container_width=True):
                st.session_state.dice_total, st.session_state.dice_image = generate_dice()
                st.session_state.dice_result = ""
                st.rerun()

        if st.session_state.dice_result:
            t, m = st.session_state.dice_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_ai:
        st.markdown('<div class="ai-arena"><h4 style="color:#f87171;">🤖 AI\'s Turn (Groq Vision)</h4><p style="color:#cbd5e1; font-size:14px;">Can AI accurately count all dots without missing any?</p>', unsafe_allow_html=True)
        st.write("")
        st.write("")
        if st.button("🚀 Let AI Count Dots", key="dice_ai_btn", use_container_width=True):
            if not groq_available:
                st.error("Please provide your Groq API key in the sidebar.")
            else:
                with st.spinner("AI counting dots across dice..."):
                    ans, err = ask_groq_vision(
                        st.session_state.dice_image, 
                        "Count the exact total number of dots across all dice shown in this image. Return ONLY the final integer number."
                    )
                    if err:
                        st.error(err)
                    else:
                        st.info(f"**AI Output:** {ans}")
                        if str(st.session_state.dice_total) in ans:
                            st.session_state.ai_score += 1
                            st.success("AI counted correctly!")
                        else:
                            st.warning("AI miscalculated the dot count!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER SECTION
# =========================================================
st.markdown(
    """
    <div class="footer">
        🤖 <b>Can AI Beat You?</b> — Elite Human vs AI Challenge Hub<br><br>
        <b>CF Name:</b> Jahangeer Ali &nbsp;|&nbsp; <b>ID:</b> MRBICF2003<br>
        Powered by Python, Streamlit & Groq Vision AI
    </div>
    """,
    unsafe_allow_html=True
)
