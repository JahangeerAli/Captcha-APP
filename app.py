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
    page_title="Can AI Beat You? | Multi-Activity Challenge",
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
        background: linear-gradient(135deg, #f4f8fb 0%, #ffffff 50%, #fef7ed 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .top-header {
        background: linear-gradient(90deg, #142957, #203d78);
        padding: 16px 28px;
        border-radius: 0 0 18px 18px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 5px 20px rgba(20, 41, 87, 0.15);
    }
    
    .brand {
        font-size: 24px;
        font-weight: 800;
    }
    
    .student-info {
        font-size: 15px;
        font-weight: 600;
    }

    .card {
        background: white;
        border: 1px solid #dce7f5;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 6px 20px rgba(25, 55, 100, 0.06);
        margin-bottom: 15px;
    }

    .human-box {
        background: #f0fff4;
        border: 2px solid #8ce3bb;
        border-radius: 18px;
        padding: 22px;
    }

    .ai-box {
        background: #fff0f2;
        border: 2px solid #ff9aaa;
        border-radius: 18px;
        padding: 22px;
    }

    .score-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        border: 1px solid #dce7f5;
        box-shadow: 0 4px 15px rgba(30, 70, 120, 0.05);
    }

    .score-number {
        font-size: 38px;
        font-weight: 900;
        color: #153e8c;
        margin: 5px 0;
    }

    .score-label {
        font-weight: 700;
        color: #52627f;
        font-size: 13px;
        text-transform: uppercase;
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
# SESSION STATE INITIALIZATION
# =========================================================
defaults = {
    "human_score": 0,
    "ai_score": 0,
    "rounds": 0,
    "dice_image": None, "dice_total": 0, "dice_result": "",
    "word_image": None, "word_text": "", "word_result": "",
    "order_image": None, "order_sequence": [], "order_result": "",
    "fool_image": None, "fool_ans": "", "fool_result": "",
    "animal_image": None, "animal_count": 0, "animal_target": "", "animal_result": "",
    "pattern_image": None, "pattern_target": "", "pattern_result": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =========================================================
# SIDEBAR CONFIGURATION
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ AI Configuration")
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
    st.markdown("### 💡 Instructions")
    st.info("Switch between activities using the top pill buttons, solve challenges, and test Groq Vision AI!")

client = None
groq_available = False
if api_key_input:
    try:
        client = Groq(api_key=api_key_input)
        groq_available = True
    except Exception:
        pass

# =========================================================
# HEADER SECTION (Original Style Restored)
# =========================================================
st.markdown(
    """
    <div class="top-header">
        <div class="brand">🤖 Can AI Beat You?</div>
        <div class="student-info">CF Name: Jahangeer Ali &nbsp;&nbsp; | &nbsp;&nbsp; ID: MRBICF2003</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LIVE SCOREBOARD (Original Style Restored)
# =========================================================
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(f'<div class="score-card"><div style="color:#149a68;font-size:18px;font-weight:800;">👤 HUMAN</div><div class="score-number">{st.session_state.human_score}</div><div class="score-label">Correct Answers</div></div>', unsafe_allow_html=True)
with s2:
    st.markdown(f'<div class="score-card"><div style="color:#e84d62;font-size:18px;font-weight:800;">🤖 AI</div><div class="score-number">{st.session_state.ai_score}</div><div class="score-label">Correct Answers</div></div>', unsafe_allow_html=True)
with s3:
    st.markdown(f'<div class="score-card"><div style="color:#a36a00;font-size:18px;font-weight:800;">🎮 ROUNDS</div><div class="score-number">{st.session_state.rounds}</div><div class="score-label">Challenges Played</div></div>', unsafe_allow_html=True)

st.write("")

# =========================================================
# ACTIVITY SELECTION PILLS
# =========================================================
tabs = [
    "🎲 Dice Count", 
    "🔤 Hidden Word", 
    "🔢 Click in Order", 
    "😲 Don't Be Fooled", 
    "🐾 Animal Grid", 
    "🧩 Pattern Fixer"
]

selected_tab = st.radio("Activities", tabs, horizontal=True, label_visibility="collapsed")
st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# HELPER: GROQ VISION CALL
# =========================================================
def ask_groq_vision(image, prompt):
    if not groq_available or client is None:
        return None, "Groq API key not provided."
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
# 1. DICE COUNT
# =========================================================
if selected_tab == "🎲 Dice Count":
    st.markdown("### 🎲 Dice Dot Counter")
    st.markdown("Count every dot on every die in the picture! Easy for you — almost impossible for a computer.")

    def gen_dice():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        total = 0
        for cx, cy in [(40, 40), (180, 50), (90, 140), (230, 130)]:
            val = random.randint(1, 6)
            total += val
            draw.rectangle([cx, cy, cx+70, cy+70], fill="#ffffff", outline="#cbd5e1", width=3)
            dot = 6
            if val in [1, 3, 5]: draw.ellipse([cx+32, cy+32, cx+32+dot, cy+32+dot], fill="#142957")
            if val >= 2:
                draw.ellipse([cx+12, cy+12, cx+12+dot, cy+12+dot], fill="#142957")
                draw.ellipse([cx+48, cy+48, cx+48+dot, cy+48+dot], fill="#142957")
            if val >= 4:
                draw.ellipse([cx+48, cy+12, cx+48+dot, cy+12+dot], fill="#142957")
                draw.ellipse([cx+12, cy+48, cx+12+dot, cy+12+dot], fill="#142957")
            if val == 6:
                draw.ellipse([cx+12, cy+30, cx+12+dot, cy+30+dot], fill="#142957")
                draw.ellipse([cx+48, cy+30, cx+48+dot, cy+30+dot], fill="#142957")
        return total, img

    if st.session_state.dice_image is None:
        st.session_state.dice_total, st.session_state.dice_image = gen_dice()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="human-box"><b>👤 Your Turn</b>', unsafe_allow_html=True)
        st.image(st.session_state.dice_image, use_container_width=True)
        guess = st.number_input("Total dots?", 1, 30, 10, key="d_in")
        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Check Answer", key="d_chk", use_container_width=True):
                st.session_state.rounds += 1
                if int(guess) == st.session_state.dice_total:
                    st.session_state.human_score += 1
                    st.session_state.dice_result = ("correct", f"Correct! Total dots were {st.session_state.dice_total}.")
                else:
                    st.session_state.dice_result = ("wrong", f"Incorrect! Total dots were {st.session_state.dice_total}.")
        with colB:
            if st.button("🔄 New Dice", key="d_new", use_container_width=True):
                st.session_state.dice_total, st.session_state.dice_image = gen_dice()
                st.session_state.dice_result = ""
                st.rerun()
        if st.session_state.dice_result:
            t, m = st.session_state.dice_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ai-box"><b>🤖 AI's Turn</b><p>Can AI count every dot correctly?</p>', unsafe_allow_html=True)
        if st.button("Ask AI to Count 🤖", key="d_ai", use_container_width=True):
            with st.spinner("AI counting..."):
                ans, err = ask_groq_vision(st.session_state.dice_image, "Count exact total number of dots on all dice. Return ONLY integer.")
                if err: st.error(err)
                else:
                    st.info(f"AI Output: {ans}")
                    if str(st.session_state.dice_total) in ans:
                        st.session_state.ai_score += 1
                        st.success("AI got it right!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 2. HIDDEN WORD
# =========================================================
elif selected_tab == "🔤 Hidden Word":
    st.markdown("### 🔤 Warped Word Reader")
    st.markdown("Read the wiggly, wobbly letters hiding in the noisy picture!")

    def gen_word():
        text = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        for _ in range(12):
            draw.line([random.randint(0,420), random.randint(0,260), random.randint(0,420), random.randint(0,260)], fill="#94a3b8", width=2)
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        except: font = ImageFont.load_default()
        x = 60
        for char in text:
            draw.text((x, random.randint(80, 110)), char, fill=random.choice(["#142957", "#c53c54", "#17815a"]), font=font)
            x += 75
        return text, img

    if st.session_state.word_image is None:
        st.session_state.word_text, st.session_state.word_image = gen_word()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="human-box"><b>👤 Your Turn</b>', unsafe_allow_html=True)
        st.image(st.session_state.word_image, use_container_width=True)
        u_w = st.text_input("Type letters you see:", key="w_in")
        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Check Word", key="w_chk", use_container_width=True):
                st.session_state.rounds += 1
                if u_w.strip().upper() == st.session_state.word_text:
                    st.session_state.human_score += 1
                    st.session_state.word_result = ("correct", "Spot on! Great reading.")
                else:
                    st.session_state.word_result = ("wrong", f"Incorrect! Word was {st.session_state.word_text}.")
        with colB:
            if st.button("🔄 New Word", key="w_new", use_container_width=True):
                st.session_state.word_text, st.session_state.word_image = gen_word()
                st.session_state.word_result = ""
                st.rerun()
        if st.session_state.word_result:
            t, m = st.session_state.word_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ai-box"><b>🤖 AI's Turn</b><p>Can AI read through noise?</p>', unsafe_allow_html=True)
        if st.button("Ask AI to Read 🤖", key="w_ai", use_container_width=True):
            with st.spinner("AI reading..."):
                ans, err = ask_groq_vision(st.session_state.word_image, "Read 4 characters hidden behind scribble lines. Return ONLY the 4 characters.")
                if err: st.error(err)
                else:
                    st.info(f"AI Output: {ans}")
                    if st.session_state.word_text in ans.upper():
                        st.session_state.ai_score += 1
                        st.success("AI read correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 3. CLICK IN ORDER
# =========================================================
elif selected_tab == "🔢 Click in Order":
    st.markdown("### 🔢 Click-in-Order Challenge")
    st.markdown("Find the numbers 1 through 5 hiding in the picture, then list them in order!")

    def gen_order():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        nums = [1, 2, 3, 4, 5]
        random.shuffle(nums)
        coords = [(60, 60), (220, 40), (120, 150), (280, 140), (50, 180)]
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        except: font = ImageFont.load_default()
        for idx, n in enumerate(nums):
            px, py = coords[idx]
            draw.rectangle([px, py, px+55, py+55], fill="#ffffff", outline="#153e8c", width=2)
            draw.text((px+15, py+8), str(n), fill="#153e8c", font=font)
        return nums, img

    if st.session_state.order_image is None:
        st.session_state.order_sequence, st.session_state.order_image = gen_order()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="human-box"><b>👤 Your Turn</b>', unsafe_allow_html=True)
        st.image(st.session_state.order_image, use_container_width=True)
        u_seq = st.text_input("Type numbers in order (e.g. 1,2,3,4,5):", key="o_in")
        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Verify Order", key="o_chk", use_container_width=True):
                st.session_state.rounds += 1
                correct_str = ",".join(map(str, sorted(st.session_state.order_sequence)))
                if u_seq.replace(" ", "") == correct_str:
                    st.session_state.human_score += 1
                    st.session_state.order_result = ("correct", "Correct sequence order!")
                else:
                    st.session_state.order_result = ("wrong", f"Incorrect! Order was {correct_str}.")
        with colB:
            if st.button("🔄 New Puzzle", key="o_new", use_container_width=True):
                st.session_state.order_sequence, st.session_state.order_image = gen_order()
                st.session_state.order_result = ""
                st.rerun()
        if st.session_state.order_result:
            t, m = st.session_state.order_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ai-box"><b>🤖 AI's Turn</b><p>Can AI find order?</p>', unsafe_allow_html=True)
        if st.button("Ask AI to Find Order 🤖", key="o_ai", use_container_width=True):
            with st.spinner("AI analyzing..."):
                ans, err = ask_groq_vision(st.session_state.order_image, "List all numbers in ascending order separated by commas.")
                if err: st.error(err)
                else:
                    st.info(f"AI Output: {ans}")
                    if "1,2,3,4,5" in ans.replace(" ", ""):
                        st.session_state.ai_score += 1
                        st.success("AI ordered correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 4. DON'T BE FOOLED
# =========================================================
elif selected_tab == "😲 Don't Be Fooled":
    st.markdown("### 😲 Don't Be Fooled Challenge")
    st.markdown("Spot the trick question where computers get confused.")

    def gen_fool():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        draw.ellipse([80, 70, 160, 150], fill="#c53c54")
        draw.rectangle([220, 70, 300, 150], fill="#153e8c")
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        except: font = ImageFont.load_default()
        draw.text((70, 180), "How many circles?", fill="#153e8c", font=font)
        return "1", img

    if st.session_state.fool_image is None:
        st.session_state.fool_ans, st.session_state.fool_image = gen_fool()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="human-box"><b>👤 Your Turn</b>', unsafe_allow_html=True)
        st.image(st.session_state.fool_image, use_container_width=True)
        choice = st.radio("Select answer:", ["1 Circle, 1 Square", "2 Circles", "2 Squares"], key="f_rad")
        if st.button("✅ Submit", key="f_chk", use_container_width=True):
            st.session_state.rounds += 1
            if choice == "1 Circle, 1 Square":
                st.session_state.human_score += 1
                st.session_state.fool_result = ("correct", "Great job not getting fooled!")
            else:
                st.session_state.fool_result = ("wrong", "Fooled! There is 1 circle and 1 square.")
        if st.session_state.fool_result:
            t, m = st.session_state.fool_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ai-box"><b>🤖 AI's Turn</b><p>Will AI hallucinate shapes?</p>', unsafe_allow_html=True)
        if st.button("Ask AI to Analyze 🤖", key="f_ai", use_container_width=True):
            with st.spinner("AI inspecting..."):
                ans, err = ask_groq_vision(st.session_state.fool_image, "How many circles and how many squares are in this image?")
                if err: st.error(err)
                else: st.info(f"AI Output: {ans}")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 5. ANIMAL GRID
# =========================================================
elif selected_tab == "🐾 Animal Grid":
    st.markdown("### 🐾 Animal / Symbol Grid")
    st.markdown("Count specific target icons in the grid.")

    def gen_grid():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        target = "★"
        actual = 0
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        except: font = ImageFont.load_default()
        for r in range(3):
            for c in range(4):
                sym = random.choice(["★", "■", "▲", "●"])
                if sym == target: actual += 1
                draw.text((60 + c*80, 40 + r*70), sym, fill="#153e8c", font=font)
        return actual, target, img

    if st.session_state.animal_image is None:
        st.session_state.animal_count, st.session_state.animal_target, st.session_state.animal_image = gen_grid()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="human-box"><b>👤 Your Turn</b>', unsafe_allow_html=True)
        st.image(st.session_state.animal_image, use_container_width=True)
        u_cnt = st.number_input(f"Count stars ('{st.session_state.animal_target}'):", 0, 12, 2, key="g_in")
        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Check Grid", key="g_chk", use_container_width=True):
                st.session_state.rounds += 1
                if int(u_cnt) == st.session_state.animal_count:
                    st.session_state.human_score += 1
                    st.session_state.animal_result = ("correct", f"Correct! There were {st.session_state.animal_count} stars.")
                else:
                    st.session_state.animal_result = ("wrong", f"Incorrect! There were actually {st.session_state.animal_count} stars.")
        with colB:
            if st.button("🔄 New Grid", key="g_new", use_container_width=True):
                st.session_state.animal_count, st.session_state.animal_target, st.session_state.animal_image = gen_grid()
                st.session_state.animal_result = ""
                st.rerun()
        if st.session_state.animal_result:
            t, m = st.session_state.animal_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ai-box"><b>🤖 AI's Turn</b><p>Can AI count grid items?</p>', unsafe_allow_html=True)
        if st.button("Ask AI to Count Grid 🤖", key="g_ai", use_container_width=True):
            with st.spinner("AI counting..."):
                ans, err = ask_groq_vision(st.session_state.animal_image, f"Count how many star symbols ('{st.session_state.animal_target}') are in this grid. Return count number.")
                if err: st.error(err)
                else:
                    st.info(f"AI Output: {ans}")
                    if str(st.session_state.animal_count) in ans:
                        st.session_state.ai_score += 1
                        st.success("AI counted correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 6. PATTERN FIXER
# =========================================================
elif selected_tab == "🧩 Pattern Fixer":
    st.markdown("### 🧩 Pattern Fixer")
    st.markdown("Look at shapes in a row, figure out the repeating pattern, and select what comes next!")

    def gen_pattern():
        pat = ["Circle", "Square", "Triangle"]
        target = pat[0]
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        except: font = ImageFont.load_default()
        for idx, s in enumerate(pat + [target]):
            draw.rectangle([30 + idx*80, 60, 95 + idx*80, 125], fill="#ffffff", outline="#dce7f5", width=2)
            draw.text((45 + idx*80, 85), s[:3], fill="#153e8c", font=font)
        return target, img

    if st.session_state.pattern_image is None:
        st.session_state.pattern_target, st.session_state.pattern_image = gen_pattern()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="human-box"><b>👤 Your Turn</b>', unsafe_allow_html=True)
        st.image(st.session_state.pattern_image, use_container_width=True)
        choice = st.selectbox("Which shape comes next?", ["Circle", "Square", "Triangle"], key="p_sel")
        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Check Pattern", key="p_chk", use_container_width=True):
                st.session_state.rounds += 1
                if choice == st.session_state.pattern_target:
                    st.session_state.human_score += 1
                    st.session_state.pattern_result = ("correct", "Correct! Pattern spotted.")
                else:
                    st.session_state.pattern_result = ("wrong", f"Incorrect! Next shape was {st.session_state.pattern_target}.")
        with colB:
            if st.button("🔄 New Pattern", key="p_new", use_container_width=True):
                st.session_state.pattern_target, st.session_state.pattern_image = gen_pattern()
                st.session_state.pattern_result = ""
                st.rerun()
        if st.session_state.pattern_result:
            t, m = st.session_state.pattern_result
            st.success(m) if t == "correct" else st.error(m)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="ai-box"><b>🤖 AI's Turn</b><p>Can AI solve sequence logic?</p>', unsafe_allow_html=True)
        if st.button("Ask AI to Solve Pattern 🤖", key="p_ai", use_container_width=True):
            with st.spinner("AI analyzing pattern..."):
                ans, err = ask_groq_vision(st.session_state.pattern_image, "What shape comes next in this repeating sequence? Return shape name.")
                if err: st.error(err)
                else:
                    st.info(f"AI Output: {ans}")
                    if st.session_state.pattern_target.lower() in ans.lower():
                        st.session_state.ai_score += 1
                        st.success("AI solved pattern correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        🤖 <b>Can AI Beat You?</b> — Multi-Activity Challenge Suite<br><br>
        <b>CF Name:</b> Jahangeer Ali &nbsp; | &nbsp; <b>ID:</b> MRBICF2003<br>
        Built with Python, Streamlit, and Groq Vision AI
    </div>
    """,
    unsafe_allow_html=True
)
