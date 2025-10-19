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
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



# --- 1. בדיקה אם PDF הוא טקסטואלי (שכבת טקסט) ---
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
#מתקן את הזווית של התמונה עובד?????????
def preprocess_image_for_ocr(pil_image):
    """
    מבצע תיקון זוית, שיפור קונטרסט והפיכת התמונה לשחור-לבן.
    """
    # המרה ל־OpenCV
    img = np.array(pil_image.convert('L'))  # גווני אפור

    # בינאריזציה (שחור-לבן חזק)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # תיקון זוית (deskew)
    coords = np.column_stack(np.where(thresh < 255))
    angle = cv2.minAreaRect(coords)[-1]
    print(f"Detected angle: {angle}")
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = thresh.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    Image.fromarray(rotated).save("debug_rotated.png")
    print("Saved debug_rotated.png for inspection.")
    return Image.fromarray(rotated)
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
            processed = preprocess_image_for_ocr(img)

            text = pytesseract.image_to_string(processed, lang=lang)
            all_text += text + "\n"
    except Exception as e:
        print(f"[extract_text_from_scanned_pdf] error: {e}", file=sys.stderr)
    return all_text.strip()


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
        "חודש"
    ]

    a_score = sum(1 for word in company_keywords if word in text_lower)
    b_score = sum(1 for word in employee_table_keywords if word in text_lower)

    if a_score > b_score and a_score >= 1:
        return "A"
    elif b_score > a_score and b_score >= 1:
        return "B"
    else:
        return "Unknown"



# --- פונקציה מאוחדת לחילוץ וזיהוי ---
def process_pdf(path: str):
    """
    מקבלת קובץ PDF והאם הוא טקסטואלי או סרוק.
    מחזירה dict עם טקסט וסוג הדוח.
    """
    is_textual=is_textual_pdf(path)
    print(is_textual)
    if is_textual:
        text = extract_text_from_textual_pdf(path)
        # print(text)
        
    else:
        text = extract_text_from_scanned_pdf(path)
        print(text)


    report_type = detect_report_type(text)

    return {
        "file": os.path.basename(path),
        "is_textual": is_textual,
        "report_type": report_type,
        "preview": text[:300]  # הצצה ל-300 תווים ראשונים
    }


# --- דוגמה לשימוש ---
if __name__ == "__main__":
    # path = r"C:\Users\ALTER\Desktop\כבי וגשל\taskToSendInPython\data\lesson1.pdf"
    # path = r"C:\Users\ALTER\Desktop\כבי וגשל\taskToSendInPython\data\a_r_9.pdf"
    # path = r"C:\Users\ALTER\Desktop\כבי וגשל\taskToSendInPython\data\a_r_25.pdf"
    # path = r"C:\Users\ALTER\Desktop\כבי וגשל\taskToSendInPython\data\n_r_5_n.pdf"
    # path = r"C:\Users\ALTER\Desktop\כבי וגשל\taskToSendInPython\data\n_r_10_n.pdf"

    result = process_pdf(path)
    print(result)
