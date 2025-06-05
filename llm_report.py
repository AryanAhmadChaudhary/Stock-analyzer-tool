import os
import requests
from groq import Groq
from dotenv import load_dotenv
from fpdf import FPDF
import unicodedata


load_dotenv()
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def clean_text_for_pdf(text):
    def replace_non_latin1(c):
        try:
            c.encode('latin-1')
            return c
        except UnicodeEncodeError:
            return '' 
    return ''.join(replace_non_latin1(c) for c in text)




def generate_swot_report(info, sentiment):
    prompt = f"""
    Create a SWOT analysis of the company with this context:
    🔸 Company: {info.get('shortName')}
    🔸 Sector: {info.get('sector')}
    🔸 Market Cap: {info.get('marketCap')}
    🔸 Summary: {info.get('longBusinessSummary')}
    🔸 Real-time Sentiment: {sentiment}

    Format it with clear headings:
    Strengths:
    Weaknesses:
    Opportunities:
    Threats:
    """

    # Call LLaMA 3.1 via Groq
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=700,
        top_p=1,
        stream=False
    )

    return completion.choices[0].message.content

# 🔹 Save SWOT to PDF safely (without encoding errors)
def save_swot_pdf(swot_text: str, filename="swot_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    clean_text = clean_text_for_pdf(swot_text)

    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf.output(filename)
    return filename
