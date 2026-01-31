# 📄 Job Application & CV Parser with OCR Automation

This project is a full-stack automated application tracking system (ATS) starter. It features a user-friendly frontend for submitting job applications and a robust backend that performs Optical Character Recognition (OCR) on resumes (PDF, Word, or Images) before sending the data to an n8n workflow for further processing.

## 🚀 Features

* **Universal File Support:** Accepts PDF, DOCX, PNG, JPG, and JPEG formats.
* **Intelligent Pre-processing:** automatically converts all uploads to high-contrast grayscale images for optimal OCR accuracy.
* **Rapid OCR:** Uses `RapidOCR` (ONNX Runtime) to extract text from resumes quickly and accurately.
* **Clean Frontend:** Built with **Streamlit** for an easy-to-use candidate submission interface.
* **Fast Backend:** Powered by **FastAPI** to handle file conversion, image processing, and API requests.
* **Automation Ready:** Automatically pushes extracted data (Candidate details + CV text) to an **n8n Webhook** for downstream tasks (Google Sheets logging, AI analysis, Email drafting).

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** FastAPI, Uvicorn
* **OCR Engine:** RapidOCR (ONNX Runtime)
* **Image Processing:** OpenCV, Pillow (PIL)
* **PDF/Word Tools:** PyMuPDF (Fitz), Docx2pdf

---

## ⚙️ Installation & Setup

### 1. Prerequisites
* Python 3.10 or 3.11
* [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (Recommended for environment management)

### 2. Create a Virtual Environment
It is highly recommended to use a clean environment to avoid dependency conflicts.

```bash
conda create --name ocr-env python=3.11 -y
conda activate ocr-env