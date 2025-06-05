import streamlit as st
from analysis import analyze_stock
from llm_report import generate_swot_report, save_swot_pdf
from voiceover import generate_voice_report
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Analyzer & Reporter", layout="wide")

# -------------------------------
# UI Header
# -------------------------------
st.markdown("""
<style>
.title {
    font-size: 36px;
    font-weight: bold;
    color: #f8a900;
}
.subtitle {
    font-size: 20px;
    color: #999;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>📈 Stock Market Analyzer & Reporter</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Analyze Indian stocks with technical indicators, LLM-based SWOT, and voice reports</div>", unsafe_allow_html=True)
st.markdown("---")

# -------------------------------
# Initialize Session State
# -------------------------------
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# -------------------------------
# Stock Selector and Time Period
# -------------------------------
stock_options = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Wipro": "WIPRO.NS",
    "Hindustan Unilever": "HINDUNILVR.NS"
}

selected_company = st.selectbox("📌 Select a Company", options=list(stock_options.keys()))
ticker = stock_options[selected_company]
period = st.radio("📅 Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], horizontal=True)

# -------------------------------
# Run Analysis Button
# -------------------------------
if st.button("🚀 Run Full Analysis"):
    with st.spinner("⏳ Fetching data and running analysis..."):
        hist, info, sentiment = analyze_stock(ticker, period)
        swot = generate_swot_report(info, sentiment)
        pdf_file = save_swot_pdf(swot)
        audio_file = generate_voice_report(swot)

        # Store in session state
        st.session_state.analysis_done = True
        st.session_state.hist = hist
        st.session_state.info = info
        st.session_state.sentiment = sentiment
        st.session_state.swot = swot
        st.session_state.pdf_file = pdf_file
        st.session_state.audio_file = audio_file

# -------------------------------
# Show Tabs After Analysis
# -------------------------------
if st.session_state.analysis_done:
    hist = st.session_state.hist
    sentiment = st.session_state.sentiment
    swot = st.session_state.swot
    pdf_file = st.session_state.pdf_file
    audio_file = st.session_state.audio_file

    tab1, tab2, tab3, tab4 = st.tabs(["Price & Indicators", "Sentiment", "SWOT + PDF", "Voice Report"])

    with tab1:
        st.subheader("📈 Stock Price + Indicators")
        fig, ax = plt.subplots(3, figsize=(12, 9))
        ax[0].plot(hist['Close'], label="Close", color='blue')
        ax[0].plot(hist['MA20'], label="MA20", color='orange')
        ax[0].plot(hist['MA50'], label="MA50", color='green')
        ax[0].legend()
        ax[0].set_title("Price + Moving Averages")

        ax[1].bar(hist.index, hist['Volume'], label="Volume", color='purple')
        ax[1].legend()
        ax[1].set_title("Volume")

        ax[2].plot(hist['RSI'], label="RSI", color='red')
        ax[2].axhline(70, color='black', linestyle='--')
        ax[2].axhline(30, color='black', linestyle='--')
        ax[2].legend()
        ax[2].set_title("RSI Indicator")
        st.pyplot(fig)

    with tab2:
        st.subheader("Real-Time News Sentiment")
        st.markdown(f"**{selected_company}** sentiment analysis based on live news:")
        st.markdown(sentiment)

    with tab3:
        st.subheader("AI SWOT Analysis")
        st.code(swot, language='markdown')
        with open(pdf_file, "rb") as f:
            st.download_button("Download SWOT PDF", data=f, file_name=pdf_file)

    with tab4:
        st.subheader("🔊 Voice Report (Text-to-Speech)")
        st.audio(audio_file)

else:
    st.markdown("Choose a stock and run the analysis to see results.")
