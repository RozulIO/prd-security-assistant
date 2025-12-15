# SECURITY.md - Security Policy & Implementation

**Project:** AI-Guided Risk Assessment Assistant
**Version:** 1.0.0
**Last Updated:** December 14, 2025

---

## 1. Security Overview ("Secure by Default")

This application is designed to process sensitive system design documentation. While this is a prototype/assignment submission, we adhere to the principle of "Secure by Default" to protect user data and maintain integrity.

## 2. Data Handling & Privacy

### 2.1 File Processing (Ephemeral Storage)
- **Zero-Persistence:** Uploaded DOCX files are saved to a temporary directory (`./temp/`) solely for parsing.
- **Immediate Cleanup:** The application explicitly deletes the file immediately after the text extraction is complete (`os.remove(temp_path)`).
- **No Database:** We do not store, log, or archive the contents of any uploaded documents or the AI-generated risk reports.

### 2.2 AI Interaction (Data Minimization)
- **Context Only:** Only the extracted text relevant to the system description is sent to the Gemini API. The AI-generated risk assessment now includes specific "Feature Name" and "Mitigation Recommendations" columns.
- **API Security:** All data in transit to Google's servers is encrypted via TLS 1.3 (handled by the LangChain/Google client).
- **Model Training:** By using the enterprise/paid tier of Gemini API (via our API Key), we operate under Google's data governance policy where API data is **not** used to train their public models (verify specific Google Cloud terms for your key type).

### 2.3 Report Generation
- **Multiple Formats:** Users can download the risk assessment table as a CSV, and the full narrative report as Markdown or PDF.
- **PDF Conversion:** Markdown reports are converted to PDF using `markdown` and `xhtml2pdf` libraries, with a basic CSS styling for professional presentation.

## 3. Infrastructure & Deployment

### 3.1 API Key Management
- **Environment Variables:** The `GOOGLE_API_KEY` is never hardcoded in the source code. It is injected via Environment Variables in the hosting provider (Render).
- **Code Repository:** `.env` files are strictly excluded from version control via `.gitignore`.

### 3.2 Network Security
- **HTTPS Enforcement:** When deployed on Render, all traffic is served over HTTPS automatically.
- **Public Exposure:** Currently, the application is public. For production use, it requires an authentication layer (e.g., Streamlit-Authenticator or OAuth) to prevent unauthorized access.

## 4. Vulnerability Reporting

### 4.1 Reporting a Bug
If you discover a security vulnerability in this project, please do **not** open a public GitHub issue.

- **Email:** security@rosul.io (or your university email)
- **Response Time:** We aim to acknowledge reports within 48 hours.

### 4.2 Known Limitations (Prototype Status)
- **No Auth:** The current version lacks user login/authentication.
- **DoS Risk:** There is no rate limiting implemented on the file uploader, making it theoretically susceptible to Denial of Service if spammed.

---

## 5. Developer Guidelines (For Contributors)

1. **Never commit secrets:** Always check `git status` to ensure `.env` is ignored.
2. **Review Dependencies:** Periodically run `pipenv check` or `pip audit` to scan `requirements.txt` for vulnerable packages. New dependencies (`tabulate`, `markdown`, `xhtml2pdf`) have been added for enhanced reporting capabilities.
3. **Input Validation:** Ensure the `load_docx` function maintains strict type checking (only `.docx` allowed) to prevent malicious file uploads.