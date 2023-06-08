# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 15:06:35 2022

@author: jfosnav
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

APP_TITLE = 'Movilidad estacional'
APP_SUB_TITLE = 'Fuente: Ine'

# def display_time_filters(df, sex):
#     year_list = list(df['Año'].unique())
#     year_list.sort(reverse = True )
#     year = st.sidebar.selectbox('Año', year_list, 0)
#     if year == 2023:
#         quarter = st.sidebar.radio('Trimestre', [1])
#     else:
#         quarter = st.sidebar.radio('Trimestre', [1, 2, 3, 4])
#     st.header(f'{year} T{quarter} - {sex}' )
#     return year, quarter

# def display_prov_filter(df, prov):
    
#     return st.sidebar.selectbox('Provincia', prov_list)

def display_day():
    return st.sidebar.radio('Día', ['20 Julio 2019', '15 Agosto 2019', '24 Noviembre 2019', '25 Diciembre 2019'])


def display_map(df, day):
    
    
    df = df.query('FECHA == @day')

    m = folium.Map(location=[40.42,  -3.7], zoom_start=5, tiles='Stamen Toner')
    print ("Asignando coropletas")
    coropletas = folium.Choropleth(geo_data=areas_geo,name="choropleth",data=df,columns=["ID_GRUPO", "porcentaje_variacion"],key_on="properties.ID_GRUPO", fill_color="RdYlBu",fill_opacity=0.4,line_opacity=1.0,legend_name="Variación de población (%)")
    print ("Añadiendo coropletas al mapa")
    coropletas.add_to(m)
    print ("Asignando tooltips")
    for feature in coropletas.geojson.data['features']:
        code = feature['properties']['ID_GRUPO']
        feature['properties']['Area'] = str(set(list(df_areas.query('ID_GRUPO == @code')['LITERAL_GRUPO'])))
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Area'], labels=False))
    print ("Agregando capa")
    folium.LayerControl().add_to(m)
    print ("Dibujando mapa")
    st_map = st_folium(m, width=700, height=450)
    codigo = '0000'
    if st_map['last_active_drawing']:
        codigo = st_map['last_active_drawing']['properties']['ID_GRUPO']
    return codigo

# def display_datos_paro(df, year, quarter, sex, prov_name):
#     df = df[(df['Año'] == year) & (df['Trimestre'] == quarter) & (df['Sexo'] == sex) & (df['Provincia'] == prov_name)]    
#     st.metric(sex, str(df.Paro.iat[0])+' %')

st.set_page_config(APP_TITLE)
st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

areas_geo = 'celdas_marzo_2020-4.json'
#prov_paro = 'TasaParoProvSeTr.csv'
#prov_data = pd.read_csv(prov_paro, encoding='utf-8')
#Sexo	Codigo	Provincia	Trimestre	Paro
#El código de provincia en el geojson es str y con cero a la izquierda
#prov_data['codigo'] = prov_data['codigo'].astype(str).str.zfill(2)

#prov_list = list(prov_data['Provincia'].unique())
#prov_dict = pd.Series(prov_data.Provincia.values,index=prov_data.codigo).to_dict()



@st.cache_data  #solo queremos leer los datos la primera vez, los tratamos y se cachean
def load_data():
    #cargamos las áreas de movilidad
    print("Cacheando...")
    #leer las areas, las necesitamos para obtenre la población y los nombres
    df_areas = pd.read_excel("areas_movilidad/areas_de_movilidad_y_poblacion_a_1_ene_2019.xlsx", sheet_name='NACIONAL_MOVILES', header=0, index_col=1, decimal='.')
    #el dataset de Pernoctación-residencia
    df_estacional = pd.read_excel("exp_em1_descargas/Tablas Publicacion EM-1/Tabla 3.4 Movilidad Estacional-Flujos Pernoctacion-Residencia +15 personas.xlsx",  header=0, decimal='.')
    
    
    #para saber la población de un área tenemos que agrupar
    df_poblacion = df_areas.groupby(['ID_GRUPO']).sum()
    
    #la clave primaria es el código "##XX"
    df_poblacion.index = df_poblacion.index.rename('Código área de pernoctación')
    #agregamos para saber cuánta gente pernocta en cada área 4488
    df_estacional_agregado = df_estacional.groupby(['FECHA','Código área de pernoctación']).sum()
    #hacemos el join con la tabla de población para tener la información que necesitamos  
    df_estacional_agregado = df_estacional_agregado.join(df_poblacion, how='left')
    #en pob_area_geo tenemos la poblacion 7903
    #vamos a calcular los que se quedan en su área de residencia, origen = destino
    df_se_quedan = df_estacional.query('`Código área de pernoctación` == `Código área de residencia`')
    #ponemos como índices el código y la fecha
    df_se_quedan = df_se_quedan.set_index(['Código área de pernoctación','FECHA'])
    #agregamos las columnas necesarias
    df_estacional_agregado['llegan'] = df_estacional_agregado['Nº de residentes en área de residencia que pernoctan en área de pernoctación'] - df_se_quedan['Nº de residentes en área de residencia que pernoctan en área de pernoctación'] 
    df_estacional_agregado['saldo'] = df_estacional_agregado['Nº de residentes en área de residencia que pernoctan en área de pernoctación'] - df_estacional_agregado['POB_AREA_GEO']
    df_estacional_agregado['porcentaje_variacion'] = (df_estacional_agregado['Nº de residentes en área de residencia que pernoctan en área de pernoctación'] - df_estacional_agregado['POB_AREA_GEO'])/df_estacional_agregado['POB_AREA_GEO'] * 100
    
    #usamos "df"
    df = df_estacional_agregado
    df = df.reset_index()
    df = df.rename(columns={"Código área de pernoctación":"ID_GRUPO"})
 
    return df, df_areas


df, df_areas = load_data()
area_data = 0 #inicialmente no hay área seleccionada
day = display_day() #obtenemos el día seleccionado de los 4 posibles
print ("Mando a dibujar")
area_code = display_map(df, day)



#Información de detalle cuando pulsan en un área


if (area_code!='0000'):
     area_nombre =  set(list(df_areas.query('ID_GRUPO == @area_code')['LITERAL_GRUPO']))
     st.header(f'Detalle del área: {area_nombre}')    

     a = df_areas.query('ID_GRUPO == @area_code')['POB_GRUPO'].iloc[0]
     e = df.query('ID_GRUPO == @area_code and FECHA == @day')['llegan'].iloc[0]
     f = df.query('ID_GRUPO == @area_code and FECHA == @day')['Nº de residentes en área de residencia que pernoctan en área de pernoctación'].iloc[0]
     c = f - e
     
     
     st.subheader(':family: Población residente en el área: ' + str(a)) 
     st.subheader(':house: Población residente que se queda en el área: ' + str(c) + ' (' + str(round(c/a * 100,2)) + '%)') 
     st.subheader(':moon: Población que pernocta en el area: '  + str(f) + ' (' + str(round(f/a * 100,2)) + '%)') 
     st.subheader(':car: Población que llega al área: '  + str(e) + ' ('  + str(round(e/a * 100,2)) + '%)') 
     st.subheader(':chart_with_upwards_trend: Variación de población: '  + str(f-a) + " (" + str(round((f-a)/a * 100,2)) + '%)') 
   
   
   
     # col1, col2 = st.columns(2)
     # with col1:
     #     st.subheader(':house: Población residente que se queda en el área: ' + str(c) + ' (C) ')
     # with col2:
     #     st.subheader(str(round(c/a * 100,2)) + '%') 
  