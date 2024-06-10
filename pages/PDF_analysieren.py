import pytesseract
import streamlit as st
from PIL import Image

from functions import api_request, displayPDF, images_to_txt

st.set_page_config(page_title="PDF analysieren")

st.markdown(
    """
    ## CSRD-Datenpunkte Zuordnung
"""
)

LANGUAGE = "deu"


file = st.file_uploader("Datei laden", type=["pdf", "png", "jpg"])
if file:
    path = file.read()
    file_extension = file.name.split(".")[-1]

    if file_extension == "pdf":
        with st.expander("PDF Vorschau"):
            displayPDF(path)

        texts, nbPages = images_to_txt(path, LANGUAGE)
        totalPages = "Pages: " + str(nbPages) + " in total"
        text = "\n\n".join(texts)

        with st.expander("Text-Vorschau"):
            st.write(text)

        # add field to enter a description about the document
        description = st.text_area(
            "Beschreibung",
            value="Ein Entgelttransparenzbericht ist ein Bericht, der im Rahmen des Entgelttransparenzgesetzes (EntgTranspG) in Deutschland erstellt wird. Das Entgelttransparenzgesetz zielt darauf ab, die Transparenz über die Entgeltstrukturen in Unternehmen zu erhöhen und geschlechtsbedingte Ungleichheiten bei der Bezahlung zu beseitigen",
        )

        if st.button("CSRD-Datenpunkte zuordnen"):
            response = api_request(text)
            st.write("Zuordnung der CSRD-Datenpunkte:")
            st.write(response.choices[0].message.content.strip())
    else:
        pil_image = Image.open(file)
        text = pytesseract.image_to_string(pil_image, lang=LANGUAGE)
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Display Image"):
                st.image(file)
        with col2:
            with st.expander("Display Text"):
                st.info(text)
        st.download_button("Download txt file", text)
