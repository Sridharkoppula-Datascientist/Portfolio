import streamlit as st
import os
import zipfile
import PyPDF2
import docx
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# ---------------- ENV ----------------
load_dotenv()
# os.environ["GOOGLE_API_KEY"] = os.getenv("gemini")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Portfolio Generator", layout="wide")

# ---------------- FUNCTIONS ----------------
def extract_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# ---------------- UI ----------------
uploaded_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])
resume_text = ""

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        resume_text = extract_pdf(uploaded_file)
    else:
        resume_text = extract_docx(uploaded_file)
    st.subheader("Extracted Resume Text")
    st.text_area("Resume Content", resume_text, height=250)

# ---------------- GENERATE WEBSITE ----------------
if st.button("Generate Portfolio Website") and resume_text.strip():

    system_prompt = """
You are a Senior Frontend Developer and UI/UX Expert. 
Your task is to analyze the content of the provided text (extracted from a PDF or text file) and generate a modern, responsive, and visually appealing website that effectively presents this information.

CONTENT STRATEGY:
1. Analyze the Context: inferred the type of document (e.g., Resume, Business Proposal, Menu, Documentation) to determine the appropriate website layout (e.g., Portfolio, Landing Page, Restaurant Theme, Wiki).
2. Structure the Data: Organize the raw text into logical HTML sections (Header, Hero, Features/Experience, Gallery, Contact).
3. Adapt for Web: You may lightly edit the text for web readability (e.g., converting long lists into bullet points or cards) while preserving the original meaning.

TECHNICAL GUIDELINES:
1. HTML: Use semantic HTML5. You MUST link the CSS file using <link rel="stylesheet" href="style.css"> and the JS file using <script src="script.js"></script>.
2. CSS: Use modern CSS (Flexbox, Grid) for layout. Ensure the design is fully responsive for mobile and desktop. Use nice fonts (e.g., import Google Fonts).
3. JS: Write clean, efficient ES6+ JavaScript. Handle DOM content loading properly.
4. IMAGES: If images are needed, use placeholder images from valid sources (like https://placehold.co/600x400) or assume a generic placeholder.

IMPORTANT: You must strictly follow the output format below. Do not add any markdown formatting (like ```html) around the tags. Just use the tags provided.

The output should be in the below format:
--html--
[html code]
--html--

--css--
[css code]
--css--

--js--
[java script code]
--js--
"""
    messages = [
        ("system", system_prompt),
        ("user", resume_text)
    ]

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    response = model.invoke(messages)
    content = response.content

    # ---------------- SAVE FILES ----------------
    html_code = content.split("--html--")[1].split("--html--")[0]
    css_code = content.split("--css--")[1].split("--css--")[0]
    js_code = content.split("--js--")[1].split("--js--")[0]

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    with open("style.css", "w", encoding="utf-8") as f:
        f.write(css_code)
    with open("script.js", "w", encoding="utf-8") as f:
        f.write(js_code)

    # ---------------- ZIP ----------------
    with zipfile.ZipFile("portfolio_website.zip", "w") as zipf:
        zipf.write("index.html")
        zipf.write("style.css")
        zipf.write("script.js")

    # ---------------- DOWNLOAD ----------------
    st.success("Portfolio Website Generated Successfully!")
    with open("portfolio_website.zip", "rb") as f:
        st.download_button(
            "⬇ Download Portfolio Website",
            data=f,
            file_name="portfolio_website.zip"
        )

