import streamlit as st

def metric_box(title, value, color="#262730"):
    st.markdown(f"""
    <div style='
        border: 1px solid #ccc;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        background-color: {color};
        text-align: center;
        margin-bottom: 10px;
    '>
        <div style='font-size: 16px; color: #555;'>{title}</div>
        <div style='font-size: 28px; font-weight: bold;'>{value}</div>
    </div>
    """, unsafe_allow_html=True)
