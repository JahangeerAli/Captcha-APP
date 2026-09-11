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
    page_title="Can AI Beat You? | Interactive AI Challenge Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS & STYLING (Bold, Colorful & Large UI Elements)
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f4f8 0%, #ffffff 50%, #fef3e2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .top-banner {
        background: linear-gradient(90deg, #102a43, #243b53);
        padding: 18px 30px;
        border-radius: 16px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(16, 42, 67, 0.2);
    }
    
    .brand-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    
    .student-badge {
        background: rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .score-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid #d9e2ec;
        box-shadow: 0 6px 20px rgba(14, 30, 37, 0.06);
        transition: transform 0.2s ease;
    }
    
    .score-card:hover {
        transform: translateY(-3px);
    }

    .score-number {
        font-size: 40px;
        font-weight: 900;
        color: #102a43;
        margin: 6px 0;
    }

    .human-arena {
        background: #f0fff4;
        border: 2px solid #68d391;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(104, 211, 145, 0.15);
    }

    .ai-arena {
        background: #fff5f5;
        border: 2px solid #fc8181;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 4px 15px rgba(252, 129, 129, 0.15);
    }

    /* --- CUSTOM VIBRANT BUTTONS STYLING --- */
    .stButton > button {
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        border: none !important;
        color: white !important;
        background: linear-gradient(135deg, #3182ce 0%, #2b6cb0 100%) !important;
        box-shadow: 0 4px 14px rgba(49, 130, 206, 0.35) !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(49, 130, 206, 0.5) !important;
        background: linear-gradient(135deg, #2b6cb0 0%, #2c5282 100%) !important;
    }

    /* --- LARGE & ATTRACTIVE ACTIVITY SELECTION RADIO BUTTONS --- */
    div.row-widget.stRadio > div[role="radiogroup"] {
        background: linear-gradient(135deg, #102a43 0%, #243b53 100%) !important;
        padding: 14px 20px !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 25px rgba(16, 42, 67, 0.25) !important;
        gap: 20px !important;
    }
    
    div.row-widget.stRadio label {
        font-size: 19px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.1) !important;
        padding: 12px 26px !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div.row-widget.stRadio label:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-2px);
    }

    .footer {
        background: #102a43;
        color: white;
        text-align: center;
        padding: 22px;
        border-radius: 16px;
        margin-top: 40px;
        box-shadow: 0 -4px 20px rgba(16, 42, 67, 0.1);
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
    st.markdown("1. Choose your activity from the top tabs.\n2. Solve the challenge yourself.\n3. Click **Ask AI** to test Groq Vision AI's intelligence!")

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
        <div class="brand-title">🤖 Can AI Beat You? — Challenge Dashboard</div>
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
    st.markdown(f'<div class="score-card"><div style="color:#2f855a;font-size:15px;font-weight:800;">👤 HUMAN SCORE</div><div class="score-number">{st.session_state.human_score}</div><div style="color:#718096;font-size:12px;font-weight:700;">CORRECT ANSWERS</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="score-card"><div style="color:#c53030;font-size:15px;font-weight:800;">🤖 AI SCORE</div><div class="score-number">{st.session_state.ai_score}</div><div style="color:#718096;font-size:12px;font-weight:700;">CORRECT ANSWERS</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="score-card"><div style="color:#d69e2e;font-size:15px;font-weight:800;">🎮 TOTAL ROUNDS</div><div class="score-number">{st.session_state.rounds}</div><div style="color:#718096;font-size:12px;font-weight:700;">CHALLENGES PLAYED</div></div>', unsafe_allow_html=True)

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
        img = Image.new("RGB", (500, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        for _ in range(15):
            draw.line([random.randint(0, 500), random.randint(0, 260), random.randint(0, 500), random.randint(0, 260)], fill="#cbd5e1", width=2)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
        except:
            font = ImageFont.load_default()
        
        x = 50
        for char in text:
            draw.text((x, random.randint(60, 100)), char, fill=random.choice(["#102a43", "#c53030", "#2b6cb0", "#2f855a"]), font=font)
            x += 80
        return text, img

    if st.session_state.captcha_image is None:
        st.session_state.captcha_text, st.session_state.captcha_image = generate_captcha()

    c_human, c_ai = st.columns(2, gap="large")

    with c_human:
        st.markdown('<div class="human-arena"><h4>👤 Your Turn (Human)</h4><p style="color:#4a5568; font-size:14px;">Read the characters hidden behind the lines.</p>', unsafe_allow_html=True)
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
        st.markdown('<div class="ai-arena"><h4>🤖 AI\'s Turn (Groq Vision)</h4><p style="color:#4a5568; font-size:14px;">Let AI analyze the image and decode the characters.</p>', unsafe_allow_html=True)
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
        img = Image.new("RGB", (500, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        total = 0
        positions = [(50, 45), (200, 40), (110, 140), (280, 130)]
        for cx, cy in positions:
            val = random.randint(1, 6)
            total += val
            draw.rectangle([cx, cy, cx+75, cy+75], fill="#ffffff", outline="#94a3b8", width=3)
            r = 4  # Dot radius helper
            
            # Center dot
            if val in [1, 3, 5]: 
                draw.ellipse([cx+37-r, cy+37-r, cx+37+r, cy+37+r], fill="#102a43")
            # Top-left & Bottom-right dots
            if val >= 2:
                draw.ellipse([cx+20-r, cy+20-r, cx+20+r, cy+20+r], fill="#102a43")
                draw.ellipse([cx+55-r, cy+55-r, cx+55+r, cy+55+r], fill="#102a43")
            # Top-right & Bottom-left dots
            if val >= 4:
                draw.ellipse([cx+55-r, cy+20-r, cx+55+r, cy+20+r], fill="#102a43")
                draw.ellipse([cx+20-r, cy+55-r, cx+20+r, cy+55+r], fill="#102a43")
            # Middle-left & Middle-right dots (for 6)
            if val == 6:
                draw.ellipse([cx+20-r, cy+37-r, cx+20+r, cy+37+r], fill="#102a43")
                draw.ellipse([cx+55-r, cy+37-r, cx+55+r, cy+37+r], fill="#102a43")
        return total, img

    if st.session_state.dice_image is None:
        st.session_state.dice_total, st.session_state.dice_image = generate_dice()

    c_human, c_ai = st.columns(2, gap="large")

    with c_human:
        st.markdown('<div class="human-arena"><h4>👤 Your Turn (Human)</h4><p style="color:#4a5568; font-size:14px;">Count the total dots on all four dice.</p>', unsafe_allow_html=True)
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
        st.markdown('<div class="ai-arena"><h4>🤖 AI\'s Turn (Groq Vision)</h4><p style="color:#4a5568; font-size:14px;">Can AI accurately count all dots without missing any?</p>', unsafe_allow_html=True)
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
        🤖 <b>Can AI Beat You?</b> — Interactive Human vs AI Challenge Suite<br><br>
        <b>CF Name:</b> Jahangeer Ali &nbsp;|&nbsp; <b>ID:</b> MRBICF2003<br>
        Powered by Python, Streamlit & Groq Vision AI
    </div>
    """,
    unsafe_allow_html=True
)
