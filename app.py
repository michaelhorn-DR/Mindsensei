import streamlit as st
import pandas as pd
import io

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MindShift Sensei",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    raw = pd.read_csv("MindShift_Starter_CSV.csv", sep="\t")
    combined = "\n".join(raw.iloc[:, 0].tolist())
    df = pd.read_csv(
        io.StringIO(combined),
        header=None,
        names=["Level","World","Negative_Script","Distortion_Type",
               "XP_Value","Hint_for_Reframe","Sample_Strong_Reframe"]
    )
    df["XP_Value"] = pd.to_numeric(df["XP_Value"], errors="coerce").fillna(0).astype(int)
    return df

df = load_data()

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
WORLD_EMOJIS = {
    "Inner Critic Woods": "🌲",
    "Reframe River":      "🌊",
    "Imposter Inferno":   "🔥",
    "Resilience Ridge":   "⛰️",
    "Growth Peak":        "🏔️",
}

WORLD_COLORS = {
    "Inner Critic Woods": "#2d6a4f",
    "Reframe River":      "#1565c0",
    "Imposter Inferno":   "#b71c1c",
    "Resilience Ridge":   "#4e342e",
    "Growth Peak":        "#4527a0",
}

WORLDS = list(WORLD_EMOJIS.keys())
TOTAL_XP = int(df["XP_Value"].sum())
TOTAL_LEVELS = len(df)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Exo+2:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; }

