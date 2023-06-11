#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 10:11:27 2023

@author: jfosnav
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.markdown("# Flujos de población")


st.markdown("Se muestra a continuación el detalle de los flujos de población para el área seleccionada. ")
st.markdown("Para ello se van a utilizar dos gráficas de barras donde se muestran por orden decreciente los flujos experimentados en las áreas donde ha ido o ha venido más gente.")



def display_day():
    return st.sidebar.radio('Día', ['20 Julio 2019', '15 Agosto 2019', '24 Noviembre 2019', '25 Diciembre 2019'])


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
    

    dfe = df_estacional

 
    return df, dfe, df_areas

df, dfe, df_areas = load_data()



day = display_day() #obtenemos el día seleccionado de los 4 posibles

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



p_out = dfe.query('`Código área de residencia`== @option and FECHA == @day and `Código área de pernoctación`!= @option')
p_out = p_out.sort_values(by=['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], ascending = False)[:20]
p_in = dfe.query('`Código área de pernoctación`== @option and FECHA == @day and `Código área de residencia`!= @option')
p_in = p_in.sort_values(by=['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], ascending = False)[:20]



st.subheader ("Dónde va la gente que reside en **" + areas[option]  + "** pero pernocta en otro sitio durante el **" + day + "**")
p_out_df = p_out[['Nombre área de pernoctación','Nº de residentes en área de residencia que pernoctan en área de pernoctación']]
p_out_df = p_out_df.rename(columns={"Nombre área de pernoctación":"Destino"})
p_out_df = p_out_df.rename(columns={"Nº de residentes en área de residencia que pernoctan en área de pernoctación":"Cantidad de personas"})

fig = plt.figure(figsize=(10,10))
plt.bar(p_out['Nombre área de pernoctación'], p_out['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], width=0.8, color='red', label="gente")
plt.grid(axis='y', color='0.85')
plt.xticks(rotation=90)
plt.title("Población que sale de " + areas[option] + " el día " + day , fontsize=15, verticalalignment='bottom')
plt.ylabel("Cantidad de personas", fontsize=15)
st.pyplot(fig)
st.dataframe(p_out_df, hide_index=True)

st.subheader ("De dónde viene la gente a **" + areas[option]  + "** que reside en otro sitio durante el **" + day + "**")
p_in_df = p_in[['Nombre área de residencia','Nº de residentes en área de residencia que pernoctan en área de pernoctación']]
p_in_df = p_in_df.rename(columns={"Nombre área de residencia":"Origen"})
p_in_df = p_in_df.rename(columns={"Nº de residentes en área de residencia que pernoctan en área de pernoctación":"Cantidad de personas"})

fig = plt.figure(figsize=(10,10))
plt.bar(p_in['Nombre área de residencia'], p_in['Nº de residentes en área de residencia que pernoctan en área de pernoctación'], width=0.8, color='blue', label="gente")
plt.grid(axis='y', color='0.85')
plt.xticks(rotation=90)
plt.title("Población que llega a " + areas[option] + " el día " + day , fontsize=15, verticalalignment='bottom')
plt.ylabel("Cantidad de personas", fontsize=15)
st.pyplot(fig)
st.dataframe(p_in_df, hide_index=True) 