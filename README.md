# AI-Guided Risk Assessment Assistant

**Author:** Adrián Puente Z. (ch0ks)  
**Organization:** Rosul IO  
**Version:** 0.9  
**Date:** December 14, 2025

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![LangChain](https://img.shields.io/badge/LangChain-0.1-green)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange)

## Project Overview

The **AI-Guided Risk Assessment Assistant** is a Streamlit-based web application designed to help security engineers and system architects quickly perform STRIDE threat modeling on their Product Requirement Documents (PRDs) or System Design Specifications.

By uploading a `.docx` file containing the system description, the application leverages Google's **Gemini Pro/Flash** models (via LangChain) to analyze the text and generate a structured risk assessment report, identifying potential threats, their descriptions, and risk levels.

## Features

- **Automated Threat Modeling:** Applies the STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) to your documents.
- **AI-Powered Analysis:** Uses Google's advanced Gemini Large Language Models for deep context understanding.
- **Secure Processing:** Features ephemeral file handling with immediate cleanup to ensure document privacy.
- **Interactive UI:** Clean, professional interface built with Streamlit.
- **Observability:** Robust logging for monitoring application health and user interactions.

## Prerequisites

- **Python 3.9+**
- **Google AI Studio API Key** (Get one [here](https://aistudio.google.com/))

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rozulio/prd-security-assistant.git
    cd prd-security-assistant
    ```

2.  **Environment Setup:**
    Create a `.env` file in the root directory:
    ```bash
    GOOGLE_API_KEY=your_actual_api_key_here
    MODELAI=gemini-flash-latest
    DEBUG=true  # Optional: Enable console logging
    ```

3.  **Install Dependencies:**
    You can use the provided Makefile for convenience:
    ```bash
    make install
    ```
    Or manually:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Application:**
    ```bash
    make run
    ```
    Or manually:
    ```bash
    streamlit run app.py --server.port 8080
    ```

2.  **Access the App:** Open your browser and navigate to `http://localhost:8080`.

3.  **Perform Assessment:**
    - Upload your System Design Document (`.docx`).
    - Click **"Perform Security Assessment"**.
    - Review the generated STRIDE analysis table.

## Security & Privacy

This project adheres to a "Secure by Default" philosophy.

-   **Data Handling:** Uploaded files are processed in a temporary directory and **permanently deleted** immediately after text extraction. No documents are stored or archived.
-   **Data Privacy:** Only extracted text is sent to the Google Gemini API over encrypted channels (TLS 1.3).
-   **Secrets Management:** API keys are managed strictly via environment variables and are never committed to version control.

For more details, please refer to [SECURITY.md](SECURITY.md).

## Project Structure

```
├── app.py                # Main Streamlit application logic
├── Makefile              # Automation for install, run, and clean tasks
├── requirements.txt      # Python dependencies
├── GEMINI.md             # Development plan and architecture docs
├── SECURITY.md           # Security policy and implementation details
├── .gitignore            # Git exclusion rules
├── .env                  # Environment variables (not committed)
└── temp/                 # Temporary directory for file processing (auto-cleaned)
```

## Contributing

Contributions are welcome! Please follow these guidelines:
1.  Fork the repository.
2.  Create a feature branch.
3.  Ensure code adheres to the existing style and conventions.
4.  Submit a Pull Request.

**Developer Note:** Please review the `Developer Guidelines` in [SECURITY.md](SECURITY.md) before contributing.

## License

Rosul IO - All Rights Reserved.