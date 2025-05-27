import streamlit as st
import asyncio # Import asyncio to run async functions
from crawler import get_all_external_links_with_playwright as crawl # Use the actual function name
from adlm import malverts
import json

st.set_page_config(layout="wide",page_title="AdLM - Ad Link Analyser Powered by Gemini")

# Initialize session state for storing results and messages
if 'links' not in st.session_state:
    st.session_state.links = []
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = ""

def run_crawl_sync(input_url):
    """
    A synchronous wrapper to run the asynchronous crawl function.
    """
    if not input_url:
        st.session_state.message = "Please enter a URL to scan."
        st.session_state.links = []
        return

    st.session_state.message = "Scanning in progress... This may take a moment."
    st.session_state.links = [] # Clear previous results


    with st.spinner('Scanning for external links...'):
        try:
            # Run the async crawl function synchronously
            captured_links = asyncio.run(crawl(input_url))
            if captured_links:
                st.session_state.links = sorted(list(captured_links))
                st.session_state.message = f"Found {len(captured_links)} unique external links."
                with st.spinner('Performing ad analysis:'):
                    st.session_state.analysis = malverts(captured_links)
            else:
                st.session_state.links = []
                st.session_state.message = "No external links found or an issue occurred during crawling."
        except Exception as e:
            st.session_state.links = []
            st.session_state.message = f"An error occurred during scanning: {e}"
            st.error(f"Error: {e}")


st.title('AdLM - Ad Link Analyser Powered by Gemini')

url = st.text_input("Enter a URL", key="url_input")

st.button("Scan for malicious ads", key="scan_button", on_click=run_crawl_sync, args=(url,))

# Display messages and results based on session state
if st.session_state.message:
    st.info(st.session_state.message)

if st.session_state.links:
    st.subheader("External Links:")
    st.text_area("Links", "\n".join(st.session_state.links), height=300)

if st.session_state.analysis:
    st.subheader("Ad Analysis:")
    analysis = json.loads(st.session_state.analysis)
    st.dataframe(analysis,hide_index=True)
    