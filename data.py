import streamlit as st
import time
import numpy as np
import pandas as pd
from sodapy import Socrata
import matplotlib.pyplot as plt
import webbrowser
import pydeck as pdk
from datetime import datetime
import datetime as dtime
from urllib.request import urlopen
import json
import plotly.express as px

#sidebar
lim=st.sidebar.slider('Dades mostrejades',min_value=200, max_value=80000, value=5000, step=200)
idate= st.sidebar.date_input('data inicial', dtime.date(2015,1,1))
fdate= st.sidebar.date_input('data final', dtime.date.today())
nom_grupo= st.sidebar.selectbox(
    "Que tipo de incidencia quieres ver?",
    ("assistència tècnica","salvaments","incendi urbà","activitat no urgent","mobilitat","pràctiques","incendi vegetació","dispositiu preventiu","fuites perilloses","suport tècnic","simulacres")
)

#cridar la nostra base de dades des de la web
client = Socrata("analisi.transparenciacatalunya.cat", None)
results = client.get('g2ay-3vnj',limit=lim)

#results = pd.read_csv("Actuacions_dels_Bombers_de_la_Generalitat.csv")
st.title('Actuacions dels bombers')

#creació d'un enllaç a l'origen de les dades
url='https://analisi.transparenciacatalunya.cat/Seguretat/Actuacions-dels-Bombers-de-la-Generalitat/g2ay-3vnj'
if st.button('Enllaç al repositori'):
    webbrowser.open_new_tab(url)

#la taula de valors amb les dades que ens interessa mostrar
st.subheader('Taula de resultats')
st.write('Es mostraran dades entre el', idate, 'i el', fdate)
results = pd.DataFrame.from_records(results,columns=['act_dat_actuacio','tga_nom_grupo','tal_nom_alarma','municipi','nom_comarca','nom_regio','any'])
results['act_dat_actuacio'] = pd.Series([datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f').date() for date_time_str in results["act_dat_actuacio"]])

#filtrar resultats entre dates
start_date = idate
end_date = fdate
after_start_date = results["act_dat_actuacio"] >= start_date
before_end_date = results["act_dat_actuacio"] <= end_date
between_two_dates = after_start_date & before_end_date
results = results.loc[between_two_dates]

#pie chart
st.subheader('Grafic')
results_df=results
pc = list(results_df["tga_nom_grupo"])
occurrences = [pc.count(x) for x in pc]
res=pd.DataFrame({'Grup de Bombers': pc, 'Alertes':occurrences})
res=res.drop_duplicates(subset ="Grup de Bombers")
#print(res)
fig = px.pie(res, values='Alertes', names='Grup de Bombers')
st.plotly_chart(fig)

#sankey
st.subheader('Sankey diagram')
from sankey_diagram import draw_sankey
container = st.container()
all = st.checkbox("Select all")
if all:
    selected_options = container.multiselect("Select one or more options:",
         ['Centre', 'Girona', 'Lleida', 'Metropolitana Nord', 'Metropolitana Sud', 'Subdirecció General Operativa', 'Tarragona', "Terres de l'Ebre", "U.F. Val d'Aran" ],['Centre', 'Girona', 'Lleida', 'Metropolitana Nord', 'Metropolitana Sud', 'Subdirecció General Operativa', 'Tarragona', "Terres de l'Ebre", "U.F. Val d'Aran" ])
else:
    selected_options =  container.multiselect("Select one or more options:",
        ['Centre', 'Girona', 'Lleida', 'Metropolitana Nord', 'Metropolitana Sud', 'Subdirecció General Operativa', 'Tarragona', "Terres de l'Ebre", "U.F. Val d'Aran" ])
draw_sankey(results, selected_options)

##Distribució de tots els casos
st.subheader('Representació de totes les dades')

#mapa
with urlopen('https://raw.githubusercontent.com/sirisacademic/catalonia-cartography/master/shapefiles_catalunya_comarcas.geojson') as response:
	geojson = json.load(response)

pc = list(results_df["nom_comarca"])
#print(len(pc))
occurrences = [pc.count(x) for x in pc]
df=pd.DataFrame({'nom_comarca': pc, 'A':occurrences})
df1=df.drop_duplicates(subset=['nom_comarca'])
sum=df1["A"].sum(axis=0,skipna = True)
#df.astype({'codi_comarca': 'str'}).dtypes
fig = px.choropleth_mapbox(df1, geojson=geojson,featureidkey="properties.nom_comar", locations='nom_comarca',color='A',
                       	#color_continuous_scale="viridis",
                       	#range_color=(0, 500),
                       	mapbox_style="carto-positron",
                       	zoom=6.5, center = {"lat": 41.7, "lon": 2.2},
                       	opacity=0.5,
                       	labels={'A':'Opeartions in area'}
                      	)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.write('En aquest mapa es mostren els accidents corresponents a tots els casos, que conté ',sum,' casos.')
st.plotly_chart(fig)

#grafica de esdeveniments al llarg del temps
dates=results["act_dat_actuacio"]
alarms_per_date = dates.value_counts().sort_index()
df5=pd.DataFrame({'Data': alarms_per_date.index, 'Alarms':alarms_per_date})
fig = px.line(df5, x='Data', y="Alarms")
st.write('Ara es mostren les dades del mapa com a actuacions per dia')
st.plotly_chart(fig)

##Distribució d'una sola categoria
st.subheader('Representació de les dades del tipus seleccionat')

#mapa
cas = list(results_df["tga_nom_grupo"])
pc = list(results_df["nom_comarca"])
df=pd.DataFrame({'tga_nom_grupo': cas, 'nom_comarca':pc})
#df.groupby(["tga_nom_grupo", "nom_comarca"]).size()
df = df.groupby(["tga_nom_grupo", "nom_comarca"]).size().reset_index(name="Time")
df1 = df[df.tga_nom_grupo.str.contains(nom_grupo)]
sum=df1["Time"].sum(axis=0,skipna = True)
fig = px.choropleth_mapbox(df1, geojson=geojson,featureidkey="properties.nom_comar", locations='nom_comarca',color='Time',
                       	#color_continuous_scale="viridis",
                       	#range_color=(0, 200),
                       	mapbox_style="carto-positron",
                       	zoom=6.5, center = {"lat": 41.7, "lon": 2.2},
                       	opacity=0.5,
                       	labels={'Time':nom_grupo}
                      	)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.write('En aquest mapa es mostren els accidents corresponents a ','**',nom_grupo,'**, que conté ',sum,' casos.')
st.plotly_chart(fig)

#grafica de esdeveniments al llarg del temps
dates=list(results_df["act_dat_actuacio"])
df=pd.DataFrame({'tga_nom_grupo': cas, 'nom_comarca':pc, 'act_dat_actuacio':dates})
df = df[df.tga_nom_grupo.str.contains(nom_grupo)]
df1 = df.groupby(['act_dat_actuacio']).size().reset_index(name="Time")
fig = px.line(df1, x="act_dat_actuacio", y="Time")
st.write('Ara es mostren les dades del mapa com a actuacions per dia')
st.plotly_chart(fig)


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
