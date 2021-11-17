#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 16:02:07 2021

@author: tiagofranco
"""

### Sankey Diagram in streamlit with 

import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected=True)
from sodapy import Socrata # Was not in the installation list for this course!
                           # Use "pip install sodapy" or "conda install sodapy" to install
#from plots.geo_plot_vaccines import plot_abundance_for_list_of_postal_codes

"variables"
scraping_depth = 200

"download data"
# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("analisi.transparenciacatalunya.cat", None)
#print("Format of dataset: ", type(client))
# Actuacions dels Bombers de la Generalitat - Dataset Identifier: g2ay-3vnj
all_info = client.get("g2ay-3vnj", limit=scraping_depth)

# Convert to pandas DataFrame
all_info_df = pd.DataFrame.from_records(all_info)

#Get nodes dataframe with Label and Color columns
#     Label
nom_regio_df = pd.DataFrame.from_dict(all_info_df['nom_regio'].unique())
tga_nom_grupo_df = pd.DataFrame.from_dict(all_info_df['tga_nom_grupo'].unique())
tga_nom_alarma_df = pd.DataFrame.from_dict(all_info_df['tal_nom_alarma'].unique())

nodes_df = pd.concat([nom_regio_df,tga_nom_grupo_df,tga_nom_alarma_df], ignore_index=True)
nodes_df = nodes_df.rename(columns={0 : 'Label'})

#     Color
ncolors = []
for i in range(len(nodes_df)):
    ncolors += ['rgba('+str(np.random.randint(256))+','+str(np.random.randint(256))+','+str(np.random.randint(256))+',0.99)']    
nodes_df.insert(1, 'Color', ncolors)


#Get links dataframe with Source, Target, Value and Color columns
links1_df = all_info_df.filter(items=['nom_regio','tga_nom_grupo'])
links2_df = all_info_df.filter(items=['tga_nom_grupo','tal_nom_alarma'])
links1_df = links1_df.rename(columns={'nom_regio':'Source', 'tga_nom_grupo':'Target'})
links2_df = links2_df.rename(columns={'tga_nom_grupo':'Source','tal_nom_alarma':'Target'})
links_df = pd.concat([links1_df,links2_df], ignore_index=True)


lvalues = []
lcolors = []
for i in range(len(links_df)): 
    source_index = nodes_df.index[nodes_df['Label']==links_df.at[i,'Source']].tolist()[0]
    target_index = nodes_df.index[nodes_df['Label']==links_df.at[i,'Target']].tolist()[0]
    lvalues += [1]
    lcolors += [nodes_df.at[source_index, 'Color'].replace('0.99','0.4')]
    links_df.at[i,'Source'] = source_index
    links_df.at[i,'Target'] = target_index
links_df.insert(2,'Value', lvalues)
links_df.insert(3,'Color', lcolors)



# Sankey plot setup
data_trace = dict(
    type='sankey',
    domain = dict(
      x =  [0,1],
      y =  [0,1]
    ),
    orientation = "h",
    valueformat = ".0f",
    node = dict(
      pad = 10,
    # thickness = 30,
      line = dict(
        color = "black",
        width = 1
      ),
      label =  nodes_df['Label'].dropna(axis=0, how='any'),
      color = nodes_df['Color'].dropna(axis=0, how='any')
    ),
    link = dict(
      source = links_df['Source'].dropna(axis=0, how='any'),
      target = links_df['Target'].dropna(axis=0, how='any'),
      value = links_df['Value'].dropna(axis=0, how='any'),
      color = links_df['Color'].dropna(axis=0, how='any'),
  )
)

layout = dict(
        title = "Sankey Diagram from Actuacions dels Bombers",
    height = 772,
    font = dict(
      size = 10),)

fig = dict(data=[data_trace], layout=layout)
iplot(fig, validate=False)