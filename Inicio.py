#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 21:42:00 2023

@author: jfosnav
"""

import streamlit as st


st.title('Movilidad estacional a partir de datos de la telefonía móvil')
st.header('Estudio EM-1')

 
st.markdown('En **2019** el **INE** realizó un primer estudio de movilidad 2019 a partir de datos de la **telefonía móvil** dentro de los trabajos preparatorios del Censo de Población y Viviendas 2021') # see *


st.header('Matriz de población estacional')


st.markdown('Se trata de una matriz de origen-destino que nos proporciona información sobre las personas que, **residiendo** en el área A, **pernoctan** en el área B')

st.subheader('Area de residencia :house: ')
st.markdown('Aquella en donde el teléfono móvil se encuentra durante más tiempo **entre las 01:00 y las 06:00 horas** durante los dos o tres meses antes al día considerado.')

st.subheader('Area de pernoctación :moon: ')
st.markdown('Aquella donde el móvil ha pasado más tiempo en la ventana temporal de **22:00 (del día anterior) a 06:00 (del día actual)**')


st.subheader('Cuatro días especiales')
st.markdown('Se pretende con ellos tener dos días representativos del **verano**, el día de **Navidad**, y un fin de semana **“valle”**.')
st.markdown('* 20 Julio 2019') 
st.markdown('* 15 Agosto 2019')
st.markdown('* 24 Noviembre 2019')
st.markdown('* 25 Diciembre 2019')

st.subheader('Referencias')
st.markdown('Los estudios de movilidad del INE: https://www.ine.es/experimental/movilidad/experimental_em.htm  Documento técnico: https://www.ine.es/experimental/movilidad/exp_em_proyecto.pdf')




