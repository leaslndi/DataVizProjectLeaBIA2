import time
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt


# Page Configuration
st.set_page_config(
    page_title="Explorateur de la consommation de gaz naturel en Europe",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown("""
    <style>
        .reportview-container {
            background: #E6F0FA;  
        }
    </style>
    """, unsafe_allow_html=True)

st.title("Explorateur de la consommation de gaz en Europe 🌍🔥")

# Introduction
col1, _ = st.columns(2)
with col1:
    st.write("""
    Cet outil vise à aider les chercheurs, les étudiants et tous ceux qui s'intéressent à comprendre comment les pays d'Europe consomment le gaz naturel. Vous pourrez explorer 📊 l'évolution de la consommation au fil du temps et comparer 🔍 différents pays.
    """)

    st.subheader('Description des données 📝')
    st.write("""
    - 📅 **Année de référence** (`annee_de_reference`): L'année concernée.
    - 🇪🇺 **Pays** (`pays`): Le pays en Europe.
    - 🔥 **Consommation finale de gaz naturel** (`consommation_finale_de_gaz_naturel_mtep`): Consommation de gaz en Mtep.
    - 📈 **Consommation totale d'énergie** (`consommation_finale_d_energie_totale_mtep`): Consommation totale d'énergie en Mtep.
    """)


# Sidebar
with st.sidebar:
    st.title("About the author")
    st.write("""
    **Léa Sellahannadi**

    In the module Data Visualization, I created this dashboard with Streamlit
    """)
    st.subheader("#dataVizEurope2023")
    # Links to GitHub and LinkedIn
    st.markdown("[🔗 GitHub](https://github.com/leaslndi)") 
    st.markdown("[🔗 LinkedIn](https://linkedin.com/in/léa-sellahannadi-8935511b6)")


# Load the dataset
@st.cache_data
def load_dataset():
    url = 'https://odre.opendatasoft.com/explore/dataset/part-du-gaz-naturel-dans-la-consommation-finale-denergie-en-europe/download?format=csv&timezone=Europe/Berlin&use_labels_for_header=false'
    data = pd.read_csv(url, delimiter=';')
    return data

df = load_dataset()

st.subheader("Source de données")
st.markdown("[🔗 Data.gouv.fr](https://www.data.gouv.fr/fr/datasets/)")
st.dataframe(df.head(5))

# Data preprocessing
# UE 27 et UE 28 are not useful here 
filtered_data = df[~df['pays'].isin(['UE 27', 'UE 28'])]
filtered_data.reset_index(drop=True, inplace=True)

# Data Exploration
st.header('Exploration des données 🔍')


# External plot using Plotly (Bar plot)

# Filter data for the years 2020 and 2021
data_2020_2021 = filtered_data[filtered_data['annee_de_reference'].isin([2020, 2021])]

# Determine the order of countries based on their total energy consumption in 2020
ordered_countries = data_2020_2021[data_2020_2021['annee_de_reference'] == 2020].sort_values(by='consommation_finale_d_energie_totale_mtep', ascending=False)['pays'].tolist()

# Interactive button to select year
selected_year = st.selectbox('Select Year:', [2020, 2021])

# Display bar plot for the selected year
st.subheader(f'Total Energy Consumption by Country in {selected_year}')

fig = px.bar(data_2020_2021[data_2020_2021['annee_de_reference'] == selected_year],
             x='pays',
             y='consommation_finale_d_energie_totale_mtep',
             title=f'Total Energy Consumption by Country in {selected_year}',
             labels={'pays': 'Country', 'consommation_finale_d_energie_totale_mtep': 'Total Energy Consumption (Mtep)'},
             category_orders={"pays": ordered_countries})

st.plotly_chart(fig)

#HAHAHAHAHA

ordered_countries = data_2020_2021[data_2020_2021['annee_de_reference'] == 2020].sort_values(by='consommation_finale_d_energie_totale_mtep', ascending=True)['pays'].tolist()

# Display horizontal bar plot for the years 2020 and 2021
st.subheader('Consommation totale d\'énergie par pays en 2020 et 2021')

fig = px.bar(data_2020_2021,
             y='pays',
             x='consommation_finale_d_energie_totale_mtep',
             title='Consommation totale d\'énergie par pays en Europe (2020 et 2021)',
             labels={'pays': 'Pays', 'consommation_finale_d_energie_totale_mtep': 'Consommation totale d\'énergie (Mtep)'},
             color='annee_de_reference',
             orientation='h',
             category_orders={"pays": ordered_countries})

fig.update_layout(barmode='group')

st.plotly_chart(fig)

# Altair Bar Chart for Natural Gas Consumption by Year
# Interactive dropdown to select the year
selected_gas_year = st.selectbox('Select Year for Natural Gas Consumption Plot:', filtered_data['annee_de_reference'].unique())

# Filter the data for the selected year
year_gas_data = filtered_data[filtered_data['annee_de_reference'] == selected_gas_year]

# Sort the data by natural gas consumption
sorted_gas_data = year_gas_data.sort_values(by='consommation_finale_de_gaz_naturel_mtep', ascending=True)

# Altair Bar Chart
gas_chart = alt.Chart(sorted_gas_data).mark_bar().encode(
    y=alt.Y('pays:N', sort='-x', title='Country'),
    x=alt.X('consommation_finale_de_gaz_naturel_mtep:Q', title='Natural Gas Consumption (Mtep)'),
    color=alt.Color('pays:N', legend=None),
    tooltip=['pays', 'consommation_finale_de_gaz_naturel_mtep']
).properties(
    title=f'Natural Gas Consumption by Country in {selected_gas_year}'
)

st.altair_chart(gas_chart, use_container_width=True)


# Trend Over Time for a Specific Country

# Interactive multi-select box to choose countries
selected_countries = st.multiselect('Select countries:', filtered_data['pays'].unique())

# Filter the data for selected countries
country_data = filtered_data[filtered_data['pays'].isin(selected_countries)]

# Plot the line chart
fig = px.line(country_data, 
              x='annee_de_reference', 
              y='consommation_finale_de_gaz_naturel_mtep', 
              color='pays',
              title='Trend of Natural Gas Consumption Over Time',
              labels={'annee_de_reference': 'Year', 'consommation_finale_de_gaz_naturel_mtep': 'Natural Gas Consumption (Mtep)', 'pays': 'Country'})

st.plotly_chart(fig)

fig = px.bar(filtered_data, 
             x='pays', 
             y='consommation_finale_de_gaz_naturel_mtep', 
             title='Consommation de Gaz par Pays en Europe en {selected_gas_year}',
             labels={'pays': 'Pays', 'consommation_finale_de_gaz_naturel_mtep': 'Consommation de Gaz (MTep)'})
fig.update_xaxes(title_text='Pays')
fig.update_yaxes(title_text='Consommation de Gaz (MTep)')
st.plotly_chart(fig, use_container_width=True)

fig = px.choropleth(filtered_data, 
                    locations='label_en',
                    locationmode='country names', 
                    color='consommation_finale_de_gaz_naturel_mtep',
                    title='Consommation de Gaz par Pays en Europe en {selected_gas_year}',
                    color_continuous_scale=px.colors.sequential.YlOrRd,  
                    range_color=(0, 55000),  
                    scope='europe',
                    labels={'consommation_finale_de_gaz_naturel_mtep': 'Consommation de gaz'})
st.plotly_chart(fig)

# Sélectionnez la donnée à afficher
choix = st.radio("Sélectionnez la donnée à afficher :", ['consommation_finale_d_energie_totale_mtep', 'consommation_finale_de_gaz_naturel_mtep'])

# Créez deux colonnes pour les graphiques côte à côte
col1, col2 = st.columns(2)

# Graphique pour l'année 2020
with col1:
    st.title(f"Répartition de la {choix.replace('_', ' ').capitalize()} par Pays en 2020")
    
    # Filtrez les données pour l'année 2020
    data_2020 = filtered_data[filtered_data['annee_de_reference'] == 2020]
    
    # Regroupez les données par pays et calculez la somme de la variable choisie
    data_grouped = data_2020.groupby('pays')[choix].sum()
    
    # Créez le graphique à secteurs
    plt.figure(figsize=(8, 8))
    plt.pie(data_grouped)
    plt.axis('equal')
    
    # Créez la légende
    legende_texte = [f"{pays}: {valeur:.2f}" for pays, valeur in zip(data_grouped.index, data_grouped)]
    plt.legend(legende_texte, title='Pays', loc='upper left', bbox_to_anchor=(1, 1))
    
    st.pyplot(plt)

# Graphique pour l'année 2021
with col2:
    st.title(f"Répartition de la {choix.replace('_', ' ').capitalize()} par Pays en 2021")
    
    # Filtrez les données pour l'année 2021
    data_2021 = filtered_data[filtered_data['annee_de_reference'] == 2021]
    
    # Regroupez les données par pays et calculez la somme de la variable choisie
    data_grouped = data_2021.groupby('pays')[choix].sum()
    
    # Créez le graphique à secteurs
    plt.figure(figsize=(8, 8))
    plt.pie(data_grouped)
    plt.axis('equal')
    
    # Créez la légende
    legende_texte = [f"{pays}: {valeur:.2f}" for pays, valeur in zip(data_grouped.index, data_grouped)]
    plt.legend(legende_texte, title='Pays', loc='upper left', bbox_to_anchor=(1, 1))
    
    st.pyplot(plt)


st.title("Evolution du pourcentage de consommation de gaz dans chaque pays")

# Sélectionnez un pays à partir d'une liste déroulante
pays_selectionne = st.selectbox("Sélectionnez un pays :", filtered_data['pays'].unique())

# Filtrer les données pour le pays sélectionné
data_pays = filtered_data[filtered_data['pays'] == pays_selectionne]

# Filtrer les données pour les années 2020 et 2021
data_20 = data_pays[data_pays['annee_de_reference'] == 2020]
data_21 = data_pays[data_pays['annee_de_reference'] == 2021]

# Vérifiez si les données sont vides et attribuez une valeur par défaut
pourcentage_2020 = data_20['part_du_gaz_naturel_dans_la_consommation_finale_d_energie0'].values[0] if not data_20.empty else 0.0
pourcentage_2021 = data_21['part_du_gaz_naturel_dans_la_consommation_finale_d_energie0'].values[0] if not data_21.empty else 0.0  

# Créez un graphique à barres
fig, ax = plt.subplots(figsize=(3, 3))
ax.bar(['2020', '2021'], [pourcentage_2020, pourcentage_2021], color=['blue', 'green'])
ax.set_ylabel('Pourcentage de Consommation')
ax.set_title(f'Pourcentage de Consommation de Gaz en {pays_selectionne} en 2020 et 2021')

# Affichez le graphique
st.pyplot(fig)
