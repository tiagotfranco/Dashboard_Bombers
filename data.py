import streamlit as st
import time
import numpy as np
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
import webbrowser
import pydeck as pdk



client = Socrata("analisi.transparenciacatalunya.cat", None)
results = client.get('g2ay-3vnj',limit=100000)
st.title('Actuacions dels bombers')

#creació d'un enllaç a l'origen de les dades
url='https://analisi.transparenciacatalunya.cat/Seguretat/Actuacions-dels-Bombers-de-la-Generalitat/g2ay-3vnj'
if st.button('Enllaç del repositori'):
    webbrowser.open_new_tab(url)


#la taula de valors amb les dades que ens interessa mostrar
st.subheader('Taula de resultats')
results = pd.DataFrame.from_records(results,columns=['act_dat_actuacio','tga_nom_grupo','tal_nom_alarma','municipi','nom_comarca','nom_regio','longitud','latitud',])
results

#aqui estan contades les diferents coses
st.subheader('Recompte tipus de incidencies')
res=pd.DataFrame.from_records(results,columns=['tga_nom_grupo']).value_counts()
res

#pie chart
st.subheader('Grafic')
pie=results["tga_nom_grupo"].value_counts().plot(kind = 'pie')
pie.figure

#mapa
zona=[41.93,2.254]
m=pd.DataFrame.from_records(results,columns=['longitud','latitud'])
m
m2=m.rename(columns={'longitud':'lon','latitud':'lat'})
m2
m3=m2.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
m3
m4=m3.astype(float)
m4
st.map(m4,zoom=6)

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
