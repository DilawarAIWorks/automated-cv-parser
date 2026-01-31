from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import PlainTextResponse
import os
import shutil
import fitz  # PyMuPDF
import cv2
import requests
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from docx2pdf import convert
import pythoncom

# ---------------- CONFIGURATION ----------------
app = FastAPI(title="Universal OCR API")
ocr_engine = RapidOCR()

# YOUR N8N WEBHOOK URL
N8N_WEBHOOK_URL = "https://hexametric-tegularly-lacresha.ngrok-free.dev/webhook-test/receive-ocr"

# Temp folders
TEMP_DIR = "temp_files"
IMG_DIR = os.path.join(TEMP_DIR, "images")
GRAY_DIR = os.path.join(TEMP_DIR, "gray")

def recreate_dirs():
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(GRAY_DIR, exist_ok=True)

recreate_dirs()

# ---------------- HELPERS ----------------

def clear_temp():
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    recreate_dirs()

def convert_word_to_pdf(docx_path, output_pdf_path):
    try:
        pythoncom.CoInitialize()
        convert(docx_path, output_pdf_path)
        return True, None
    except Exception as e:
        return False, str(e)

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    image_paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_path = os.path.join(IMG_DIR, f"page_{i+1}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    doc.close()
    return image_paths

def to_grayscale(image_paths):
    gray_paths = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is None: continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_path = os.path.join(GRAY_DIR, os.path.basename(path).replace(".png", "_gray.png"))
        cv2.imwrite(gray_path, gray)
        gray_paths.append(gray_path)
    return gray_paths

def run_ocr(image_path):
    img_np = cv2.imread(image_path, 0)
    if img_np is None: return ""
    result, _ = ocr_engine(img_np)
    if result:
        return "\n".join([line[1] for line in result])
    return ""

def send_to_n8n(text_content):
    """Sends the COMBINED text to your n8n webhook."""
    try:
        payload = {"extracted_text": text_content}
        print(f"DEBUG: Attempting to send to: {N8N_WEBHOOK_URL}")
        requests.post(N8N_WEBHOOK_URL, json=payload)
    except Exception as e:
        print(f"DEBUG: Failed to send to n8n: {e}")

# ---------------- API ENDPOINT ----------------

@app.post("/extract-text/", response_class=PlainTextResponse)
async def extract_text_api(
    role: str = Form(...),
    email: str = Form(...),
    user_message: str = Form(...),
    file: UploadFile = File(...)
):
    # 1. Validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    clear_temp()
    filename = file.filename.lower()
    input_path = os.path.join(TEMP_DIR, file.filename)
    pdf_path = os.path.join(TEMP_DIR, "converted.pdf")

    # 2. Save File
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # 3. Conversion Logic
    if filename.endswith(".docx"):
        success, error = convert_word_to_pdf(input_path, pdf_path)
        if not success: raise HTTPException(status_code=500, detail=error)
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(input_path)
        img.save(pdf_path, "PDF")
    elif filename.endswith(".pdf"):
        pdf_path = input_path
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 4. OCR Pipeline
    try:
        raw_images = pdf_to_images(pdf_path)
        gray_images = to_grayscale(raw_images)
        
        cv_text = ""
        for i, img_path in enumerate(gray_images):
            page_text = run_ocr(img_path)
            cv_text += f"\n--- Page {i+1} ---\n{page_text}\n"
        
        # 5. COMBINE EVERYTHING (The Format You Requested)
        final_combined_text = (
            f"Role: {role}\n"
            f"User message: {email} {user_message}\n\n"
            f"Extracted CV text:\n{cv_text}"
        )
        
        # 6. Send Combined Text to n8n
        send_to_n8n(final_combined_text)
        
        # 7. Return Combined Text to Streamlit
        return PlainTextResponse(final_combined_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "OCR API is running."}