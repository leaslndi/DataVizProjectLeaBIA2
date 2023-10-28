# Léa Sellahannadi - BIA2 - Data Vizualisation Project 
# Import the librairies I plan to use (of course I wrote even those I didnt even use)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import altair as alt
import streamlit as st
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, ColorBar
from bokeh.layouts import column
from bokeh.palettes import Category10, Spectral11
from bokeh.transform import factor_cmap
from bokeh.models.tools import HoverTool
from bokeh.models import Slider
from bokeh.plotting import show
import plotly.graph_objects as go
import time

# My personal information on the side bar 
with st.sidebar:
    st.title("Information:")
    st.write(""" **Léa Sellahannadi - M1 BIA2 - EFREI PARIS** """)
    st.subheader("#dataviz2023efrei")
    st.markdown("[GitHub](https://github.com/leaslndi)")
    st.markdown("[LinkedIn](https://linkedin.com/in/léa-sellahannadi-8935511b6)")

# Header with problem statement and target audience
st.title("SCHOOLS IN FRANCE")
st.write("""
Are you are student, a parent, or even someone interested in understanding how local schools are situated compared to others in France in terms of the Social Position Index (IPS)? Well, this dashboard is for you! 
""")

# Our variables

st.subheader('Description des données')
st.write("""
    - **Rentrée scolaire** (`rentree_scolaire`): Year on which the indices are based
    - **Académie** (`academie`): Academy to which the establishment belongs
    - **Département** (`departement`): Department code to which the establishment belongs
    - **UAI** (`uai`): Establishment identification number
    - **Nom de l'établissement** (`nom_de_l_etablissment`): Name of the establishment
    - **Secteur** (`secteur`): Public establishment or private establishment
    - **IPS** (`ips`): Social position index of the students of the establishment
""")

# I load the dataset to understand and explore the dataset before analysis
@st.cache_data
def load_dataset():
    return pd.read_csv('fr-en-ips_ecoles_v2.csv', delimiter=';')
df = load_dataset()
st.subheader("Data source ")
st.markdown("[Data.gouv.fr](https://www.data.gouv.fr/fr/datasets/indices-de-position-sociale-dans-les-ecoles-de-france-metropolitaine-et-drom-version-2-1/)")
st.dataframe(df)

# I then do the data processing because there a missing values, unknown values, duplicates...alt
df['nom_de_l_etablissment'].fillna('INCONNU', inplace=True)
df['nom_de_l_etablissment'].replace(['A COMPLETER', 'ECOLE PRIMAIRE', 'ECOLE ELEMENTAIRE'], 'INCONNU', inplace=True)
df_unique_uai = df.drop_duplicates(subset='uai', keep='first')

# To make our plots easier I decide to calculate the percentiles 25 et 75 for the IPS
percentile_25 = df['ips'].quantile(0.25)
percentile_75 = df['ips'].quantile(0.75)

# I even created a new column called categories_ips
df['categorie_ips'] = 'moyen'
df.loc[df['ips'] < percentile_25, 'categorie_ips'] = 'faible'
df.loc[df['ips'] > percentile_75, 'categorie_ips'] = 'élevé'

# Let's explore the data now 

# Personalized colours
custom_colors1 = ["#FF5733", "#33FF57"]
custom_colors2 = ["#7791EF", "#DD77EF"]
custom_colors3 = ["#DAF7A6", "#FFC300"]

st.subheader('School distribution')
# I want to created interactive buttons
button1 = st.button("Academy")
button2 = st.button("Department")
button3 = st.button("Public vs Private")

if button1:
    data = df_unique_uai['academie'].value_counts().reset_index()
    data.columns = ['Academy', 'Number of Schools']
    fig = px.pie(data, names='Academy', values='Number of Schools', hole=0.3, color_discrete_sequence=custom_colors1)
    st.plotly_chart(fig)

elif button2:
    data = df_unique_uai['departement'].value_counts().reset_index()
    data.columns = ['Department', 'Number of Schools']
    fig = px.bar(data, x='Department', y='Number of Schools', title="Number of schools by Department", color_discrete_sequence=custom_colors2)
    st.plotly_chart(fig)

elif button3:
    secteur_counts = df_unique_uai['secteur'].value_counts()
    fig = px.pie(names=secteur_counts.index, values=secteur_counts.values, title='Distribution of Schools by Sector', color_discrete_sequence=custom_colors3)
    st.plotly_chart(fig)


grouped_data = df.groupby(['rentree_scolaire', 'secteur']).size().unstack()

st.subheader('Evolution of the number of schools by sector over time')
st.line_chart(grouped_data)

st.subheader('Distribution of schools by academy')
academy_counts = df_unique_uai['academie'].value_counts()
st.bar_chart(academy_counts)

st.subheader('Distribution of Schools by Sector')
secteur_counts = df['secteur'].value_counts()
st.bar_chart(secteur_counts)

st.subheader('Distribution of Schools by Sector in Each Academy')

