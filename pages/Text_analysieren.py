import streamlit as st

from functions import api_request

st.set_page_config(page_title="Text analysieren")

st.markdown(
    """
    ## CSRD-Datenpunkte Zuordnung
"""
)

text = st.text_area("Text:", value="", height=500)

if st.button("CSRD-Datenpunkte zuordnen"):
    response = api_request(text)
    st.write("Zuordnung der CSRD-Datenpunkte:")
    st.write(response.choices[0].message.content.strip())