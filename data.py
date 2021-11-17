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

client = Socrata("analisi.transparenciacatalunya.cat", None)
results = client.get('g2ay-3vnj',limit=20000)
#results = pd.read_csv("Actuacions_dels_Bombers_de_la_Generalitat.csv")
st.title('Actuacions dels bombers')

#creació d'un enllaç a l'origen de les dades
url='https://analisi.transparenciacatalunya.cat/Seguretat/Actuacions-dels-Bombers-de-la-Generalitat/g2ay-3vnj'
if st.button('Enllaç del repositori'):
    webbrowser.open_new_tab(url)
#sidebar
idate= st.sidebar.date_input('data inicial', dtime.date(2015,1,1))
fdate= st.sidebar.date_input('data final', dtime.date.today())

nom_grupo= st.sidebar.selectbox(
    "Que tipo de incidencia quieres ver?",
    ("assistència tècnica","salvaments","incendi urbà","activitat no urgent","mobilitat","pràctiques","incendi vegetació","dispositiu preventiu","fuites perilloses","suport tècnic","simulacres")
)

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
#results

#aqui estan contades les diferents coses
#st.subheader('Recompte tipus de incidencies')
res=pd.DataFrame.from_records(results,columns=['tga_nom_grupo']).value_counts()
#res

#pie chart
st.subheader('Grafic')
pie=results["tga_nom_grupo"].value_counts().plot(kind = 'pie')
pie.figure










results_df=results

#mapa
dates=results["act_dat_actuacio"]
alarms_per_date = dates.value_counts().sort_index()
df5=pd.DataFrame({'Data': alarms_per_date.index, 'Alarms':alarms_per_date})
fig = px.line(df5, x='Data', y="Alarms")
st.plotly_chart(fig)


#grafica
with urlopen('https://raw.githubusercontent.com/sirisacademic/catalonia-cartography/master/shapefiles_catalunya_comarcas.geojson') as response:
	geojson = json.load(response)

pc = list(results_df["nom_comarca"])
#print(len(pc))
occurrences = [pc.count(x) for x in pc]
df=pd.DataFrame({'nom_comarca': pc, 'A':occurrences})
#df.astype({'codi_comarca': 'str'}).dtypes

fig = px.choropleth_mapbox(df, geojson=geojson,featureidkey="properties.nom_comar", locations='nom_comarca',color='A',
                       	#color_continuous_scale="viridis",
                       	#range_color=(0, 500),
                       	mapbox_style="carto-positron",
                       	zoom=6.5, center = {"lat": 41.7, "lon": 2.2},
                       	opacity=0.5,
                       	labels={'A':'Opeartions in area'}
                      	)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)

#mapa 2
st.write('En aquest mapa es mostren els accidents corresponents a ','**',nom_grupo,'**.')
cas = list(results_df["tga_nom_grupo"])
pc = list(results_df["nom_comarca"])
df=pd.DataFrame({'tga_nom_grupo': cas, 'nom_comarca':pc})
#df.groupby(["tga_nom_grupo", "nom_comarca"]).size()

df = df.groupby(["tga_nom_grupo", "nom_comarca"]).size().reset_index(name="Time")
df1 = df[df.tga_nom_grupo.str.contains(nom_grupo)]
fig = px.choropleth_mapbox(df1, geojson=geojson,featureidkey="properties.nom_comar", locations='nom_comarca',color='Time',
                       	#color_continuous_scale="viridis",
                       	#range_color=(0, 200),
                       	mapbox_style="carto-positron",
                       	zoom=6.5, center = {"lat": 41.7, "lon": 2.2},
                       	opacity=0.5,
                       	labels={'Time':nom_grupo}
                      	)
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)


# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
