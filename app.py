import streamlit as st
import json
import requests

st.set_page_config(page_title="Moody Family Reading Tracker", layout="wide")

st.title("📚 Moody Family Reading Tracker")

kids = ["Freddie", "Genevieve", "Juliette", "Eleanor"]

# --- LOAD DATA SAFELY ---
try:
    with open("data.json", "r") as f:
        data = json.load(f)
        if not isinstance(data, dict):
            data = {}
except:
    data = {}

# ✅ Ensure correct structure
for kid in kids:
    if kid not in data or not isinstance(data[kid], list):
        data[kid] = []

# --- GET BOOK COVER (Open Library - reliable) ---
def get_book_cover(title):
    try:
        search_url = f"https://openlibrary.org/search.json?title={title}"
        response = requests.get(search_url, timeout=5).json()

        if "docs" not in response or len(response["docs"]) == 0:
            return None

        cover_id = response["docs"][0].get("cover_i")

        if cover_id:
            return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"

        return None

    except:
        return None

# --- INPUT ---
st.subheader("➕ Add a book")

col1, col2 = st.columns(2)

with col1:
    child = st.selectbox("Who is reading?", kids)

with col2:
    book = st.text_input("Book name (add author if possible)")

if st.button("Add Book"):
    if book:
        data[child].append(book)

        with open("data.json", "w") as f:
            json.dump(data, f)

        st.success(f"✅ {child} read '{book}'")

        # 🎉 Celebration every 5 books
        if len(data[child]) % 5 == 0:
            st.balloons()

# --- LEADERBOARD ---
st.divider()
st.subheader("🏆 Leaderboard")

leaderboard = sorted(kids, key=lambda x: len(data[x]), reverse=True)

for i, kid in enumerate(leaderboard):
    medal = ["🥇", "🥈", "🥉", ""][i] if i < 4 else ""
    st.write(f"{medal} **{kid}** — {len(data[kid])} books")

# --- PROGRESS ---
st.divider()
st.subheader("📊 Progress")

cols = st.columns(len(kids))

for i, kid in enumerate(kids):
    count = len(data[kid])
    level = count // 5 + 1
    progress = count % 5

    with cols[i]:
        st.markdown(f"### {kid}")
        st.metric("Books", count)
        st.progress(progress / 5)
        st.caption(f"Level {level}")

# --- BOOK DISPLAY ---
st.divider()
st.subheader("📖 Books Read")

for kid in kids:
    st.markdown(f"## {kid}")
    books = data[kid]

    if not books:
        st.write("No books yet")
        continue

    cols = st.columns(5)

    for i, book in enumerate(books):
        with cols[i % 5]:
            cover = get_book_cover(book)

            if cover:
                st.image(cover)
            else:
                st.image("https://placehold.co/128x200?text=No+Cover")

            st.caption(book)