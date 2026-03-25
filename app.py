import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Економіка України", layout="wide")

st.title("📈 Економічний дашборд України")
st.write("Привіт! Тут скоро з'являться графіки ВВП, інфляції та безробіття з відкритих API.")
st.info("Дані завантажуються...")