selected_academy = st.selectbox('Choose an academy:', df['academie'].unique())

df_academy = df[df['academie'] == selected_academy]
sector_counts = df_academy['secteur'].value_counts()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=sector_counts.index,
    y=sector_counts.values,
    marker_color=['pink', 'blue']
))
fig.update_layout(title=f'Distribution of Schools by Sector in {selected_academy}',
                  xaxis=dict(title='Sector'),
                  yaxis=dict(title='Number of Schools'))

st.plotly_chart(fig)


st.header("IPS ANALYSIS")
st.subheader('IPS distribution')
selected_year = st.selectbox('Choose an academic year:', df['rentree_scolaire'].unique(), key='selected_year_key')
df_year = df[df['rentree_scolaire'] == selected_year]
plt.figure(figsize=(12, 6))
sns.histplot(df_year['ips'], kde=True, color="dodgerblue")
plt.title(f"IPS Distribution in the Academic Year {selected_year}")
plt.xlabel("IPS")
plt.ylabel("Density")
st.pyplot(plt)

st.subheader("Average IPS in an academy by year")
selected_year_ips = st.select_slider('Choose a school year:', df['rentree_scolaire'].unique())

# The calculation of the average of IPS for the selected year
df_year_ips = df[df['rentree_scolaire'] == selected_year_ips]
avg_ips_per_academie = df_year_ips.groupby('academie')['ips'].mean().reset_index()

fig_ips = px.bar(avg_ips_per_academie, 
                 x='academie', 
                 y='ips', 
                 color='academie', 
                 title=f"Average IPS by Academy for the year {selected_year_ips}",
                 color_discrete_sequence=px.colors.qualitative.Set1)  
st.plotly_chart(fig_ips)

st.subheader("Distribution of schools by IPS category")
ips_category_counts = df['categorie_ips'].value_counts().reset_index()
ips_category_counts.columns = ['IPS Category', 'Number of Schools']
colors = {'faible': 'pink', 'moyen': 'yellow', 'élevé': 'blue'}

fig_ips_category = px.pie(ips_category_counts,
                          names='IPS Category',
                          values='Number of Schools',
                          title="Distribution of Schools by IPS Category",
                          color='IPS Category',
                          color_discrete_map=colors,
                          hole=0.6)
fig_ips_category.update_traces(textinfo='percent+label', pull=[0.1, 0.1, 0.1])
st.plotly_chart(fig_ips_category)

st.subheader("The evolution of the average IPS over time for different academies")

df['rentree_scolaire'] = df['rentree_scolaire'].astype(str)
df['rentree_scolaire'] = df['rentree_scolaire'].str.split('-').str[0].astype(int)

default_academies = ["BORDEAUX", "PARIS"]
selected_academies = st.multiselect('Choose academies to compare:', df['academie'].unique(), default=default_academies)
df_selected = df[df['academie'].isin(selected_academies)]
df_grouped = df_selected.groupby(['rentree_scolaire', 'academie'])['ips'].mean().reset_index()

p = figure(width=600, height=400, title='Evolution of the Average IPS over Time')
p.title.text_font_size = '14pt'
hover = HoverTool()
hover.tooltips = [("Academy", "@academie"),
                      ("Academic Year", "@rentree_scolaire"),
                      ("IPS", "@ips")]
p.add_tools(hover)

for i, academy in enumerate(selected_academies):
    subset = df_grouped[df_grouped['academie'] == academy]
    source = ColumnDataSource(subset)
    p.line('rentree_scolaire', 'ips', source=source, line_width=2, color=Category10[10][i], legend_label=academy)
    p.circle('rentree_scolaire', 'ips', source=source, fill_color=Category10[10][i], size=6)

p.legend.location = "top_left"
p.legend.click_policy = "hide"
p.xaxis.axis_label = "Academic Year"
p.yaxis.axis_label = "IPS"
st.bokeh_chart(p)

st.subheader("Evolution of the maximum and minimum IPS over time by academy")
selected_academy = st.selectbox('Choose an academy:', df['academie'].unique(), key='unique_key_for_this_selectbox')

df_academy = df[df['academie'] == selected_academy]
df_grouped = df_academy.groupby('rentree_scolaire').agg({'ips': ['min', 'max']}).reset_index()
df_grouped.columns = ['rentree_scolaire', 'ips_min', 'ips_max']

fig = px.scatter(df_grouped,
                 x='rentree_scolaire',
                 y='ips_min',
                 size='ips_max',
                 color='ips_min',
                 hover_data=['ips_min', 'ips_max'],
                 title=f"Evolution of the min and max of IPS for the Academy of {selected_academy} over Time",
                 labels={'ips_min': 'IPS Min', 'ips_max': 'IPS Max', 'rentree_scolaire': 'Academic Year'},
                 color_continuous_scale='Mint',
                 size_max=15)

fig.update_traces(marker=dict(symbol='triangle-up'))
st.plotly_chart(fig)








