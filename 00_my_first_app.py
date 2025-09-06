import streamlit as st

st.write("Hello world. Let's learn how to build a AI-based app together.")
st.write("🤖 2025年版：GPT-5とLangChainを使ったAIアプリ開発")

# 新機能のデモ
col1, col2 = st.columns(2)
with col1:
    st.info("Streamlit 1.48.0の新機能を体験中！")
with col2:
    if st.button("GPT-5について"):
        st.success("GPT-5は2025年8月にリリースされた最新のAIモデルです！")
