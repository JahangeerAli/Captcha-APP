import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from groq import Groq
import random
import string
import io
import base64
import re


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Can AI Beat You?",
    page_icon="🧠",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7f8fc;
}

.top-box {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 20px 25px;
    border-radius: 15px;
    color: white;
    margin-bottom: 20px;
}

.title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    opacity: 0.95;
}

.info-box {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    margin-bottom: 15px;
}

.score-human {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

.score-ai {
    background-color: #fff3e0;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 20px;
    font-weight: bold;
}

.challenge-box {
    background-color: white;
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #dddddd;
    margin-top: 15px;
}

.footer {
    text-align: center;
    color: gray;
    margin-top: 40px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SESSION STATE
# =========================================================

if "human_score" not in st.session_state:
    st.session_state.human_score = 0

if "ai_score" not in st.session_state:
    st.session_state.ai_score = 0

if "round_count" not in st.session_state:
    st.session_state.round_count = 0

if "captcha_text" not in st.session_state:
    st.session_state.captcha_text = None

if "animal_grid" not in st.session_state:
    st.session_state.animal_grid = None

if "selected_animals" not in st.session_state:
    st.session_state.selected_animals = []

if "message" not in st.session_state:
    st.session_state.message = ""


# =========================================================
# SIDEBAR - API KEY
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    st.subheader("Groq API Key")

    api_key = st.text_input(
        "Paste your Groq API key:",
        type="password",
        placeholder="gsk_...",
        help="Your API key is used only for this Streamlit session."
    )

    st.caption(
        "🔐 Do not put your API key directly inside app.py or GitHub."
    )

    st.divider()

    st.subheader("AI Model")

    st.code("qwen/qwen3.6-27b")

    st.caption(
        "This model supports image/vision input."
    )

    st.divider()

    if st.button("🧪 Test API Key", use_container_width=True):

        if not api_key.strip():
            st.warning("Please paste your Groq API key first.")

        else:
            try:
                client = Groq(api_key=api_key.strip())

                response = client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=[
                        {
                            "role": "user",
                            "content": "Reply with only: API WORKING"
                        }
                    ],
                    max_tokens=20
                )

                st.success("✅ API Key is working!")

            except Exception as e:
                st.error("❌ API Key / API request failed.")
                st.caption(str(e))

    st.divider()

    if st.button("🔄 Reset Scores", use_container_width=True):

        st.session_state.human_score = 0
        st.session_state.ai_score = 0
        st.session_state.round_count = 0
        st.session_state.message = ""

        st.success("Scores reset!")

        st.rerun()


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="top-box">

<div class="title">
🧠 Can AI Beat You?
</div>

<div class="subtitle">
Play fun challenges that are easy for humans but difficult for AI.
Let's discover whether human intelligence can beat artificial intelligence!
</div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# USER / PROJECT INFORMATION
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="info-box">
    <b>CF Name:</b><br>
    Jahangeer Ali
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
    <b>ID:</b><br>
    MRBICF2003
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="info-box">
    <b>Project:</b><br>
    Human vs AI Challenge
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# SCOREBOARD
# =========================================================

st.subheader("🏆 Scoreboard")

score1, score2, score3 = st.columns(3)

with score1:
    st.markdown(
        f"""
        <div class="score-human">
        👤 Human<br>
        {st.session_state.human_score}
        </div>
        """,
        unsafe_allow_html=True
    )

with score2:
    st.markdown(
        f"""
        <div class="score-ai">
        🤖 AI<br>
        {st.session_state.ai_score}
        </div>
        """,
        unsafe_allow_html=True
    )

with score3:
    st.markdown(
        f"""
        <div class="score-human">
        🎮 Rounds<br>
        {st.session_state.round_count}
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FUNCTIONS
# =========================================================

def create_captcha():

    characters = string.ascii_uppercase + string.digits

    text = "".join(
        random.choice(characters)
        for _ in range(5)
    )

    width = 450
    height = 160

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype(
            "arial.ttf",
            65
        )
    except:
        font = ImageFont.load_default()

    # Random lines
    for _ in range(8):

        x1 = random.randint(0, width)
        y1 = random.randint(0, height)

        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        draw.line(
            (x1, y1, x2, y2),
            fill=(150, 150, 150),
            width=2
        )

    # Random dots
    for _ in range(60):

        x = random.randint(0, width)
        y = random.randint(0, height)

        draw.ellipse(
            (x, y, x + 3, y + 3),
            fill=(100, 100, 100)
        )

    # CAPTCHA text
    draw.text(
        (80, 40),
        text,
        fill=(20, 20, 20),
        font=font
    )

    return image, text


def create_animal_grid():

    animals = [
        "🐱",
        "🐶",
        "🐭",
        "🐹",
        "🐰",
        "🦊",
        "🐻",
        "🐼",
        "🐨",
        "🐯",
        "🦁",
        "🐮",
        "🐷",
        "🐸",
        "🐵",
        "🐙"
    ]

    target = random.choice(
        ["🐱", "🐶", "🐰", "🐼", "🐯"]
    )

    grid = animals.copy()

    random.shuffle(grid)

    correct_indices = [
        i for i, animal in enumerate(grid)
        if animal == target
    ]

    return grid, target, correct_indices


def image_to_base64(image):

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def ask_groq_about_image(image, prompt, api_key):

    if not api_key.strip():
        return None, "Please enter your Groq API key in the sidebar."

    try:

        client = Groq(
            api_key=api_key.strip()
        )

        image_base64 = image_to_base64(image)

        response = client.chat.completions.create(

            model="qwen/qwen3.6-27b",

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

            max_tokens=200
        )

        answer = response.choices[0].message.content

        return answer, None

    except Exception as e:

        return None, str(e)


# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3 = st.tabs(
    [
        "🏠 Home",
        "🔤 Text CAPTCHA",
        "🐾 Animal Grid"
    ]
)


# =========================================================
# HOME
# =========================================================

with tab1:

    st.markdown("""
    <div class="challenge-box">

    <h2>Welcome! 👋</h2>

    <p>
    This project compares human intelligence with Artificial Intelligence.
    </p>

    <p>
    Humans solve visual challenges and Groq AI tries to solve
    the same type of challenge.
    </p>

    <h3>How it works</h3>

    <ol>
        <li>Choose a challenge.</li>
        <li>Human solves the challenge.</li>
        <li>Groq Vision AI analyzes the challenge.</li>
        <li>Human and AI results are compared.</li>
        <li>The scoreboard is updated.</li>
    </ol>

    </div>
    """, unsafe_allow_html=True)

    st.info(
        "👈 First paste your Groq API key in the sidebar."
    )


# =========================================================
# TEXT CAPTCHA
# =========================================================

with tab2:

    st.subheader("🔤 Text CAPTCHA Challenge")

    st.write(
        "Read the distorted characters and enter what you see."
    )

    if st.session_state.captcha_text is None:

        image, text = create_captcha()

        st.session_state.captcha_image = image
        st.session_state.captcha_text = text

    else:

        image = st.session_state.captcha_image
        text = st.session_state.captcha_text

    st.image(
        image,
        width=450
    )

    human_answer = st.text_input(
        "Enter the characters:",
        key="captcha_input"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "👤 Human Verify",
            use_container_width=True
        ):

            if human_answer.strip().upper() == text.upper():

                st.session_state.human_score += 1
                st.session_state.round_count += 1

                st.success(
                    "🎉 Correct! Human gets the point."
                )

            else:

                st.session_state.round_count += 1

                st.error(
                    f"❌ Incorrect. Correct answer was: {text}"
                )

    with col2:

        if st.button(
            "🤖 Ask AI",
            use_container_width=True
        ):

            if not api_key.strip():

                st.warning(
                    "Please paste your Groq API key in the sidebar."
                )

            else:

                with st.spinner(
                    "🤖 Groq AI is analyzing the CAPTCHA..."
                ):

                    prompt = """
                    This is a CAPTCHA image.

                    Read the characters carefully.

                    Return ONLY the characters you see.
                    Do not explain anything.
                    """

                    ai_answer, error = ask_groq_about_image(
                        image,
                        prompt,
                        api_key
                    )

                if error:

                    st.error(error)

                else:

                    st.write(
                        f"🤖 AI answered: **{ai_answer}**"
                    )

                    clean_ai = re.sub(
                        r"[^A-Za-z0-9]",
                        "",
                        ai_answer
                    ).upper()

                    correct = text.upper()

                    if clean_ai == correct:

                        st.session_state.ai_score += 1

                        st.success(
                            "🤖 AI solved the CAPTCHA!"
                        )

                    else:

                        st.info(
                            f"AI could not solve it correctly. "
                            f"Correct answer: {correct}"
                        )

    st.divider()

    if st.button(
        "🔄 New CAPTCHA",
        use_container_width=True
    ):

        new_image, new_text = create_captcha()

        st.session_state.captcha_image = new_image
        st.session_state.captcha_text = new_text

        st.rerun()


# =========================================================
# ANIMAL GRID
# =========================================================

with tab3:

    st.subheader("🐾 Animal Grid Challenge")

    if st.session_state.animal_grid is None:

        grid, target, correct_indices = create_animal_grid()

        st.session_state.animal_grid = grid
        st.session_state.animal_target = target
        st.session_state.animal_correct = correct_indices

    grid = st.session_state.animal_grid
    target = st.session_state.animal_target
    correct_indices = st.session_state.animal_correct

    st.info(
        f"Find all tiles containing: {target}"
    )

    # Create visual grid image for AI
    grid_image = Image.new(
        "RGB",
        (600, 600),
        "white"
    )

    draw = ImageDraw.Draw(grid_image)

    try:
        emoji_font = ImageFont.truetype(
            "seguiemj.ttf",
            55
        )
    except:
        emoji_font = ImageFont.load_default()

    for i, animal in enumerate(grid):

        row = i // 4
        col = i % 4

        x = col * 150
        y = row * 150

        draw.rectangle(
            (x + 5, y + 5, x + 145, y + 145),
            outline="black",
            width=2
        )

        draw.text(
            (x + 50, y + 40),
            animal,
            font=emoji_font,
            fill="black"
        )

        draw.text(
            (x + 10, y + 115),
            str(i + 1),
            fill="black"
        )

    st.image(
        grid_image,
        width=600
    )

    st.write("### Select the matching tiles")

    selected = []

    cols = st.columns(4)

    for i in range(16):

        row = i // 4
        col = i % 4

        with cols[col]:

            checked = st.checkbox(
                f"Tile {i + 1}",
                key=f"tile_{i}"
            )

            if checked:
                selected.append(i)

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "👤 Verify Human Answer",
            use_container_width=True
        ):

            if sorted(selected) == sorted(correct_indices):

                st.session_state.human_score += 1
                st.session_state.round_count += 1

                st.success(
                    "🎉 Correct! Human found all matching animals."
                )

            else:

                st.session_state.round_count += 1

                correct_tiles = [
                    i + 1
                    for i in correct_indices
                ]

                st.error(
                    f"❌ Incorrect. Correct tiles: {correct_tiles}"
                )

    with col2:

        if st.button(
            "🤖 Ask AI",
            use_container_width=True
        ):

            if not api_key.strip():

                st.warning(
                    "Please paste your Groq API key in the sidebar."
                )

            else:

                with st.spinner(
                    "🤖 Groq AI is analyzing the animal grid..."
                ):

                    prompt = f"""
                    Look at this 4x4 animal grid.

                    The target animal is: {target}

                    Each tile is numbered from 1 to 16.

                    Identify every tile containing the target animal.

                    Return ONLY the tile numbers separated by commas.

                    Example:
                    2, 7, 14
                    """

                    ai_answer, error = ask_groq_about_image(
                        grid_image,
                        prompt,
                        api_key
                    )

                if error:

                    st.error(error)

                else:

                    st.write(
                        f"🤖 AI selected: **{ai_answer}**"
                    )

                    numbers = re.findall(
                        r"\d+",
                        ai_answer
                    )

                    ai_indices = []

                    for number in numbers:

                        n = int(number)

                        if 1 <= n <= 16:
                            ai_indices.append(n - 1)

                    ai_indices = sorted(
                        list(set(ai_indices))
                    )

                    if ai_indices == sorted(correct_indices):

                        st.session_state.ai_score += 1

                        st.success(
                            "🤖 AI correctly identified all matching tiles!"
                        )

                    else:

                        correct_tiles = [
                            i + 1
                            for i in correct_indices
                        ]

                        st.info(
                            f"AI was incorrect. "
                            f"Correct tiles: {correct_tiles}"
                        )

    st.divider()

    if st.button(
        "🔄 New Animal Grid",
        use_container_width=True
    ):

        grid, target, correct_indices = create_animal_grid()

        st.session_state.animal_grid = grid
        st.session_state.animal_target = target
        st.session_state.animal_correct = correct_indices

        st.session_state.selected_animals = []

        st.rerun()


# =========================================================
# PROJECT INFORMATION
# =========================================================

st.divider()

st.markdown("""
<div class="footer">

<b>Can AI Beat You?</b><br><br>

Human vs Artificial Intelligence Visual Challenge<br>

CF Name: Jahangeer Ali &nbsp; | &nbsp; ID: MRBICF2003

</div>
""", unsafe_allow_html=True)
