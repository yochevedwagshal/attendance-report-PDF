# 🧾 מערכת חילוץ טקסטים מקבצי PDF סרוקים

פרויקט זה נועד לחלץ טקסטים מתוך קבצי PDF — גם מטקסטים רגילים וגם מקבצים סרוקים באמצעות OCR (זיהוי תווים אופטי).  
המערכת מזהה האם הקובץ הוא טקסטואלי או סרוק, מחלצת את הטקסט, ומסווגת את הדוח לסוג **A** או **B**.

---

## ⚙️ התקנה והפעלה

### דרישות מוקדמות
- Python 3.11 ומעלה  
- Git  
- ספריית **Poppler** (להמרת PDF לתמונות)  
- ספריית **Tesseract OCR** (לקריאת טקסט מתמונות)

---

### 📦 התקנת סביבת העבודה

1. צרי סביבה וירטואלית:
   ```bash
   python -m venv venv
   venv\Scripts\activate


התקיני את הספריות הדרושות:

pip install pdfplumber pdf2image pytesseract pillow pandas opencv-python-headless


ודאי ש־Tesseract מותקן במחשב:

הנתיב צריך להיות (ברירת מחדל):

C:\Program Files\Tesseract-OCR\tesseract.exe


ודאי ש־Poppler מותקן (למשל):

C:\poppler\poppler-25.07.0\Library\bin

🚀 הפעלה

להרצת הקוד הראשי:

python src/extract.py


הקובץ extract.py יקבל קובץ PDF מהנתיב שהוגדר בקוד,
יבדוק אם הקובץ טקסטואלי או סרוק, ויחלץ את הטקסט בהתאם.

🧠 לוגיקת הסיווג

A – קובץ שבו מופיע שם החברה או מחרוזות כמו “חברה”, “בע"מ”, “Company”.

B – קובץ שמכיל טבלה עם “שם העובד”, “סיכום שעות”, “סה"כ לתשלום”, “חודש” וכו'.

אם לא נמצאה התאמה — הסקריפט מחזיר "Unknown".

📂 מבנה הפרויקט
taskToSendInPython/
│
├── data/                ← קבצי PDF לבדיקה
├── src/
│   └── extract.py       ← קובץ הקוד הראשי
├── venv/                ← סביבה וירטואלית (לא חובה להעלות ל־Git)
└── README.md            ← קובץ תיעוד זה

✨ פלט לדוגמה
{
  "file": "a_r_9.pdf",
  "is_textual": False,
  "report_type": "A",
  "preview": "נ.ע. הנשר כח אדם בע\"מ..."
}

🧩 פקודות Git בסיסיות

להעלאה ראשונה ל־GitHub:

git init
git add .
git commit -m "Initial commit - OCR PDF extractor"
git branch -M main
git remote add origin https://github.com/USERNAME/pdf-ocr-extractor.git
git push -u origin main

👩‍💻 מפתחת

פותח ע"י [י_וגשל]
פרויקט לעיבוד מסמכים ו־OCR ב־Python.