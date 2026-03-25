import streamlit as st
import pandas as pd
import requests
import plotly.express as px  # ДОДАЛИ БІБЛІОТЕКУ ДЛЯ ГРАФІКІВ

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

# Виводимо спінер
with st.spinner('Підключення до бази даних Світового банку...'):
    df = fetch_wb_data()

# Перевіряємо, чи завантажилися дані
st.markdown("---")
if not df.empty:
    st.success(" Дані успішно завантажено та оброблено!")
    
    # --- БЛОК 1: ГРАФІКИ ---
    st.header(" Динаміка макроекономічних показників")
    
    # Створюємо 3 вкладки (Tabs) для зручного перемикання між графіками
    tab1, tab2, tab3 = st.tabs([" ВВП", " Інфляція", " Безробіття"])
    
    with tab1:
        fig_gdp = px.line(df, x='Рік', y='ВВП (Річне зростання, %)', markers=True, title='Динаміка ВВП України')
        fig_gdp.update_xaxes(type='category') # Робимо роки чіткими
        st.plotly_chart(fig_gdp, use_container_width=True)
        
    with tab2:
        # Інфляцію зробимо червоним кольором
        fig_inf = px.line(df, x='Рік', y='Інфляція (%)', markers=True, title='Рівень інфляції', color_discrete_sequence=['red'])
        fig_inf.update_xaxes(type='category')
        st.plotly_chart(fig_inf, use_container_width=True)
        
    with tab3:
        # Безробіття зробимо помаранчевим
        fig_unemp = px.line(df, x='Рік', y='Безробіття (%)', markers=True, title='Рівень безробіття', color_discrete_sequence=['orange'])
        fig_unemp.update_xaxes(type='category')
        st.plotly_chart(fig_unemp, use_container_width=True)

    # --- БЛОК 2: ТАБЛИЦЯ ---
    with st.expander("Переглянути сирі дані (таблиця)"):
        st.dataframe(df.tail(15), use_container_width=True)
        
else:
    st.error(" Не вдалося завантажити дані. Спробуйте оновити сторінку.")
