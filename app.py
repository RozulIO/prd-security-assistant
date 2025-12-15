# Author = Adrian Puente Z. <ch0ks>
# Date = Sunday, December 14, 2025
# Version = 0.9

import os
import logging
import json
import pandas as pd
import streamlit as st
import markdown
from xhtml2pdf import pisa
from io import BytesIO
from langchain_community.document_loaders import Docx2txtLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Logging Configuration ---
log_handlers = [logging.FileHandler("app.log")]

# Check for DEBUG environment variable
if os.getenv("DEBUG", "false").lower() == "true":
    log_handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def convert_to_pdf(source_html):
    """
    Converts HTML string to PDF bytes using xhtml2pdf.
    """
    result = BytesIO()
    pisa_status = pisa.CreatePDF(source_html, dest=result)
    if pisa_status.err:
        logger.error(f"PDF generation error: {pisa_status.err}")
        return None
    return result.getvalue()

# --- Core Logic ---

def load_docx(uploaded_file):
    """
    Saves the uploaded file to a temporary directory, loads it using Docx2txtLoader,
    and returns the content. Cleans up the temporary file afterwards.
    """
    # Ensure temp directory exists
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", uploaded_file.name)
    
    logger.info(f"Saving uploaded file to temporary path: {temp_path}")
    
    # Save to temp
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # Load
        logger.info("Loading document content...")
        loader = Docx2txtLoader(temp_path)
        data = loader.load()
        content = data[0].page_content # loader.load() returns a list of documents
        logger.info("Document content loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading document: {e}")
        raise e
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Cleaned up temporary file: {temp_path}")
            
    return content

def analyze_risk(text_content):
    """
    Uses Google Gemini to perform a STRIDE-based security risk assessment.
    Returns a list of dictionaries (JSON).
    """
    logger.info("Starting risk assessment analysis...")
    
    model_name = os.getenv("MODELAI", "gemini-flash-latest")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("GOOGLE_API_KEY not found.")
        st.error("Error: GOOGLE_API_KEY not found in environment variables.")
        return []

    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.3, google_api_key=api_key)
    
    # We ask for a strict JSON output
    template = """
    You are a Senior Security Engineer. You are analyzing a product requirement document.
    Apply the STRIDE threat modeling methodology to the following system description.
    
    Identify potential threats and return the output as a strictly formatted JSON array of objects. 
    Each object must have the following keys:
    - "Feature Name": The specific feature or component affected.
    - "Threat Type": The STRIDE category (Spoofing, Tampering, etc.).
    - "Description": A description of the threat.
    - "Risk": The potential impact or consequence.
    - "Recommendation": Mitigation steps.
    - "Risk Level": High, Medium, or Low.

    Do not include any markdown formatting (like ```json). Just the raw JSON array.
    
    System Description: {text}
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        response = chain.invoke({"text": text_content})
        logger.info("Risk assessment analysis completed successfully.")
        return response
    except Exception as e:
        logger.error(f"Error during risk assessment analysis: {e}")
        st.error(f"Error parsing AI response: {e}")
        return []
def generate_report_narrative(text_content, risks_data):
    """
    Generates the narrative sections of the report (Executive Summary, Intro, etc.).
    """
    logger.info("Generating report narrative...")
    
    model_name = os.getenv("MODELAI", "gemini-flash-latest")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.5, google_api_key=api_key)
    
    template = """
    You are a Senior Security Engineer writing a formal Security Assessment Report.
    
    Based on the System Description and the identified risks provided below, generate the following sections in Markdown format: 
    
    # Security Assessment Report
    
    ## Executive Summary
    (A high-level summary of the system and the critical findings)
    
    ## Introduction
    (Brief introduction to the document and the system under review)
    
    ## Scope
    (Define what was analyzed)
    
    ## Methodology
    (Briefly explain that STRIDE threat modeling was used)
    
    ## Conclusion
    (Final thoughts and next steps)
    
    Do NOT include the "Risk Assessment" table in this output; I will append it manually.
    
    System Description: {text}
    Identified Risks Summary: {risks}
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    try:
        response = chain.invoke({"text": text_content, "risks": str(risks_data)})
        cleaned_response = response.replace("```markdown", "").replace("```", "").strip()

        return cleaned_response
    except Exception as e:
        logger.error(f"Error generating report narrative: {e}")
        return "Error generating report narrative."

# --- UI Implementation ---

