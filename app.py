import streamlit as st
import pandas as pd
import requests

# Налаштування сторінки
st.set_page_config(page_title="Економіка України", layout="wide")
st.title(" Економічний дашборд України")
st.write("Дані автоматично завантажуються з відкритих API Світового банку (World Bank).")

# Коди індикаторів Світового банку
INDICATORS = {
    'NY.GDP.MKTP.KD.ZG': 'ВВП (Річне зростання, %)',
    'FP.CPI.TOTL.ZG': 'Інфляція (%)',
    'SL.UEM.TOTL.ZS': 'Безробіття (%)'
}

# Функція для завантаження даних
@st.cache_data
def fetch_wb_data():
    df_list = []
    
    for code, name in INDICATORS.items():
        url = f"http://api.worldbank.org/v2/country/UKR/indicator/{code}?format=json&per_page=30"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                records = [{'Рік': int(item['date']), name: item['value']} 
                           for item in data[1] if item['value'] is not None]
                df_temp = pd.DataFrame(records)
                df_list.append(df_temp)

    if df_list:
        df_final = df_list[0]
        for df in df_list[1:]:
            df_final = pd.merge(df_final, df, on='Рік', how='outer')
            
        return df_final.sort_values('Рік').reset_index(drop=True)
    
    return pd.DataFrame()

# Виводимо спінер, поки дані вантажаться
with st.spinner('Підключення до бази даних Світового банку...'):
    df = fetch_wb_data()

# Перевіряємо, чи завантажилися дані
st.markdown("---")
if not df.empty:
    st.success(" Дані успішно завантажено та оброблено!")
    
    st.subheader(" Сирі дані (останні 15 років)")
    st.dataframe(df.tail(15), use_container_width=True)
else:
    st.error(" Не вдалося завантажити дані.")
