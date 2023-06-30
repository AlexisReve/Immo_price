import pandas as pd 
import numpy as np
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import folium
import streamlit.components.v1 as components
import plotly.express as px
import pickle

st.set_page_config(layout = 'wide')

@st.cache_data
def load_data():
    data = pd.read_csv("immo/TGV.csv", sep=";")
    return data


@st.cache_data()
def get_golden_map():
  HtmlFile = open("map.html", 'r', encoding='utf-8')
  bcn_map_html = HtmlFile.read()
  return bcn_map_html

def main():
    global data

    data = load_data()

    st.title("Tableau de Bord Prix Immobiliers")
    bcn_map_html = get_golden_map()
    with st.container():
        st.subheader("Prix Immobiliers par Commune en 2021")
        components.html(bcn_map_html,width=1000, height=500)

    st.subheader("Analyse par Année")
    with st.container():
        year = st.selectbox("Année", data["Annee"].unique().tolist())

    col1, col2 = st.columns(2)
    data_filtered = data.copy()
    data_filtered = data_filtered[data_filtered["Annee"]==year]
    with col1:
        prix = data_filtered["Prixm2Moyen"].mean()
        max_prix = data_filtered["Prixm2Moyen"].max()
        commune_max_prix = data_filtered.loc[data_filtered["Prixm2Moyen"].idxmax(), "Commune"]
        commune_min_prix = data_filtered.loc[data_filtered["Prixm2Moyen"].idxmin(), "Commune"]
        min_prix = data_filtered["Prixm2Moyen"].min()
        max_trans = data_filtered["Nb_mutations"].max()
        commune_max_trans = data_filtered.loc[data_filtered["Nb_mutations"].idxmax(), "Commune"]

        st.write("Prix m2 Moyen : {:,.0f} €".format(prix))
        st.write("Prix m2 Max : {:,.0f} € ({} pour {} vente(s))".format(max_prix, commune_max_prix, data_filtered.loc[data_filtered["Prixm2Moyen"].idxmax(), "Nb_mutations"]))
        st.write("Prix m2 Min : {:,.0f} € ({} pour {} vente(s))".format(min_prix, commune_min_prix, data_filtered.loc[data_filtered["Prixm2Moyen"].idxmin(), "Nb_mutations"]))
        st.write("Plus grand nombre de ventes immobilières : {:,.0f}, ({})".format(max_trans, commune_max_trans))

    with col2:
        table = data_filtered[["TGV"]]
        table = table.apply(pd.Series.value_counts)#.loc[["Pas de gare", "Gare TGV", "Gare voyageurs non TGV"]]
        table["Somme"] = table.sum(axis=1, skipna=True, numeric_only=True)
        fig = px.pie(table, values='Somme', names=table.index)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Prédisez votre prix :")
    
    text = '''Attention, les résultats délivrés par le modèle ne peuvent être représentatif de la réalité.
            Ce modèle à été construit à partir des bases de données de valeurs foncières disponibles sur la
            plateformeData.gouv (2014-2021), les données concernent uniquement les transactions immobilières et ne
            sont donc pas forcément représentatif du parc immobilier de chaque commune. En particulier lorsque le 
            prix au m2 par commune est calculé sur un faible nombre de transactions immobilières. Les bases Demandes de
            valeurs foncières ne sont pas suffisantes pour le cas d'usage de prédiction de prix. Celles-ci doivent être
            enrichies d'autres données telles que des indicateurs de qualité de vie (nombre de délits, accès aux soins) ou
            des indicateurs d'activité (taux de chômage, nombre d'entreprise). Si un premier travail de fusion de plusieurs
            bases de données (listes gares sncf, taux de chômage par commune) a été effectué par nos soins, nous restons
            tributaires de la disponibilité et de la qualité des données. Nous encourageons donc l'ensemble des acteurs
            publiques et privés à travailler en étroite collaboration afin de mettre à disposition de nouvelles données
            au citoyen.'''
    st.info(text)
    st.info("")
    with st.form(key = 'my_form'):
        with st.container():
            col3, col4, col5, col6 = st.columns(4)

            with col3:
                Input_Maisons = st.number_input("Nombre de maisons vendues")

            with col4:
                Input_appart = st.number_input("Nombre d'appartements vendues")
            
            with col5:
                Input_surface = st.number_input("Surface Moyenne")

            with col6:
                Input_gare = st.selectbox("Gare", data["TGV"].unique().tolist())
            
            col7, col8, col9 = st.columns(3)

            with col8:
                submitted = st.form_submit_button("Appliquer les filtres")

    if submitted:
        input = [Input_Maisons, Input_appart, Input_surface]

        with open('modele_xgboost.pkl', 'rb') as file:
            model = pickle.load(file)

        input_pas_gare = 1 if Input_gare == "Pas de gare" else 0
        input_tgv = 1 if Input_gare == "Gare TGV" else 0
        input_gare_voyageur = 1 if Input_gare == "Gare voyageurs non TGV" else 0
        new_data = input + [input_pas_gare, input_gare_voyageur, input_tgv]
        new_data = np.reshape(new_data, (1,-1))
        predictions = pd.DataFrame(model.predict_proba(new_data)).rename(columns = {0 : "[0:1107]",
                                                                                    1 : "[1108 : 1451]",
                                                                                    2 : "[1452 : 1922]",
                                                                                    3: "[1922:]"})
        st.table(predictions)
                
        


main()
