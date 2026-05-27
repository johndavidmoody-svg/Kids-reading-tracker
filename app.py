import json
import datetime as dt
import requests
import streamlit as st

# ----------------------------
# Page setup
# ----------------------------
st.set_page_config(
    page_title="Moody Family Reading Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Styling (CSS)
# ----------------------------
st.markdown(
    """
<style>
:root {
  --bg: #0b1220;
  --card: #111a2e;
  --card2: #0f172a;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #60a5fa;
  --good: #34d399;
  --warning: #fbbf24;
  --border: rgba(255,255,255,0.08);
}

.block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
[data-testid="stSidebar"] { border-right: 1px solid var(--border); }
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
h1, h2, h3 { letter-spacing: -0.02em; }

.kpi-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px 16px 14px 16px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.25);
}
.kpi-title { color: var(--muted); font-size: 0.85rem; margin-bottom: 6px; }
.kpi-value { color: var(--text); font-size: 1.55rem; font-weight: 700; line-height: 1.15; }
.kpi-sub { color: var(--muted); font-size: 0.85rem; margin-top: 6px; }

.section {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  background: rgba(255,255,255,0.02);
}

.book-card {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 10px;
  background: rgba(255,255,255,0.02);
}

.small-muted { color: var(--muted); font-size: 0.85rem; }

.stButton>button {
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.12);
  padding: 0.6rem 0.9rem;
  font-weight: 650;
}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# App constants
# ----------------------------
KIDS = ["Freddie", "Genevieve", "Juliette", "Eleanor"]
DATA_FILE = "data.json"

BADGES = [
    (5, "⭐ Getting Strong"),
    (10, "🔥 Reading Star"),
    (20, "🏆 Book Master"),
]

# ----------------------------
# Data helpers
# ----------------------------
def load_data() -> dict:
    try:
        with open(DATA_FILE, "r") as f:
            d = json.load(f)
            if not isinstance(d, dict):
                d = {}
    except:
        d = {}
    # ensure structure
    for k in KIDS:
        if k not in d or not isinstance(d[k], list):
            d[k] = []
    return d

def save_data(d: dict) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(d, f)

def badge_for(count: int) -> str:
    result = "📘 Just Starting"
    for threshold, label in BADGES:
        if count >= threshold:
            result = label
    return result

def level_for(count: int) -> int:
    return (count // 5) + 1

def progress_to_next_level(count: int) -> float:
    return (count % 5) / 5.0

# ----------------------------
# Cover lookup (Open Library) + caching
# ----------------------------
@st.cache_data(ttl=60 * 60 * 24)  # cache for 24 hours per title
def get_cover_url(title: str) -> str | None:
    """
    Uses Open Library search to find a cover id, then builds a cover url.
    """
    try:
        search_url = f"https://openlibrary.org/search.json?title={title}"
        r = requests.get(search_url, timeout=6)
        if r.status_code != 200:
            return None
        payload = r.json()
        docs = payload.get("docs", [])
        if not docs:
            return None
        cover_id = docs[0].get("cover_i")
        if not cover_id:
            return None
        return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
    except:
        return None

PLACEHOLDER = "https://placehold.co/180x260?text=No+Cover"

# ----------------------------
# Load data
# ----------------------------
data = load_data()

# ----------------------------
# Header
# ----------------------------
st.markdown("## 📚 Moody Family Reading Tracker")
st.markdown('<div class="small-muted">Log books, track levels, and celebrate progress.</div>', unsafe_allow_html=True)
st.write("")

# ----------------------------
# Sidebar: Add book
# ----------------------------
with st.sidebar:
    st.markdown("### ➕ Add a book")
    st.markdown('<div class="small-muted">Tip: add the author for better cover matches (e.g., “Matilda Roald Dahl”).</div>', unsafe_allow_html=True)
    st.write("")

    child = st.selectbox("Reader", KIDS, index=0)
    book = st.text_input("Book title", placeholder="e.g., The Gruffalo Julia Donaldson")

    add_clicked = st.button("Add Book", use_container_width=True)

    if add_clicked:
        cleaned = (book or "").strip()
        if not cleaned:
            st.warning("Please type a book title first.")
        else:
            data[child].append(cleaned)
            save_data(data)
            # celebratory moment each 5 books
            if len(data[child]) % 5 == 0:
                st.success(f"Nice! {child} reached a new level 🎉")
                st.balloons()
            else:
                st.success(f"Added: “{cleaned}” for {child}")
            st.rerun()

    st.divider()
    st.markdown("### ⚙️ Admin")
    if st.button("Reset ALL data (clears data.json)", type="secondary", use_container_width=True):
        for k in KIDS:
            data[k] = []
        save_data(data)
        st.success("All data cleared.")
        st.rerun()

# ----------------------------
# Overview KPIs
# ----------------------------
total_books = sum(len(data[k]) for k in KIDS)
top_kid = max(KIDS, key=lambda k: len(data[k]))
top_count = len(data[top_kid])

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">Total books logged</div>
          <div class="kpi-value">{total_books}</div>
          <div class="kpi-sub">Across all readers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">Current leader</div>
          <div class="kpi-value">{top_kid}</div>
          <div class="kpi-sub">{top_count} book(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi3:
    avg = round(total_books / max(len(KIDS), 1), 1)
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">Average per reader</div>
          <div class="kpi-value">{avg}</div>
          <div class="kpi-sub">Books logged</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with kpi4:
    today = dt.date.today().strftime("%d %b %Y")
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-title">Today</div>
          <div class="kpi-value">{today}</div>
          <div class="kpi-sub">Keep reading 📖</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ----------------------------
# Main sections: Progress + Library
# ----------------------------
tab1, tab2 = st.tabs(["📈 Progress", "🗂️ Library"])

# ---------- Progress Tab ----------
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, kid in enumerate(KIDS):
        count = len(data[kid])
        lvl = level_for(count)
        prog = progress_to_next_level(count)
        badge = badge_for(count)

        with cols[i]:
            st.markdown(f"### {kid}")
            st.metric("Books", count)
            st.progress(prog)
            st.caption(f"Level {lvl} • {badge}")

    st.write("")
    st.subheader("🏆 Leaderboard")
    leaderboard = sorted(KIDS, key=lambda k: len(data[k]), reverse=True)

    for rank, kid in enumerate(leaderboard, start=1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
        st.write(f"{medal} **{kid}** — {len(data[kid])} book(s)")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Library Tab ----------
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)

    st.markdown("### 📖 Books by reader")
    st.markdown('<div class="small-muted">Covers are fetched automatically. If a cover is missing, try adding the author.</div>', unsafe_allow_html=True)
    st.write("")

    for kid in KIDS:
        books = data[kid]
        with st.expander(f"{kid} — {len(books)} book(s)", expanded=(kid == top_kid)):
            if not books:
                st.info("No books logged yet.")
            else:
                # show in a neat grid
                grid = st.columns(5)
                for idx, title in enumerate(books):
                    with grid[idx % 5]:
                        cover = get_cover_url(title) or PLACEHOLDER
                        st.image(cover, use_container_width=True)
                        st.markdown(f"<div class='small-muted'>{title}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown("<div class='small-muted'>Tip: After you push changes to GitHub, Streamlit will redeploy automatically.</div>", unsafe_allow_html=True)
