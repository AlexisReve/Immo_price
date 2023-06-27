import pandas as pd 
import streamlit as st
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import folium
import streamlit.components.v1 as components
import plotly.express as px

st.set_page_config(layout = 'wide')

@st.cache_data
def load_data():
    data = pd.read_csv("TGV.csv", sep=";")
    return data


def map_call():
    ''' Création d'une carte interactive territorialisée à l'échelle de la commune '''
    df = data[data["Annee"] == 2021]
    df = df[["Code INSEE" ,"Commune", "Prixm2Moyen", "SurfaceMoy", "Nb_mutations", "TGV"]].dropna(subset=["SurfaceMoy", "Nb_mutations"])
    df.drop_duplicates(subset=["Code INSEE"], inplace=True)

    paris = folium.Map(location = [46.8534, 2.3488], zoom_start=6, min_zoom=4, tiles = "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
            attr = '&copy; OpenStreetMap France | &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors')

    choropleth = folium.Choropleth(
    geo_data= "modified_communes.geojson",
    name="choropleth",
    data= df,
    columns=["Code INSEE", "Prixm2Moyen"],
    key_on="feature.properties.code",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.5,
    highlight = True,
    legend_name="Engagement par département",
    )
    choropleth.geojson.add_to(paris)

    result_indexed = df.set_index('Code INSEE')

    for feature in choropleth.geojson.data['features']:
        Communes = feature['properties']['code']
        feature['properties']['Prixm2Moyen'] = '{:,.0f} €'.format(result_indexed.loc[Communes, 'Prixm2Moyen']).replace(',', ' ') if Communes in list(result_indexed.index) else 'Aucune données disponibles'
        feature['properties']['Nb_mutations'] = format(result_indexed.loc[Communes, 'Nb_mutations']) if Communes in list(result_indexed.index) else 'Aucune données disponibles'
        feature['properties']['SurfaceMoy'] = '{:,.0f} m2'.format(result_indexed.loc[Communes, 'SurfaceMoy']) if Communes in list(result_indexed.index) else 'Aucune données disponibles'
        

    folium.GeoJsonTooltip(['nom', "Prixm2Moyen", 'SurfaceMoy', 'Nb_mutations', "TGV"]).add_to(choropleth.geojson)  
    folium_static(paris,width=1000, height= 500)


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
        st.subheader("Prix Immobiliers par Commune en 2022")
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

    with st.form(key = 'my_form'):
        with st.container():
            col3, col4, col5, col6 = st.columns(4)

            with col3:
                Input_Maisons = st.text_input("Nombre de maisons vendues")

            with col4:
                Input_appart = st.text_input("Nombre d'appartements vendues")
            
            with col5:
                Input_surface = st.text_input("Surface Moyenne")

            with col6:
                Input_gare = st.selectbox("Gare", data["TGV"].unique().tolist())
            
            col7, col8, col9 = st.columns(3)

            with col8:
                submitted = st.form_submit_button("Appliquer les filtres")

        

main()
