#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 08:43:48 2023

@author: jfosnav
"""


import streamlit as st




import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

#APP_TITLE = 'Flujos por área'
#APP_SUB_TITLE = 'Fuente: Ine'


st.markdown("# Evolución durante los días especiales")
st.markdown("Al tratarse de 4 días especiales durante el año escogidos arbitrariamente no se adecúan mucho a lo que es una serie temporal pero aún así los podemos representar para ver cómo se comportan algunos indicadores en estos días escogidos")

st.subheader("Variación del porcentaje de población en un área :chart_with_upwards_trend:" )
st.markdown("Se colorea la barra en rojo cuando el flujo de población es negativo (sale más gente que entra) y en azul cuando es positivo (entra más gente que sale)")

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
    
    areas_geo = 'celdas_marzo_2020-4.json'
    dfe = df_estacional
    geo = gpd.read_file(areas_geo)
 
    return df, dfe, df_areas, geo

df, dfe, df_areas, geo = load_data()


# option = st.sidebar.selectbox(
#     'Elige área',
#      sorted(df_areas['ID_GRUPO'].unique()))



provincias = pd.Series(df_areas.NPRO.values,index=df_areas.NPRO).to_dict()
option = st.sidebar.selectbox('Elige provincia', provincias.keys(), format_func=lambda x:provincias[ x ])

dfa = df_areas.query("NPRO == @option")

areas = pd.Series(dfa.LITERAL_GRUPO.values,index=dfa.ID_GRUPO).to_dict()
option = st.sidebar.selectbox('Elige área', areas.keys(), format_func=lambda x:areas[ x ])


dfw = df.query('ID_GRUPO == @option')
dfw['new_index'] = [2,1,3,4]
dfw = dfw.reset_index()
dfw = dfw.set_index('new_index')
dfw = dfw.sort_index()



dfw['date'] = ['2019-07-20','2019-08-15','2019-11-24','2019-12-25']
dfw['date']= pd.to_datetime(dfw['date'])




#st.write(dfw)
#st.write(dfw.index)


fig = plt.figure(figsize=(10,10))
dfw['positivo'] = dfw['porcentaje_variacion'] > 0
plt.bar(dfw.date, dfw.porcentaje_variacion, width=20, color=dfw.positivo.map({True: 'b', False: 'r'}), label="Variación de población")
plt.grid(axis='y', color='0.85')

plt.title("Variación del porcentaje de población experimentado en " + areas[option] + " durante los días especiales" , fontsize=12, verticalalignment='bottom')
plt.ylabel("Porcentaje", fontsize=15)
#plt.ylim(-100, 100)
st.pyplot(fig)


dfp = dfw[['FECHA','porcentaje_variacion']]
dfp['porcentaje_variacion'] =round(dfp['porcentaje_variacion'],2)
dfp = dfp.astype({"porcentaje_variacion": str})
dfp['porcentaje_variacion'] =dfp['porcentaje_variacion'] + "%"
 #+ "%"
dfp = dfp.rename(columns={"porcentaje_variacion":"Porcentaje de variación"})
st.dataframe(dfp, hide_index=True)



st.subheader("Cuánta gente pernocta :moon:")

# fig = plt.figure(figsize=(10, 10))
# plt.grid(linestyle="-.", linewidth=1, color='lightgray')
# plt.plot(dfw.FECHA, dfw.llegan, marker='', linestyle='dashed', color='black',  linewidth=3, markersize=5, label="llegan")
# plt.plot(dfw.FECHA, dfw['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], marker='', linestyle='dashed', color='brown',  linewidth=3, markersize=5, label="Pernoctan")

# plt.xticks(rotation=45)
# plt.legend(loc = "upper left", fontsize = 15)
# #plt.title("Población que llega a ", fontsize=30, verticalalignment='bottom')
# plt.xlabel("Fecha", fontsize=20)
# plt.ylabel("Ciudadanos", fontsize=20)
# #plt.show()
# st.pyplot(fig)


fig = plt.figure(figsize=(10,10))
plt.bar(dfw.date,  dfw['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], width=20, color='b', label="Población que pernocta en el área")
plt.grid(axis='y', color='0.85')

plt.title("Población que pernocta  en " + areas[option] + " durante los días especiales" , fontsize=12, verticalalignment='bottom')
plt.ylabel("Ciudadanos", fontsize=15)
#plt.ylim(-100, 100)
st.pyplot(fig)


dfp = dfw[['FECHA','Nº de residentes en área de residencia que pernoctan en área de pernoctación']]
dfp = dfp.rename(columns={"Nº de residentes en área de residencia que pernoctan en área de pernoctación":"Personas que pernoctan"})
st.dataframe(dfp, hide_index=True)


#centroid_equal_area = geo.query('ID_GRUPO == @option').to_crs('+proj=cea').centroid.to_crs(geo.crs)


#print (centroid_equal_area)

# m = folium.Map(location=[40.42,  -3.7], zoom_start=5, tiles='Stamen Toner')
# coropletas = folium.Choropleth(geo_data=geo,name="choropleth",data=df,columns=["ID_GRUPO", "porcentaje_variacion"],key_on="properties.ID_GRUPO", fill_color="RdYlBu",fill_opacity=0.4,line_opacity=1.0,legend_name="Variación de población (%)")
# print ("Añadiendo coropletas al mapa")
# coropletas.add_to(m)
# st_map = st_folium(m, width=700, height=450)

#day = "15 Agosto 2019"


st.subheader("Cuánta gente llega :car:")

# fig = plt.figure(figsize=(10, 10))
# plt.grid(linestyle="-.", linewidth=1, color='lightgray')
# plt.plot(dfw.FECHA, dfw.llegan, marker='', linestyle='dashed', color='black',  linewidth=3, markersize=5, label="llegan")
# plt.plot(dfw.FECHA, dfw['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], marker='', linestyle='dashed', color='brown',  linewidth=3, markersize=5, label="Pernoctan")

# plt.xticks(rotation=45)
# plt.legend(loc = "upper left", fontsize = 15)
# #plt.title("Población que llega a ", fontsize=30, verticalalignment='bottom')
# plt.xlabel("Fecha", fontsize=20)
# plt.ylabel("Ciudadanos", fontsize=20)
# #plt.show()
# st.pyplot(fig)


fig = plt.figure(figsize=(10,10))
plt.bar(dfw.date,  dfw['llegan'], width=20, color='b', label="Población que pernocta en el área")
plt.grid(axis='y', color='0.85')

plt.title("Población que llaga a " + areas[option] + " durante los días especiales" , fontsize=12, verticalalignment='bottom')
plt.ylabel("Ciudadanos", fontsize=15)
#plt.ylim(-100, 100)
st.pyplot(fig)


dfp = dfw[['FECHA','llegan']]
dfp = dfp.rename(columns={"llegan":"Personas que llegan"})
st.dataframe(dfp, hide_index=True)




