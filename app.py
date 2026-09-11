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
    page_title="Can AI Beat You? | Multi-Activity Human vs AI Challenge",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS & STYLING (Matching Screenshot UI)
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f4f8fb 0%, #ffffff 50%, #fef7ed 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .top-header {
        background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
        padding: 18px 28px;
        border-radius: 16px;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .brand {
        font-size: 24px;
        font-weight: 800;
    }
    
    .student-info {
        font-size: 14px;
        font-weight: 600;
        background: rgba(255, 255, 255, 0.15);
        padding: 5px 14px;
        border-radius: 20px;
        backdrop-filter: blur(5px);
    }

    .card {
        background: white;
        border: 1px solid #d9e2ec;
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 6px 18px rgba(16, 42, 67, 0.05);
        margin-bottom: 15px;
    }

    .human-box {
        background: #f0fff4;
        border: 2px solid #9ae6b4;
        border-radius: 18px;
        padding: 24px;
    }

    .ai-box {
        background: #fff5f5;
        border: 2px solid #feb2b2;
        border-radius: 18px;
        padding: 24px;
    }

    .score-card {
        background: white;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        border: 1px solid #d9e2ec;
        box-shadow: 0 4px 12px rgba(16, 42, 67, 0.04);
    }

    .score-number {
        font-size: 38px;
        font-weight: 900;
        color: #0f2027;
        margin: 5px 0;
    }

    .score-label {
        font-weight: 700;
        color: #627d98;
        font-size: 13px;
        text-transform: uppercase;
    }

    .footer {
        background: #0f2027;
        color: white;
        text-align: center;
        padding: 20px;
        border-radius: 16px;
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
    "active_tab": "Dice Count",
    # Dice Count state
    "dice_image": None,
    "dice_total": 0,
    "dice_result": "",
    # Hidden Word state
    "word_image": None,
    "word_text": "",
    "word_result": "",
    # Click in Order state
    "order_image": None,
    "order_sequence": [],
    "order_result": "",
    # Don't Be Fooled state
    "fool_image": None,
    "fool_ans": "",
    "fool_result": "",
    # Animal Grid state
    "animal_image": None,
    "animal_count": 0,
    "animal_result": "",
    # Pattern Fixer state
    "pattern_image": None,
    "pattern_target": "",
    "pattern_result": ""
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# =========================================================
# SIDEBAR - CONFIGURATION & NAV
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Groq AI Configuration")
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
    st.markdown("### 👨‍🎓 Developer Info")
    st.markdown("**CF Name:** Jahangeer Ali")
    st.markdown("**ID:** MRBICF2003")
    st.markdown("---")
    st.info("💡 Select different challenges from the top navigation menu to test Human vs AI capabilities!")

client = None
groq_available = False
if api_key_input:
    try:
        client = Groq(api_key=api_key_input)
        groq_available = True
    except Exception:
        pass

# =========================================================
# HEADER SECTION
# =========================================================
st.markdown(
    """
    <div class="top-header">
        <div class="brand">🤖 Can AI Beat You? — Challenge Suite</div>
        <div class="student-info">CF Name: Jahangeer Ali &nbsp;|&nbsp; ID: MRBICF2003</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# TOP NAVIGATION PILLS
# =========================================================
tabs = [
    "🎲 Dice Count", 
    "🔤 Hidden Word", 
    "🔢 Click in Order", 
    "😲 Don't Be Fooled", 
    "🐾 Animal Grid", 
    "🧩 Pattern Fixer"
]

selected_tab = st.radio("Select Challenge", tabs, horizontal=True, label_visibility="collapsed")
st.session_state.active_tab = selected_tab
st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# HELPER: AI VISION SOLVER FUNCTION
# =========================================================
def ask_groq_vision(image, prompt_text):
    if not groq_available or client is None:
        return None, "Groq API key not configured in sidebar."
    try:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]
                }
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip(), None
    except Exception as e:
        return None, str(e)


# =========================================================
# ACTIVITY 1: DICE COUNT
# =========================================================
if selected_tab == "🎲 Dice Count":
    st.markdown("### 🎲 Dice Dot Counter")
    st.markdown("Count every dot on every die in the picture! Easy for you — almost impossible for a computer.")

    def gen_dice():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        total_dots = 0
        
        # Draw 4 random dice
        coords = [(40, 40), (180, 50), (90, 140), (230, 130)]
        for cx, cy in coords:
            val = random.randint(1, 6)
            total_dots += val
            # Dice box
            draw.rectangle([cx, cy, cx+70, cy+70], fill="#ffffff", outline="#cbd5e1", width=3)
            # Draw dots
            dot_r = 6
            if val in [1, 3, 5]: # center
                draw.ellipse([cx+32, cy+32, cx+32+dot_r*2, cy+32+dot_r*2], fill="#0f2027")
            if val >= 2: # top-left & bottom-right
                draw.ellipse([cx+12, cy+12, cx+12+dot_r*2, cy+12+dot_r*2], fill="#0f2027")
                draw.ellipse([cx+48, cy+48, cx+48+dot_r*2, cy+48+dot_r*2], fill="#0f2027")
            if val >= 4: # top-right & bottom-left
                draw.ellipse([cx+48, cy+12, cx+48+dot_r*2, cy+12+dot_r*2], fill="#0f2027")
                draw.ellipse([cx+12, cy+48, cx+12+dot_r*2, cy+12+dot_r*2], fill="#0f2027")
            if val == 6: # middle sides
                draw.ellipse([cx+12, cy+30, cx+12+dot_r*2, cy+30+dot_r*2], fill="#0f2027")
                draw.ellipse([cx+48, cy+30, cx+48+dot_r*2, cy+30+dot_r*2], fill="#0f2027")
        return total_dots, img

    if st.session_state.dice_image is None:
        st.session_state.dice_total, st.session_state.dice_image = gen_dice()

    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        st.markdown('<div class="human-box">', unsafe_allow_html=True)
        st.markdown("<b>👤 Your Turn</b>", unsafe_allow_html=True)
        st.image(st.session_state.dice_image, use_container_width=True)
        user_guess = st.number_input("How many total dots?", min_value=1, max_value=30, value=10, key="dice_input")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Check Answer", key="dice_check", use_container_width=True):
                st.session_state.rounds += 1
                if int(user_guess) == st.session_state.dice_total:
                    st.session_state.human_score += 1
                    st.session_state.dice_result = ("correct", f"Correct! Total dots were {st.session_state.dice_total}.")
                else:
                    st.session_state.dice_result = ("wrong", f"Incorrect! Total dots were {st.session_state.dice_total}.")
        with col2:
            if st.button("🔄 New Dice", key="dice_new", use_container_width=True):
                st.session_state.dice_total, st.session_state.dice_image = gen_dice()
                st.session_state.dice_result = ""
                st.rerun()

        if st.session_state.dice_result:
            rtype, rmsg = st.session_state.dice_result
            if rtype == "correct": st.success(rmsg)
            else: st.error(rmsg)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("<b>🤖 AI's Turn</b>", unsafe_allow_html=True)
        st.write("Can Groq Vision accurately count every single dot across the dice?")
        if st.button("Ask AI to Count 🤖", key="dice_ai", use_container_width=True):
            with st.spinner("AI is counting dots..."):
                ans, err = ask_groq_vision(st.session_state.dice_image, "Count the exact total number of black dots on all dice in this image. Return ONLY the integer number.")
                if err:
                    st.error(err)
                else:
                    st.info(f"AI Response: {ans}")
                    if str(st.session_state.dice_total) in ans:
                        st.session_state.ai_score += 1
                        st.success("AI got it right!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIVITY 2: HIDDEN WORD
# =========================================================
elif selected_tab == "🔤 Hidden Word":
    st.markdown("### 🔤 Warped Word Reader")
    st.markdown("Read the wiggly, wobbly characters hiding in the noisy picture!")

    def gen_word():
        text = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        # Noise lines
        for _ in range(15):
            draw.line([random.randint(0,420), random.randint(0,260), random.randint(0,420), random.randint(0,260)], fill="#94a3b8", width=2)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        x = 60
        for char in text:
            draw.text((x, random.randint(80, 120)), char, fill=random.choice(["#1e293b", "#0284c7", "#dc2626", "#16a34a"]), font=font)
            x += 75
        return text, img

    if st.session_state.word_image is None:
        st.session_state.word_text, st.session_state.word_image = gen_word()

    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        st.markdown('<div class="human-box">', unsafe_allow_html=True)
        st.markdown("<b>👤 Your Turn</b>", unsafe_allow_html=True)
        st.image(st.session_state.word_image, use_container_width=True)
        u_word = st.text_input("Type the 4 characters you see:", key="word_input")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Check Word", key="word_chk", use_container_width=True):
                st.session_state.rounds += 1
                if u_word.strip().upper() == st.session_state.word_text:
                    st.session_state.human_score += 1
                    st.session_state.word_result = ("correct", "Spot on! Perfect reading.")
                else:
                    st.session_state.word_result = ("wrong", f"Incorrect! Word was {st.session_state.word_text}.")
        with col2:
            if st.button("🔄 New Word", key="word_new", use_container_width=True):
                st.session_state.word_text, st.session_state.word_image = gen_word()
                st.session_state.word_result = ""
                st.rerun()

        if st.session_state.word_result:
            rtype, rmsg = st.session_state.word_result
            if rtype == "correct": st.success(rmsg)
            else: st.error(rmsg)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("<b>🤖 AI's Turn</b>", unsafe_allow_html=True)
        st.write("Can AI read through the messy noise lines to find the characters?")
        if st.button("Ask AI to Read 🤖", key="word_ai", use_container_width=True):
            with st.spinner("AI is reading..."):
                ans, err = ask_groq_vision(st.session_state.word_image, "Read the 4 characters hidden behind the scribble lines in this image. Return ONLY the 4 characters.")
                if err: st.error(err)
                else:
                    st.info(f"AI Response: {ans}")
                    if st.session_state.word_text in ans.upper():
                        st.session_state.ai_score += 1
                        st.success("AI read it correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIVITY 3: CLICK IN ORDER
# =========================================================
elif selected_tab == "🔢 Click in Order":
    st.markdown("### 🔢 Click-in-Order Challenge")
    st.markdown("Find numbers 1 through 5 in the picture and verify your mental sequence order.")

    def gen_order():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        nums = [1, 2, 3, 4, 5]
        random.shuffle(nums)
        positions = [(60, 60), (220, 40), (120, 150), (280, 140), (50, 180)]
        
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        except: font = ImageFont.load_default()

        for idx, n in enumerate(nums):
            px, py = positions[idx]
            draw.rectangle([px, py, px+55, py+55], fill="#ffffff", outline="#3b82f6", width=2)
            draw.text((px+15, py+8), str(n), fill="#1e293b", font=font)
        return nums, img

    if st.session_state.order_image is None:
        st.session_state.order_sequence, st.session_state.order_image = gen_order()

    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        st.markdown('<div class="human-box">', unsafe_allow_html=True)
        st.markdown("<b>👤 Your Turn</b>", unsafe_allow_html=True)
        st.image(st.session_state.order_image, use_container_width=True)
        st.write(f"Numbers present in image (shuffled): {sorted(st.session_state.order_sequence)}")
        user_seq = st.text_input("Type numbers in ascending order (e.g. 1,2,3,4,5):", key="order_input")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Verify Order", key="order_chk", use_container_width=True):
                st.session_state.rounds += 1
                correct_str = ",".join(map(str, sorted(st.session_state.order_sequence)))
                cleaned_user = user_seq.replace(" ", "")
                if cleaned_user == correct_str.replace(" ", ""):
                    st.session_state.human_score += 1
                    st.session_state.order_result = ("correct", "Correct sequence order!")
                else:
                    st.session_state.order_result = ("wrong", f"Incorrect! Correct order was {correct_str}.")
        with col2:
            if st.button("🔄 New Puzzle", key="order_new", use_container_width=True):
                st.session_state.order_sequence, st.session_state.order_image = gen_order()
                st.session_state.order_result = ""
                st.rerun()

        if st.session_state.order_result:
            rtype, rmsg = st.session_state.order_result
            if rtype == "correct": st.success(rmsg)
            else: st.error(rmsg)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("<b>🤖 AI's Turn</b>", unsafe_allow_html=True)
        st.write("Can AI scan coordinates and list numbers 1 to 5 in correct ascending sequence?")
        if st.button("Ask AI to Sort 🤖", key="order_ai", use_container_width=True):
            with st.spinner("AI is analyzing spatial order..."):
                ans, err = ask_groq_vision(st.session_state.order_image, "Find all numbers in this image and list them in ascending numerical order separated by commas.")
                if err: st.error(err)
                else:
                    st.info(f"AI Response: {ans}")
                    if "1,2,3,4,5" in ans.replace(" ", ""):
                        st.session_state.ai_score += 1
                        st.success("AI ordered correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIVITY 4: DON'T BE FOOLED
# =========================================================
elif selected_tab == "😲 Don't Be Fooled":
    st.markdown("### 😲 Don't Be Fooled Challenge")
    st.markdown("Spot the trick question / optical oddity where computers easily get misled!")

    def gen_fool():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        # Draw misleading visual shapes
        draw.ellipse([80, 70, 160, 150], fill="#e11d48")
        draw.rectangle([220, 70, 300, 150], fill="#0284c7")
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        except: font = ImageFont.load_default()
        draw.text((70, 180), "How many circles?", fill="#1e293b", font=font)
        return "1", img

    if st.session_state.fool_image is None:
        st.session_state.fool_ans, st.session_state.fool_image = gen_fool()

    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        st.markdown('<div class="human-box">', unsafe_allow_html=True)
        st.markdown("<b>👤 Your Turn</b>", unsafe_allow_html=True)
        st.image(st.session_state.fool_image, use_container_width=True)
        ans_choice = st.radio("Select correct answer:", ["1 Circle, 1 Square", "2 Circles", "2 Squares"], key="fool_radio")
        
        if st.button("✅ Submit Answer", key="fool_chk", use_container_width=True):
            st.session_state.rounds += 1
            if ans_choice == "1 Circle, 1 Square":
                st.session_state.human_score += 1
                st.session_state.fool_result = ("correct", "Great job not getting fooled!")
            else:
                st.session_state.fool_result = ("wrong", "Fooled! There is 1 circle and 1 square.")

        if st.session_state.fool_result:
            rtype, rmsg = st.session_state.fool_result
            if rtype == "correct": st.success(rmsg)
            else: st.error(rmsg)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("<b>🤖 AI's Turn</b>", unsafe_allow_html=True)
        st.write("Does the AI hallucinate shapes or answer correctly?")
        if st.button("Ask AI to Analyze 🤖", key="fool_ai", use_container_width=True):
            with st.spinner("AI is inspecting..."):
                ans, err = ask_groq_vision(st.session_state.fool_image, "How many circles and how many squares are in this image?")
                if err: st.error(err)
                else: st.info(f"AI Response: {ans}")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIVITY 5: ANIMAL GRID
# =========================================================
elif selected_tab == "🐾 Animal Grid":
    st.markdown("### 🐾 Animal / Symbol Grid")
    st.markdown("Count specific target icons in the grid.")

    def gen_grid():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        target_count = random.randint(2, 5)
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        except: font = ImageFont.load_default()
        
        symbols = ["★", "■", "▲", "●"]
        target = "★"
        actual = 0
        
        for r in range(3):
            for c in range(4):
                sym = random.choice(symbols)
                if sym == target: actual += 1
                draw.text((60 + c*80, 40 + r*70), sym, fill="#0f2027", font=font)
        return actual, target, img

    if st.session_state.animal_image is None:
        st.session_state.animal_count, st.session_state.animal_target, st.session_state.animal_image = gen_grid()

    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        st.markdown('<div class="human-box">', unsafe_allow_html=True)
        st.markdown("<b>👤 Your Turn</b>", unsafe_allow_html=True)
        st.image(st.session_state.animal_image, use_container_width=True)
        u_count = st.number_input(f"Count how many stars ('{st.session_state.animal_target}') appear in the grid:", min_value=0, max_value=12, value=2, key="grid_inp")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Check Grid", key="grid_chk", use_container_width=True):
                st.session_state.rounds += 1
                if int(u_count) == st.session_state.animal_count:
                    st.session_state.human_score += 1
                    st.session_state.animal_result = ("correct", f"Correct! There were {st.session_state.animal_count} stars.")
                else:
                    st.session_state.animal_result = ("wrong", f"Incorrect! There were actually {st.session_state.animal_count} stars.")
        with col2:
            if st.button("🔄 New Grid", key="grid_new", use_container_width=True):
                st.session_state.animal_count, st.session_state.animal_target, st.session_state.animal_image = gen_grid()
                st.session_state.animal_result = ""
                st.rerun()

        if st.session_state.animal_result:
            rtype, rmsg = st.session_state.animal_result
            if rtype == "correct": st.success(rmsg)
            else: st.error(rmsg)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("<b>🤖 AI's Turn</b>", unsafe_allow_html=True)
        st.write(f"Can AI count all occurrences of '{st.session_state.animal_target}'?")
        if st.button("Ask AI to Count Grid 🤖", key="grid_ai", use_container_width=True):
            with st.spinner("AI counting grid..."):
                ans, err = ask_groq_vision(st.session_state.animal_image, f"Count how many star symbols ('{st.session_state.animal_target}') are present in this grid. Return the exact count number.")
                if err: st.error(err)
                else:
                    st.info(f"AI Response: {ans}")
                    if str(st.session_state.animal_count) in ans:
                        st.session_state.ai_score += 1
                        st.success("AI counted correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# ACTIVITY 6: PATTERN FIXER
# =========================================================
elif selected_tab == "🧩 Pattern Fixer":
    st.markdown("### 🧩 Pattern Fixer")
    st.markdown("Look at the shapes in a row, figure out the repeating pattern, and select what comes next!")

    def gen_pattern():
        img = Image.new("RGB", (420, 260), "#f8fafc")
        draw = ImageDraw.Draw(img)
        shapes = ["Circle", "Square", "Triangle"]
        pat = [random.choice(shapes), random.choice(shapes), random.choice(shapes)]
        target = pat[0] # repeating
        
        try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        except: font = ImageFont.load_default()

        # Draw sequence
        full_seq = pat + [target]
        for idx, s in enumerate(full_seq):
            draw.rectangle([30 + idx*80, 60, 95 + idx*80, 125], fill="#ffffff", outline="#cbd5e1", width=2)
            draw.text((45 + idx*80, 85), s[:3], fill="#0f2027", font=font)
        return target, img

    if st.session_state.pattern_image is None:
        st.session_state.pattern_target, st.session_state.pattern_image = gen_pattern()

    c_left, c_right = st.columns(2, gap="large")
    with c_left:
        st.markdown('<div class="human-box">', unsafe_allow_html=True)
        st.markdown("<b>👤 Your Turn</b>", unsafe_allow_html=True)
        st.image(st.session_state.pattern_image, use_container_width=True)
        choice = st.selectbox("Which shape comes next in the repeating sequence?", ["Circle", "Square", "Triangle"], key="pat_sel")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Check Pattern", key="pat_chk", use_container_width=True):
                st.session_state.rounds += 1
                if choice == st.session_state.pattern_target:
                    st.session_state.human_score += 1
                    st.session_state.pattern_result = ("correct", "Correct! You spotted the repeating pattern.")
                else:
                    st.session_state.pattern_result = ("wrong", f"Incorrect! Next shape was {st.session_state.pattern_target}.")
        with col2:
            if st.button("🔄 New Pattern", key="pat_new", use_container_width=True):
                st.session_state.pattern_target, st.session_state.pattern_image = gen_pattern()
                st.session_state.pattern_result = ""
                st.rerun()

        if st.session_state.pattern_result:
            rtype, rmsg = st.session_state.pattern_result
            if rtype == "correct": st.success(rmsg)
            else: st.error(rmsg)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_right:
        st.markdown('<div class="ai-box">', unsafe_allow_html=True)
        st.markdown("<b>🤖 AI's Turn</b>", unsafe_allow_html=True)
        st.write("Can AI analyze sequence logic and predict the missing shape?")
        if st.button("Ask AI to Solve Pattern 🤖", key="pat_ai", use_container_width=True):
            with st.spinner("AI analyzing pattern..."):
                ans, err = ask_groq_vision(st.session_state.pattern_image, "What shape comes next in this repeating sequence? Return the shape name.")
                if err: st.error(err)
                else:
                    st.info(f"AI Response: {ans}")
                    if st.session_state.pattern_target.lower() in ans.lower():
                        st.session_state.ai_score += 1
                        st.success("AI solved pattern correctly!")
        st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# LIVE GLOBAL SCOREBOARD SUMMARY
# =========================================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="card"><h3>📊 Global Session Scoreboard</h3></div>', unsafe_allow_html=True)
sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown(f'<div class="score-card"><div style="color:#107c41; font-weight:800;">👤 HUMAN SCORE</div><div class="score-number">{st.session_state.human_score}</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="score-card"><div style="color:#d64545; font-weight:800;">🤖 AI SCORE</div><div class="score-number">{st.session_state.ai_score}</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown(f'<div class="score-card"><div style="color:#b7791f; font-weight:800;">🎮 TOTAL ROUNDS</div><div class="score-number">{st.session_state.rounds}</div></div>', unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="footer">
        🤖 <b>Can AI Beat You? — Multi-Activity Challenge Suite</b><br><br>
        <b>CF Name:</b> Jahangeer Ali &nbsp;|&nbsp; <b>ID:</b> MRBICF2003<br>
        Built with Python, Streamlit, and Groq Vision AI
    </div>
    """,
    unsafe_allow_html=True
)
