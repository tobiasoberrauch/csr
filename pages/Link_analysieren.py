import streamlit as st

from functions import api_request

st.set_page_config(page_title="Link analysieren")

st.markdown(
    """
    ## CSRD-Datenpunkte Zuordnung
"""
)

link = st.text_input("Link:", value="https://www.audius.de/de/blog/sauberes-trinkwasser-fuer-uganda")

description = st.text_area(
    "Beschreibung",
    value="Der Blogbeitrag auf der Website von Audius beschreibt ein Projekt zur Bereitstellung von sauberem Trinkwasser in Uganda. ",
)

text = f"""
Bitte lese folgende Url ein: {link}
Dabei handelt es sich um folgendes: {description}
"""

if st.button("CSRD-Datenpunkte zuordnen"):
    response = api_request(text)
    st.write("Zuordnung der CSRD-Datenpunkte:")
    st.write(response.choices[0].message.content.strip())