import streamlit as st
from generate_html import generate_html_from_yandex

st.set_page_config(page_title="Road Events Visualizer", layout="wide")

st.title("🚗 Road Events Visualizer")

url = st.text_input("URL папки на Яндекс.Диске :", placeholder="https://disk.yandex.ru/d/...")

if url:
    try:
        html_content = generate_html_from_yandex(url)
        st.components.v1.html(html_content, height=800, scrolling=True)
    except Exception as e:
        st.error(f"Ошибка: {str(e)}")