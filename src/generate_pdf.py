from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
#יצירת קובץ חדש
def create_pdf_from_text(output_path: str, original_text: str, normalized_text: str):
    """
    יוצר PDF חדש עם גרסה מקורית וגרסה מתוקנת.
    """
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # כותרת
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, height - 40, "דו\"ח שעות - גרסה מתוקנת")

    # כותרת משנה
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    c.drawString(30, height - 60, "נוצר אוטומטית מתוך סריקה מעודכנת")
    c.setFillColor(colors.black)

    # חלק א' — טקסט מקורי
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 90, "טקסט מקורי:")
    c.setFont("Helvetica", 9)

    y = height - 110
    for line in original_text.splitlines():
        c.drawString(30, y, line[:100])  # חותך שורה ארוכה מדי
        y -= 12
        if y < 150:
            c.showPage()
            y = height - 50

    # חלק ב' — טקסט מעודכן
    c.showPage()  # עמוד חדש
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height - 40, "טקסט לאחר תיקון:")
    c.setFont("Helvetica", 9)

    y = height - 60
    for line in normalized_text.splitlines():
        c.drawString(30, y, line[:100])
        y -= 12
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    print("✅ נוצר קובץ PDF חדש")
