import base64
import logging
from io import StringIO
from zipfile import ZipFile

# ------- OCR ------------
import pdf2image
import pytesseract
import streamlit as st
from openai import OpenAI
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pytesseract import Output, TesseractError

client = OpenAI(api_key=st.secrets.get("openai_api_key"))


@st.cache_data
def images_to_txt(path, language):
    images = pdf2image.convert_from_bytes(path)
    all_text = []
    for i in images:
        pil_im = i
        text = pytesseract.image_to_string(pil_im, lang=language)
        # ocr_dict = pytesseract.image_to_data(pil_im, lang='eng', output_type=Output.DICT)
        # ocr_dict now holds all the OCR info including text and location on the image
        # text = " ".join(ocr_dict['text'])
        # text = re.sub('[ ]{2,}', '\n', text)
        all_text.append(text)
    return all_text, len(all_text)


@st.cache_data
def convert_pdf_to_txt_pages(path):
    texts = []
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    size = 0
    c = 0
    file_pages = PDFPage.get_pages(path)
    nbPages = len(list(file_pages))
    for page in PDFPage.get_pages(path):
        interpreter.process_page(page)
        t = retstr.getvalue()
        if c == 0:
            texts.append(t)
        else:
            texts.append(t[size:])
        c = c + 1
        size = len(t)
    # text = retstr.getvalue()

    # fp.close()
    device.close()
    retstr.close()
    return texts, nbPages


@st.cache_data
def convert_pdf_to_txt_file(path):
    texts = []
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    # fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    file_pages = PDFPage.get_pages(path)
    nbPages = len(list(file_pages))
    for page in PDFPage.get_pages(path):
        interpreter.process_page(page)
        t = retstr.getvalue()
    # text = retstr.getvalue()

    # fp.close()
    device.close()
    retstr.close()
    return t, nbPages


@st.cache_data
def save_pages(pages):

    files = []
    for page in range(len(pages)):
        filename = "page_" + str(page) + ".txt"
        with open("./file_pages/" + filename, "w", encoding="utf-8") as file:
            file.write(pages[page])
            files.append(file.name)

    # create zipfile object
    zipPath = "./file_pages/pdf_to_txt.zip"
    zipObj = ZipFile(zipPath, "w")
    for f in files:
        zipObj.write(f)
    zipObj.close()

    return zipPath


def displayPDF(file):
    # Opening file from file path
    # with open(file, "rb") as f:
    base64_pdf = base64.b64encode(file).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def load_datapoints(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


datapoints_file = "datapoints.md"  # Path to your markdown file
datapoints_content = load_datapoints(datapoints_file)
system_prompt = f"""
    Zu welchen CSRD-Datenpunkten passt dieser Artikel am besten?
    Bitte immer deutsch antworten.
    Bitte als Tabelle ausgeben:

    | Datenpunkt | Zitat aus dem Text oder dem Link | Warum passt der Datenpunkt zur Passage? | 
    |------------------|---------------------------------------------|---------------------------------------------|
    | ESRS 2 MDR-x nnx | ... | ... |
    | ESRS 2 MDR-x nnx | ... | ... |

    {datapoints_content}
"""


def api_request(text):
    logging.info('Request', text)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{text} Bitte immer deutsch antworten"},
        ],
        temperature=0.0,
    )
    logging.info('Response', response)
    return response