def main():
    logger.info("Application starting...")

    query_params = st.query_params
    if "healthz" in query_params:
        st.write("OK")
        return

    logger.info("Application starting...")
    
    # 1. Configuration
    st.set_page_config(
        page_title="AI Risk Assessment",
        page_icon="🛡️",
        layout="centered"
    )

    # 2. Custom CSS
    st.markdown("""
    <style>
        .stButton button.primary {
            background-color: #007bff;
            color: white;
            border-color: #007bff;
        }
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            color: #555;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            z-index: 1000;
        }
        .main-header {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #333;
            font-weight: 700;
            font-size: 2rem;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'risk_data' not in st.session_state:
        st.session_state.risk_data = None
    if 'original_text' not in st.session_state:
        st.session_state.original_text = None

    # --- Page Routing ---
    if st.session_state.page == 'home':
        render_home_page()
    elif st.session_state.page == 'report':
        render_report_page()

def render_home_page():
    # 3. Header
    st.markdown("""
        <div class="main-header">
            <span>🛡️</span> AI Security Risk Assessment
        </div>
    """, unsafe_allow_html=True)

    # 4. Main Container
    uploaded_file = st.file_uploader("Upload your PRD/Spec", type=['docx'])
    
    if st.button("Perform Security Assessment", type="primary"):
        if uploaded_file is not None:
            logger.info(f"User initiated assessment for file: {uploaded_file.name}")
            with st.spinner("Analyzing security risks..."):
                try:
                    # Load content
                    content = load_docx(uploaded_file)
                    st.session_state.original_text = content
                    
                    if not content:
                        logger.warning("No content extracted from document.")
                        st.error("Could not extract text from the document.")
                    else:
                        # Analyze and store in session state
                        risks = analyze_risk(content)
                        st.session_state.risk_data = risks
                        # Clear previous report if it exists
                        if 'full_report_md' in st.session_state:
                            del st.session_state.full_report_md
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            logger.warning("User attempted to perform assessment without uploading a file.")
            st.warning("Please upload a DOCX file first.")

    # Display Results if available
    if st.session_state.risk_data:
        st.success("Assessment Complete!")
        
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.risk_data)
        
        # Display Table
        st.subheader("Risk Assessment Table")
        st.dataframe(df)
        
        # Download CSV and Generate Report buttons
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Table as CSV",
                data=csv,
                file_name='risk_assessment.csv',
                mime='text/csv',
                type="primary"
            )
        with col2:
            if st.button("Generate Full Report", type="primary"):
                st.session_state.page = 'report'
                st.rerun()

    # 6. Footer
    st.markdown("""
        <div class="footer">
            ©2025 Rozul IO. All rights reserved
        </div>
    """, unsafe_allow_html=True)

def render_report_page():
    st.button("← Back to Assessment", on_click=lambda: st.session_state.update({'page': 'home'}), type="primary")
    
    if st.session_state.risk_data and st.session_state.original_text:
        # Check if report is already generated in session state
        if 'full_report_md' not in st.session_state or st.session_state.full_report_md is None:
            with st.spinner("Generating narrative report..."):
                # Generate narrative
                narrative = generate_report_narrative(st.session_state.original_text, st.session_state.risk_data)
                
                # Construct the table Markdown
                df = pd.DataFrame(st.session_state.risk_data)
                table_md = df.to_markdown(index=False)
                
                # Combine
                st.session_state.full_report_md = f"{narrative}\n\n## Risk Assessment\n\n{table_md}"
        
        # Display the report
        st.markdown(st.session_state.full_report_md)
        
        # Download Buttons
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Download Report (Markdown)",
                data=st.session_state.full_report_md,
                file_name='security_assessment_report.md',
                mime='text/markdown',
                type="primary"
            )
        
        with col2:
            # Convert MD to HTML for PDF
            html_text = markdown.markdown(st.session_state.full_report_md, extensions=['tables'])
            
            # Add basic CSS for PDF
            html_with_style = f"""
            <html>
            <head>
            <style>
                body {{ font-family: Helvetica, sans-serif; font-size: 12px; }}
                h1 {{ color: #333; font-size: 24px; }}
                h2 {{ color: #555; font-size: 18px; margin-top: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
            </head>
            <body>
            {html_text}
            </body>
            </html>
            """
            
            pdf_bytes = convert_to_pdf(html_with_style)
            
            if pdf_bytes:
                st.download_button(
                    label="Download Report (PDF)",
                    data=pdf_bytes,
                    file_name='security_assessment_report.pdf',
                    mime='application/pdf',
                    type="primary"
                )
            else:
                st.error("Failed to generate PDF.")
    else:
        st.error("No data available. Please perform an assessment first.")

if __name__ == "__main__":
    main()
