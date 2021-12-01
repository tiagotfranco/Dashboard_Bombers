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

#function to import the database
@st.cache(allow_output_mutation=True)
def db(lim):
    client = Socrata("analisi.transparenciacatalunya.cat", None)
    database = client.get('g2ay-3vnj',limit=lim)
    return database

database=db(lim)

#results = pd.read_csv("Actuacions_dels_Bombers_de_la_Generalitat.csv")
st.title('Actions of the Generalitat Fire Brigade')
st.write("By Pablo Candelas, Joan Falcón, Tiago Franco, David Pujols.")
st.write('In this database the data will be frow between', idate, 'and', fdate,', and will contain',lim,'columns of data.')
#button with the link to the location of the data
url='https://analisi.transparenciacatalunya.cat/Seguretat/Actuacions-dels-Bombers-de-la-Generalitat/g2ay-3vnj'
url2="https://github.com/tiagotfranco/Dashboard_Bombers"
col1,col2,col3,col4,col5=st.columns(5)
with col1:
    if st.button('Link to the database'):
        webbrowser.open_new_tab(url)
with col2:
    if st.button('Link to the github'):
        webbrowser.open_new_tab(url2)
with col3:
    " "
with col4:
    " "
with col5:
    " "
st.subheader("Abstract")
st.write("Firefighters are an essential part of our community. They are responsible for extinguishing fires, getting people out of terrible car accidents, rescuing lost people and animals and many other important tasks. Our aim with this dashboard is to increase awareness on the vital role firefighters play. There are eleven departments answering emergencies throughout the Generalitat. We present a map with the number of alarms on the territory, observing an anormal higher density of alarms for Vallès Occidental and Baix Llobregat. To delve deeper, we analyze the map considering only specific departments, which allows us to infer from them some qualitative facts of the territory. Finally, we analyze the activity of specific departments through time and discover some interesting facts, like a yearly periodic cycle on many of the departments or the spike in January of 2020 pertaining to technical assistance. We expect that, after going through this dashboard, you will have a clear idea of how important firefighters are.")


#creation of the dataframe with the columns we need and between the selected dates


@st.cache(allow_output_mutation=True)
def db_dat(idate,fdate,database):
    results = pd.DataFrame.from_records(database,columns=['act_dat_actuacio','tga_nom_grupo','tal_nom_alarma','municipi','nom_comarca','nom_regio','any'])
    results['act_dat_actuacio'] = pd.Series([datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S.%f').date() for date_time_str in results["act_dat_actuacio"]])
    start_date = idate
    end_date = fdate
    after_start_date = results["act_dat_actuacio"] >= start_date
    before_end_date = results["act_dat_actuacio"] <= end_date
    between_two_dates = after_start_date & before_end_date
    results = results.loc[between_two_dates]
    return results

results=db_dat(idate,fdate,database)

#pie chart
st.subheader('Pie chart')
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
switch=False
if st.button('Switch Action with Departments'):
    if switch == False:
        switch=True
    elif switch == True:
        switch=False
st.write(switch)
from sankey_diagram import draw_sanke
container = st.container()
all = st.checkbox("Select all")
if all:
    selected_options = container.multiselect("Select one or more options:",
         ['Centre', 'Girona', 'Lleida', 'Metropolitana Nord', 'Metropolitana Sud', 'Subdirecció General Operativa', 'Tarragona', "Terres de l'Ebre", "U.F. Val d'Aran" ],['Centre', 'Girona', 'Lleida', 'Metropolitana Nord', 'Metropolitana Sud', 'Subdirecció General Operativa', 'Tarragona', "Terres de l'Ebre", "U.F. Val d'Aran" ])
else:
    selected_options =  container.multiselect("Select one or more options:",
        ['Centre', 'Girona', 'Lleida', 'Metropolitana Nord', 'Metropolitana Sud', 'Subdirecció General Operativa', 'Tarragona', "Terres de l'Ebre", "U.F. Val d'Aran" ])
fig2=draw_sanke(results,selected_options,switch)
st.plotly_chart(fig2)
##Distribució de tots els casos
st.subheader('Representation of all the data by location')

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
st.write('This map contains all the incidences, adding up to ',sum,' cases.')
st.plotly_chart(fig)
st.subheader('Representation of all the data by date')
#grafica de esdeveniments al llarg del temps
dates=results["act_dat_actuacio"]
alarms_per_date = dates.value_counts().sort_index()
df5=pd.DataFrame({'Date': alarms_per_date.index, 'Alarms':alarms_per_date})
fig = px.line(df5, x='Date', y="Alarms")
st.write('Now the same data but ordered by date')
st.plotly_chart(fig)

##Distribució d'una sola categoria
st.subheader('Representation of the data from the selected type by location')

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
st.write('In this map we show the incidents from the group ','**',nom_grupo,'**, containing ',sum,' cases.')
st.plotly_chart(fig)
st.subheader('Representation of the data from the selected type by date')
#grafica de esdeveniments al llarg del temps
dates=list(results_df["act_dat_actuacio"])
df=pd.DataFrame({'tga_nom_grupo': cas, 'nom_comarca':pc, 'act_dat_actuacio':dates})
df = df[df.tga_nom_grupo.str.contains(nom_grupo)]
df1 = df.groupby(['act_dat_actuacio']).size().reset_index(name="Time")
fig = px.line(df1, x="act_dat_actuacio", y="Time")
st.write('Now the same data but ordered by date')
st.plotly_chart(fig)

st.header("Conclusions")
st.write("We had the data of all the actuations of the firefighters in the last years, so we classified it with different criteria, in order to extract som patterns or interesting information from the data. We have seen that both the number and type of actuations vary a lot over the different regions of the territory, and also over the year they have very different numbers. We have found out that usually, the peaks of activity are periodic and related to national events, like the 24th of June or the 5th of January, and the general behaviour from one year to the next one is similar. However, sometimes there can be an unexpected cause of a great peak or low, like during the Gloria or because of covid. With all of this in mind, we can assume that due to the periodic behaviour over the years, the firefighter can already be prepared for quite a lot of the actuations they will have to do. However, they will need some degree of adaptability for unexpected situations like the ones lived recently. As a last remark, making an analysis of this kind with the data can prove of a great use for the firefighters to know of this regularity, so this is a great application of data analysis and visualisation.")
# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")
