import logging
import shutil

import pytesseract
import streamlit as st
import streamlit.components.v1 as components

# Include Google Analytics tracking code
with open("index.html", "r") as f:
    html_code = f.read()
    components.html(html_code, height=0)

logging.basicConfig(level=logging.INFO)

# search for tesseract binary in path
@st.cache_resource
def find_tesseract_binary() -> str:
    return shutil.which("tesseract")


# set tesseract binary path
pytesseract.pytesseract.tesseract_cmd = find_tesseract_binary()
if not pytesseract.pytesseract.tesseract_cmd:
    st.error("Tesseract binary not found in PATH. Please install Tesseract.")
