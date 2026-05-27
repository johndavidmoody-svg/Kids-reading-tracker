import streamlit as st
import json
import requests

st.set_page_config(page_title="Kids Reading Tracker", layout="wide")

st.title("📚 Kids Reading Tracker")

kids = ["Freddie", "Genevieve", "Juliette", "Eleanor"]

# Load saved data

try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {}

# ✅ Ensure all kids exist
for kid in kids:
    if kid not in data:
        data[kid] = []


# --- FUNCTION: Get book cover ---
def get_book_cover(title):
    url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
    response = requests.get(url).json()
    try:
        return response["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
    except:
        return None

# --- INPUT AREA ---
st.subheader("Add a book")

col1, col2 = st.columns(2)

with col1:
    child = st.selectbox("Who is reading?", kids)

with col2:
    book = st.text_input("Book name")

if st.button("Add Book"):
    if book:
        data[child].append(book)
        with open("data.json", "w") as f:
            json.dump(data, f)
        st.success(f"✅ {child} read '{book}'")

# --- DISPLAY PROGRESS ---
st.divider()
st.subheader("📊 Progress")

cols = st.columns(len(kids))

for i, kid in enumerate(kids):
    count = len(data[kid])
    level = count // 5 + 1
    progress = count % 5

    with cols[i]:
        st.markdown(f"### {kid}")
        st.metric(label="Books Read", value=count)
        st.progress(progress / 5)
        st.caption(f"Level {level}")

# --- DISPLAY BOOKS ---
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

            st.caption(book)