.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem;
    text-align: center;
    background: linear-gradient(135deg, #7c3aed, #2563eb, #059669);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.tagline {
    text-align: center;
    font-size: 1.2rem;
    color: #94a3b8;
    margin-bottom: 2rem;
    font-style: italic;
}
.xp-bar-label {
    font-weight: 600;
    font-size: 0.9rem;
    color: #7c3aed;
}
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 700;
    color: white;
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    margin-bottom: 0.5rem;
}
.world-card {
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
    color: white;
    font-weight: 600;
}
.challenge-box {
    background: #1e293b;
    border-left: 5px solid #7c3aed;
    border-radius: 8px;
    padding: 20px;
    font-size: 1.15rem;
    font-style: italic;
    color: #e2e8f0;
    margin: 1rem 0;
}
.hint-box {
    background: #fef9c3;
    border-left: 4px solid #eab308;
    border-radius: 8px;
    padding: 14px;
    color: #713f12;
    margin: 0.5rem 0;
}
.reframe-box {
    background: #dcfce7;
    border-left: 5px solid #16a34a;
    border-radius: 8px;
    padding: 16px;
    color: #14532d;
    font-weight: 600;
    margin: 0.5rem 0;
}
.xp-award {
    text-align: center;
    font-size: 2rem;
    font-family: 'Orbitron', sans-serif;
    color: #eab308;
}
.victory-box {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    color: white;
    margin: 2rem auto;
    max-width: 600px;
    box-shadow: 0 0 40px rgba(124,58,237,0.5);
}
.victory-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 2.5rem;
    color: #fbbf24;
}
.stButton > button {
    border-radius: 10px;
    font-family: 'Exo 2', sans-serif;
    font-weight: 700;
    transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
defaults = {
    "screen": "welcome",
    "player_name": "",
    "current_level_idx": 0,
    "total_xp": 0,
    "hint_shown": False,
    "submitted": False,
    "reframe_input": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def go(screen):
    st.session_state.screen = screen

def advance_level():
    st.session_state.current_level_idx += 1
    st.session_state.hint_shown = False
    st.session_state.submitted = False
    st.session_state.reframe_input = ""
    if st.session_state.current_level_idx >= TOTAL_LEVELS:
        st.session_state.screen = "victory"
    else:
        st.session_state.screen = "game"

def world_status(world_name):
    world_rows = df[df["World"] == world_name].index.tolist()
    cur = st.session_state.current_level_idx
    if cur > max(world_rows):
        return "complete"
    elif cur >= min(world_rows):
        return "in_progress"
    else:
        return "locked"

# ─────────────────────────────────────────────
# SIDEBAR — WORLD MAP
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ World Map")
    if st.session_state.player_name:
        st.markdown(f"**Sensei:** {st.session_state.player_name}")
    st.markdown("---")
    for world in WORLDS:
        emoji = WORLD_EMOJIS[world]
        status = world_status(world)
        if status == "complete":
            icon, color, label = "✅", "#15803d", "Complete"
        elif status == "in_progress":
            icon, color, label = "⚔️", WORLD_COLORS[world], "In Progress"
        else:
            icon, color, label = "🔒", "#475569", "Locked"
        st.markdown(
            f'''<div class="world-card" style="background:{color};">
                {emoji} {icon} <strong>{world}</strong><br>
                <small>{label}</small>
            </div>''',
            unsafe_allow_html=True
        )
    st.markdown("---")
    st.markdown(f"**Total Possible XP:** {TOTAL_XP} ⭐")
    if st.session_state.screen not in ("welcome", "name"):
        pct = int((st.session_state.total_xp / TOTAL_XP) * 100)
        st.markdown(f"**Your XP:** {st.session_state.total_xp} / {TOTAL_XP} ({pct}%)")

# ─────────────────────────────────────────────
# SCREEN: WELCOME
# ─────────────────────────────────────────────
if st.session_state.screen == "welcome":
    st.markdown("<div class='main-title'>🧠 MindShift Sensei</div>", unsafe_allow_html=True)
    st.markdown("<div class='tagline'>Reframe your inner critic. Level up your mindset.</div>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Welcome, future Sensei! 🥷

        In **MindShift Sensei**, you'll journey through **5 Worlds** filled with
        cognitive distortions and negative self-talk.

        Your mission: **reframe the inner critic** and earn XP by
        replacing destructive thoughts with growth-oriented mindsets.

        ---
        🌲 **Inner Critic Woods** → 🌊 **Reframe River** → 🔥 **Imposter Inferno**
        → ⛰️ **Resilience Ridge** → 🏔️ **Growth Peak**

        ---
        **5 worlds · 25 levels · 150 XP available**
        """)
        if st.button("🚀 Begin Your Journey", use_container_width=True, type="primary"):
            go("name")
            st.rerun()

# ─────────────────────────────────────────────
# SCREEN: ENTER NAME
# ─────────────────────────────────────────────
elif st.session_state.screen == "name":
    st.markdown("<div class='main-title'>🧠 MindShift Sensei</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🥷 What shall we call you, Sensei?")
        name = st.text_input("Enter your name:", placeholder="e.g. Alex, Jordan, Dr. Smith...")
        if st.button("⚔️ Enter the Game", use_container_width=True, type="primary"):
            if name.strip():
                st.session_state.player_name = name.strip()
                go("game")
                st.rerun()
            else:
                st.warning("Please enter your name to continue!")

# ─────────────────────────────────────────────
# SCREEN: GAME
# ─────────────────────────────────────────────
elif st.session_state.screen == "game":
    idx = st.session_state.current_level_idx
    row = df.iloc[idx]

    world     = row["World"]
    emoji     = WORLD_EMOJIS[world]
    color     = WORLD_COLORS[world]
    level     = row["Level"]
    distortion = row["Distortion_Type"]
    script    = row["Negative_Script"]
    hint      = row["Hint_for_Reframe"]
    sample    = row["Sample_Strong_Reframe"]
    xp_val    = int(row["XP_Value"])

    # ── TOP XP BAR ──
    xp_now = st.session_state.total_xp
    pct = xp_now / TOTAL_XP
    col_xp1, col_xp2 = st.columns([3, 1])
    with col_xp1:
        st.markdown(f"<span class='xp-bar-label'>⭐ XP Progress: {xp_now} / {TOTAL_XP}</span>",
                    unsafe_allow_html=True)
        st.progress(pct)
    with col_xp2:
        st.markdown(f"**Level {idx+1} / {TOTAL_LEVELS}**")

    st.markdown("---")

    # ── WORLD HEADER ──
    st.markdown(
        f'''<div class="world-card" style="background:{color}; font-size:1.3rem;">
            {emoji} <strong>{world}</strong> &nbsp;|&nbsp; Level {level}
        </div>''',
        unsafe_allow_html=True
    )

    # ── DISTORTION BADGE ──
    st.markdown(f'<span class="badge">🧩 Distortion: {distortion}</span>',
                unsafe_allow_html=True)

    # ── CHALLENGE ──
    st.markdown("#### 💬 Inner Critic Says:")
    st.markdown(f'<div class="challenge-box">"{script}"</div>', unsafe_allow_html=True)

    # ── REFRAME INPUT ──
    if not st.session_state.submitted:
        st.markdown("#### ✍️ Your Reframe:")
        user_reframe = st.text_area(
            "How would you reframe this thought?",
            value=st.session_state.reframe_input,
            height=120,
            placeholder="Replace the negative script with a growth-oriented reframe...",
            key=f"reframe_{idx}"
        )
        st.session_state.reframe_input = user_reframe

        col_hint, col_submit = st.columns([1, 2])
        with col_hint:
            if st.button("💡 Show Hint", use_container_width=True):
                st.session_state.hint_shown = True
                st.rerun()
        with col_submit:
            if st.button("✅ Submit Reframe", use_container_width=True, type="primary"):
                if st.session_state.reframe_input.strip():
                    st.session_state.total_xp += xp_val
                    st.session_state.submitted = True
                    st.rerun()
                else:
                    st.warning("Please write your reframe before submitting!")

        if st.session_state.hint_shown:
            st.markdown(
                f'<div class="hint-box">💡 <strong>Hint:</strong> {hint}</div>',
                unsafe_allow_html=True
            )

    # ── POST-SUBMIT FEEDBACK ──
    else:
        st.markdown("#### ✍️ Your Reframe:")
        st.info(st.session_state.reframe_input)
        st.markdown(
            f'<div class="xp-award">+{xp_val} XP Earned! ⭐</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="reframe-box">🏆 <strong>Sample Strong Reframe:</strong><br>{sample}</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        next_label = "🏁 See Final Results" if idx + 1 >= TOTAL_LEVELS else "⏭️ Next Level →"
        if st.button(next_label, use_container_width=True, type="primary"):
            advance_level()
            st.rerun()

# ─────────────────────────────────────────────
# SCREEN: VICTORY
# ─────────────────────────────────────────────
elif st.session_state.screen == "victory":
    st.markdown("<div class='main-title'>🧠 MindShift Sensei</div>", unsafe_allow_html=True)
    name = st.session_state.player_name
    xp   = st.session_state.total_xp
    pct  = int((xp / TOTAL_XP) * 100)

    if pct == 100:
        rank, msg = "🏆 Grand Sensei", "Perfect score! You've mastered every reframe!"
    elif pct >= 80:
        rank, msg = "⭐ Mindset Master", "Incredible work! Your inner critic doesn't stand a chance."
    elif pct >= 60:
        rank, msg = "🎯 Reframe Warrior", "Solid journey! Keep practicing these reframes daily."
    else:
        rank, msg = "🌱 Growth Seeker", "Every journey starts somewhere. Come back and level up!"

    st.markdown(f"""
    <div class="victory-box">
        <div class="victory-title">🎉 Journey Complete!</div>
        <br>
        <h2>Well done, <span style="color:#fbbf24;">{name}</span>!</h2>
        <br>
        <p style="font-size:1.5rem;">⭐ Total XP Earned: <strong style="color:#fbbf24;">{xp} / {TOTAL_XP}</strong></p>
        <p style="font-size:1.2rem;">Your Rank: <strong style="color:#a78bfa;">{rank}</strong></p>
        <p style="color:#cbd5e1;">{msg}</p>
        <br>
        <p style="color:#94a3b8; font-size:0.9rem; font-style:italic;">
            "The mind is its own place, and in itself can make a heaven of hell, a hell of heaven."<br>
            — John Milton
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🗺️ World Completion Summary")
        for world in WORLDS:
            e = WORLD_EMOJIS[world]
            world_xp = int(df[df["World"] == world]["XP_Value"].sum())
            st.markdown(f"✅ {e} **{world}** — {world_xp} XP")
        st.markdown("---")
        if st.button("🔄 Play Again", use_container_width=True, type="primary"):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()