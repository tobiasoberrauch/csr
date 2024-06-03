import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import docx2txt
import PyPDF2
import tempfile
import os

load_dotenv()

client = OpenAI()

# OpenAI API-Key eingeben

st.title("CSRD-Datenpunkte Zuordnung")

system_prompt = """
    Zu welchen CSRD-Datenpunkten passt dieser Artikel am besten?
    Bitte immer deutsch antworten.
    Bitte als Tabelle ausgeben:

    | Datenpunkt | Passage direkt aus dem Artikel oder dem Link | Warum passt der Datenpunkt zur Passage? | 
    |------------------|---------------------------------------------|---------------------------------------------|
    | ESRS 2 MDR-x nnx | ... | ... |
    | ESRS 2 MDR-x nnx | ... | ... |

    **Datenpunkte:**

    | ESRS | DR | Paragraph | Related AR | Name | Data Type |
    |------|----|-----------|------------|------|-----------|
    | ESRS 2 | MDR-P | 65 a | | Description of key contents of policy | narrative |
    | ESRS 2 | MDR-P | 65 b | | Description of scope of policy or of its exclusions | narrative |
    | ESRS 2 | MDR-P | 65 c | | Description of most senior level in organisation that is accountable for implementation of policy | narrative |
    | ESRS 2 | MDR-P | 65 d | | Disclosure of third-party standards or initiatives that are respected through implementation of policy | narrative |
    | ESRS 2 | MDR-P | 65 e | | Description of consideration given to interests of key stakeholders in setting policy | narrative |
    | ESRS 2 | MDR-P | 65 f | | Explanation of how policy is made available to potentially affected stakeholders and stakeholders who need to help implement it | narrative |
    | ESRS 2 | MDR-A | 68 a | AR 22 | Disclosure of key action | narrative |
    | ESRS 2 | MDR-A | 68 b | | Description of scope of key action | narrative |
    | ESRS 2 | MDR-A | 68 c | | Time horizon under which key action is to be completed | semi-narrative |
    | ESRS 2 | MDR-A | 68 d | | Description of key action taken, and its results, to provide for and cooperate in or support provision of remedy for those harmed by actual material impacts | narrative |
    | ESRS 2 | MDR-A | 68 e | | Disclosure of quantitative and qualitative information regarding progress of actions or action plans disclosed in prior periods | narrative |
    | ESRS 2 | MDR-A | 69 a | AR 23 | Disclosure of the type of current and future financial and other resources allocated to the action plan | narrative |
    | ESRS 2 | MDR-A | 69 b | | Current financial resources allocated to action plan (Capex) | Monetary |
    | ESRS 2 | MDR-A | 69 b | | Current financial resources allocated to action plan (Opex) | Monetary |
    | ESRS 2 | MDR-A | 69 c | | Future financial resources allocated to action plan (Capex) | Monetary |
    | ESRS 2 | MDR-A | 69 c | | Future financial resources allocated to action plan (Opex) | Monetary |
    | ESRS 2 | MDR-M | 75 | | Description of metric used to evaluate performance and effectiveness, in relation to material impact, risk or opportunity | narrative |
    | ESRS 2 | MDR-M | 77 a | | Disclosure of methodologies and significant assumptions behind metric | narrative |
    | ESRS 2 | MDR-M | 77 b | | Type of external body other than assurance provider that provides validation | narrative |
    | ESRS 2 | MDR-T | 80 a | "AR 24 - AR 26" | Relationship with policy objectives | Decimal |
    | ESRS 2 | MDR-T | 80 b | "AR 24 - AR 26" | Measurable target | Decimal/Percent/narrative |
    | ESRS 2 | MDR-T | 80 b | "AR 24 - AR 26" | Nature of target | semi-narrative |
    | ESRS 2 | MDR-T | 80 c | "AR 24 - AR 26" | Description of scope of target | narrative |
    | ESRS 2 | MDR-T | 80 d | "AR 24 - AR 26" | Baseline value | Integer |
    | ESRS 2 | MDR-T | 80 d | "AR 24 - AR 26" | Baseline year | Integer |
    | ESRS 2 | MDR-T | 80 e | "AR 24 - AR 26" | Period to which target applies | semi-narrative |
    | ESRS 2 | MDR-T | 80 e | "AR 24 - AR 26" | Indication of milestones or interim targets | narrative |
    | ESRS 2 | MDR-T | 80 f | "AR 24 - AR 26" | Description of methodologies and significant assumptions used to define target | narrative |
    | ESRS 2 | MDR-T | 80 g | "AR 24 - AR 26" | Target related to environmental matters is based on conclusive scientific evidence | semi-narrative |
    | ESRS 2 | MDR-T | 80 h | "AR 24 - AR 26" | Disclosure of how stakeholders have been involved in target setting | narrative |
    | ESRS 2 | MDR-T | 80 i | "AR 24 - AR 26" | Description of any changes in target and corresponding metrics or underlying measurement methodologies, significant assumptions, limitations, sources and adopted processes to collect data | narrative |
    | ESRS 2 | MDR-T | 80 j | "AR 24 - AR 26" | Description of performance against disclosed target | narrative |
    | ESRS 2 | MDR-P | 62 | | Disclosure of reasons for not having adopted policies | narrative |
    | ESRS 2 | MDR-P | 62 | | Disclosure of timeframe in which the undertakings aims to adopt policies | narrative |
    | ESRS 2 | MDR-A | 62 | | Disclosure of reasons for not having adopted actions | narrative |
    | ESRS 2 | MDR-A | 62 | | Disclosure of timeframe in which the undertakings aims to adopt actions | narrative |
    | ESRS 2 | MDR-T | 81 a | | Disclosure of timeframe for setting of measurable outcome-oriented targets | narrative |
    | ESRS 2 | MDR-T | 81 a | | Description of reasons why there are no plans to set measurable outcome-oriented targets | narrative |
    | ESRS 2 | MDR-T | 81 b | | Effectiveness of policies and actions is tracked in relation to material sustainability-related impact, risk and opportunity | semi-narrative |
    | ESRS 2 | MDR-T | 81 b i | | Description of processes through which effectiveness of policies and actions is tracked in relation to material sustainability-related impact, risk and opportunity | narrative |
    | ESRS 2 | MDR-T | 81 b ii | | Description of defined level of ambition to be achieved and of any qualitative or quantitative indicators used to evaluate progress | narrative |
    | ESRS 2 | MDR-T | 81 b ii 80 d | | Base year from which progress is measured | GYear |

"""

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        text += page.extract_text()
    return text

def read_docx(file):
    return docx2txt.process(file)

uploaded_file = st.file_uploader("Laden Sie eine PDF-, DOC- oder DOCX-Datei hoch", type=["pdf", "doc", "docx"])

text_input = st.text_area("Oder geben Sie den Artikeltext oder die URL ein", height=200)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
    if uploaded_file.name.endswith(".pdf"):
        text_input = read_pdf(temp_file_path)
    elif uploaded_file.name.endswith(".doc") or uploaded_file.name.endswith(".docx"):
        text_input = read_docx(temp_file_path)
    os.remove(temp_file_path)

if st.button("CSRD-Datenpunkte zuordnen"):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"{text_input} Bitte immer deutsch antworten"
            },
        ],
        temperature=0.0,
    )
    st.write("Zuordnung der CSRD-Datenpunkte:")
    st.write(response.choices[0].message.content.strip())
