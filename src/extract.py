# src/extract.py
import os
import io
import sys
from typing import List, Dict, Any
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import pandas as pd
import re
import cv2
import numpy as np
from mutate import normalize_report_a
from generate_pdf import create_pdf_from_text
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

#הוא טקסטואלי (שכבת טקסט) PDF בדיקה אם ה 
def is_textual_pdf(path: str, min_text_len: int = 20) -> bool:
    """
    פותח את ה-PDF עם pdfplumber ומחפש האם קיימת כמות משמעותית של טקסט בעמודים.
    מחזיר True אם יש טקסט מובנה; False אם נראה סרוק.
    """
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text and len(text.strip()) >= min_text_len:
                    return True
    except Exception as e:
        # במצבים מסוימים pdfplumber לא מצליח לפתוח (corrupt) - נחזור False
        print(f"[is_textual_pdf] warning: {e}", file=sys.stderr)
    return False

# --- חילוץ טקסט מדף טקסטואלי ---
def extract_text_from_textual_pdf(path: str) -> str:
    """
    מחלץ טקסט מקובץ PDF טקסטואלי.
    מחזיר מחרוזת אחת עם כל התוכן.
    """
    all_text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_text += text + "\n"
    except Exception as e:
        print(f"[extract_text_from_textual_pdf] error: {e}", file=sys.stderr)
    return all_text.strip()

# --- חילוץ טקסט מדף סרוק (OCR) ---
def extract_text_from_scanned_pdf(path: str, dpi: int = 300, lang: str = "heb+eng") -> str:
    """
    ממיר כל עמוד לתמונה ומריץ עליו OCR.
    מחזיר טקסט מלא של המסמך.
    """
    all_text = ""
    try:
        images = convert_from_path(
            path,
            dpi=dpi,
            poppler_path=r"C:\poppler\poppler-25.07.0\Library\bin"
        )

        for i, img in enumerate(images):
            # המרה ל-numpy array
            img_cv = np.array(img)
            # המרה לגווני אפור
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            # סינון רעש וחידוד קונטרסט
            gray = cv2.medianBlur(gray, 3)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            text = pytesseract.image_to_string(thresh, lang=lang)
            all_text += text + "\n"
    except Exception as e:
        print(f"[extract_text_from_scanned_pdf] error: {e}", file=sys.stderr)
    return all_text.strip()

#מזהה האם הדף מסוג A או B
def detect_report_type(text: str) -> str:
  
    text_lower = text.lower()

    company_keywords = ["חברה", "בעמ", "בע\"מ", "company", "limited", "ltd"]

    employee_table_keywords = [
        "כרטיס עובד",
        "שם העובד",
        "ימי עבודה",
        "סהכ שעות",
        "סהכ לתשלום",
        "סיכום שעות",
        "תשלום",
        "חודש",
        "שעת כניסה",
        "שעת יציאה"
        
    ]

    a_score = sum(1 for word in company_keywords if word in text_lower)
    b_score = sum(1 for word in employee_table_keywords if word in text_lower)

    if a_score > b_score and a_score >= 1:
        return "A"
    elif b_score > a_score and b_score >= 1:
        return "B"
    else:
        return "Unknown"


# --- פונקציה כללית המפעילה את שאר הפונקציות  ---
def process_pdf(path: str):
    #is_textual_pdf שליחה ל 
    is_textual=is_textual_pdf(path)
    print(f"הדף טקסטואלי: {is_textual}")
    if is_textual:
        text = extract_text_from_textual_pdf(path)
    else:
        text = extract_text_from_scanned_pdf(path)
        
    #שליחה לפונקציה הבודקת מאיזה סוג המסמך
    report_type = detect_report_type(text)

    normalized = None
    if report_type == "A":
        #mutate.py   שליחה  לפונקציה בקובץ Aאם המסמך מסוג   
        normalized = normalize_report_a(text)
        #חדש עם התוכן המתוקן PFD יצירת קובץ
        output_path = path.replace(".pdf", "_fixed.pdf")
        create_pdf_from_text(output_path, text, normalized)
        print("\n===== טקסט לאחר תיקון =====\n")
        print(normalized)
        print("\n============================\n")

    
    return {
        "file": os.path.basename(path),
        "is_textual": is_textual,
        "report_type": report_type,
        "preview": text[:300],
        "normalized": normalized,
    }


# --- דוגמה לשימוש ---
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(BASE_DIR, "data", "a_r_9.pdf")
    # path = os.path.join(BASE_DIR, "data", "a_r_25.pdf")
    # path = os.path.join(BASE_DIR, "data", "n_r_5_n.pdf")
    # path = os.path.join(BASE_DIR, "data", "n_r_10_n.pdf")

    result = process_pdf(path)
