import streamlit as st
import json

st.title("📚 Kids Reading Tracker")

kids = ["Freddie", "Genevieve", "Juliette", "Eleanor"]

# Load saved data
try:
    with open("data.json", "r") as f:
        data = json.load(f)
except:
    data = {kid: [] for kid in kids}

child = st.selectbox("Who is reading?", kids)

book = st.text_input("What book did they read?")

if st.button("Add Book"):
    if book:
        data[child].append(book)
        with open("data.json", "w") as f:
            json.dump(data, f)
        st.success(f"✅ {child} read '{book}'")

# Show books
st.subheader("📖 Books read")

for kid in kids:
    st.write(f"**{kid}:**")
    for b in data[kid]:
        st.write(f"- {b}")
        
st.subheader("📊 Progress")

for kid in kids:
    count = len(data[kid])
    level = count // 5 + 1

    st.write(f"**{kid}** - {count} books - Level {level}")

    for b in data[kid]:
        st.write(f"- {b}")
