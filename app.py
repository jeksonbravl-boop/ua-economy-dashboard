import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import numpy as np
from sklearn.linear_model import LinearRegression # Додали бібліотеку для прогнозування

# Налаштування сторінки
st.set_page_config(page_title="Економіка України", layout="wide")
st.title(" Економічний дашборд України (+ Прогноз)")
st.write("Дані завантажуються з API Світового банку. 2025-2026 роки згенеровано алгоритмом машинного навчання (Лінійна регресія).")

INDICATORS = {
    'NY.GDP.MKTP.KD.ZG': 'ВВП (Річне зростання, %)',
    'FP.CPI.TOTL.ZG': 'Інфляція (%)',
    'SL.UEM.TOTL.ZS': 'Безробіття (%)'
}

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
                df_list.append(pd.DataFrame(records))

    if df_list:
        df_final = df_list[0]
        for df in df_list[1:]:
            df_final = pd.merge(df_final, df, on='Рік', how='outer')
        return df_final.sort_values('Рік').reset_index(drop=True)
    return pd.DataFrame()

with st.spinner('Підключення до бази даних та розрахунок прогнозів...'):
    df = fetch_wb_data()

st.markdown("---")
if not df.empty:
    
    # --- БЛОК МАШИННОГО НАВЧАННЯ (ПРОГНОЗ 2025-2026) ---
    df['Тип даних'] = 'Фактичні' # Позначаємо реальні дані
    
    future_years = pd.DataFrame({'Рік': [2025, 2026], 'Тип даних': ['Прогноз', 'Прогноз']})
    model = LinearRegression()
    
    for col in INDICATORS.values():
        # Беремо дані без порожніх значень для навчання
        valid_data = df.dropna(subset=[col])
        if not valid_data.empty:
            X_train = valid_data['Рік'].values.reshape(-1, 1)
            y_train = valid_data[col].values
            
            # Навчаємо модель і робимо прогноз
            model.fit(X_train, y_train)
            future_preds = model.predict(future_years['Рік'].values.reshape(-1, 1))
            future_years[col] = future_preds.round(2)
            
    # Об'єднуємо реальні дані та прогноз
    df_extended = pd.concat([df, future_years], ignore_index=True)

    st.success(" Дані завантажено. Прогноз на 2 роки побудовано!")
    
    # --- БЛОК 1: ГРАФІКИ ---
    st.header(" Динаміка макроекономічних показників")
    tab1, tab2, tab3 = st.tabs([" ВВП", " Інфляція", " Безробіття"])
    
    with tab1:
        fig_gdp = px.line(df_extended, x='Рік', y='ВВП (Річне зростання, %)', markers=True, 
                          line_dash='Тип даних', title='Динаміка ВВП України (з прогнозом)')
        fig_gdp.update_xaxes(type='category')
        st.plotly_chart(fig_gdp, use_container_width=True)
        
    with tab2:
        fig_inf = px.line(df_extended, x='Рік', y='Інфляція (%)', markers=True, 
                          line_dash='Тип даних', color_discrete_sequence=['red'], title='Рівень інфляції (з прогнозом)')
        fig_inf.update_xaxes(type='category')
        st.plotly_chart(fig_inf, use_container_width=True)
        
    with tab3:
        fig_unemp = px.line(df_extended, x='Рік', y='Безробіття (%)', markers=True, 
                            line_dash='Тип даних', color_discrete_sequence=['orange'], title='Рівень безробіття (з прогнозом)')
        fig_unemp.update_xaxes(type='category')
        st.plotly_chart(fig_unemp, use_container_width=True)

    # --- БЛОК 2: КОРЕЛЯЦІЯ ---
    st.markdown("---")
    st.header(" Зв'язок між показниками (Кореляція)")
    # Для кореляції використовуємо тільки фактичні дані (без прогнозу)
    corr_matrix = df.drop(columns=['Рік', 'Тип даних']).corr().round(2)
    fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
    st.plotly_chart(fig_corr, use_container_width=True)

    # --- БЛОК 3: ТАБЛИЦЯ ---
    with st.expander("Переглянути всі дані та прогноз (таблиця)"):
        # Показуємо останні 10 років факту + 2 роки прогнозу
        st.dataframe(df_extended.tail(12).style.apply(lambda x: ['background: #e6ffe6' if v == 'Прогноз' else '' for v in x], axis=1), use_container_width=True)
        
else:
    st.error(" Не вдалося завантажити дані. Спробуйте оновити сторінку.")
