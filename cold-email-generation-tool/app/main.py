import ssl
import certifi

# ✅ Fix SSL Certificate Error (Windows HTTPS fix)
ssl._create_default_https_context = ssl.create_default_context(
    cafile=certifi.where()
)

import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chain import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(chain, portfolio):
    st.title("Cold Mail Generator")

    url_input = st.text_input(
        "Enter a Job URL:",
        value="https://jobs.nike.com/job/R-33460"
    )

    submit_button = st.button("Generate Email")

    if submit_button and url_input:
        try:
            st.write("🔎 Fetching job page...")

            loader = WebBaseLoader([url_input])
            documents = loader.load()

            if not documents:
                st.error("No content loaded from URL.")
                return

            page_content = documents[0].page_content
            cleaned_data = clean_text(page_content)

            st.write("📄 Extracting job details...")

            portfolio.load_portfolio()

            jobs = chain.extract_jobs(cleaned_data)

            if not jobs:
                st.warning("No jobs found on this page.")
                return

            for job in jobs:

                if not isinstance(job, dict):
                    continue

                skills = job.get("skills", [])

                # ✅ Prevent Chroma crash if skills empty
                if skills:
                    links = portfolio.query_links(skills)
                else:
                    links = []

                email = chain.write_mail(job, links)

                st.subheader(job.get("role", "Job Position"))
                st.code(email, language="markdown")

        except Exception as e:
            st.error(f"An Error Occurred: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(
        layout="wide",
        page_title="Cold Email Generator",
        page_icon="📧"
    )

    chain = Chain()
    portfolio = Portfolio()

    create_streamlit_app(chain, portfolio)