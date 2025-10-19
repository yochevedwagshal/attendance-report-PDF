import re
from datetime import datetime
# פונקציה המבצעת וריאציה ומחזירה את הטקסט לאחר השינויים
def normalize_report_a(text: str) -> str:
    """
    מקבלת טקסט של דוח סוג A (כפי שחולץ ב-OCR)
    מתקנת שעות כניסה/יציאה ועמודת 100% לפי כללים הגיוניים.
    מחזירה טקסט מעודכן.
    """

    lines = text.splitlines()
    updated_lines = []

    for line in lines:
        # נבדוק אם זו שורה שכנראה מכילה שעות (לפי דפוס)
        if re.search(r'\d{1,2}:\d{2}\s+\d{1,2}:\d{2}', line):
            # חילוץ שעות
            match = re.search(r'(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})', line)
            if match:
                start_time_str, end_time_str = match.groups()

                try:
                    start = datetime.strptime(start_time_str, "%H:%M")
                    end = datetime.strptime(end_time_str, "%H:%M")

                    # אם שעת יציאה קטנה משעת כניסה – נחליף ביניהן
                    if end <= start:
                        line = line.replace(start_time_str, end_time_str, 1)
                        line = line.replace(end_time_str, start_time_str, 1)
                        print(f"⚠️ שורה עם כניסה/יציאה לא תקינות תוקנה: {line}")

                except ValueError:
                    pass

            # תיקון ערך 100% (נניח שהוא בא אחרי העמודה "סה\"כ")
            parts = re.split(r'\s+', line.strip())

            # נמצא את האינדקס של הערך של "סה\"כ" – שהוא הערך לפני 100%
            total_index = None
            for i, part in enumerate(parts):
                # נזהה ערך שכנראה מייצג את הסה"כ (לרוב בין 4–12 שעות)
                if re.match(r'^\d+(\.\d+)?$', part):
                    try:
                        value = float(part)
                        if 3 < value <= 12:  # שעות עבודה רגילות
                            total_index = i
                    except ValueError:
                        continue

            if total_index is not None and total_index + 1 < len(parts):
                next_part = parts[total_index + 1]
                if re.match(r'^\d+(\.\d+)?$', next_part):
                    try:
                        value = float(next_part)
                        if value > 9:
                            parts[total_index + 1] = "9.00"
                            print(f"⚠️ ערך 100% עודכן ל-9: {line}")
                    except ValueError:
                        pass

            line = " ".join(parts)

        updated_lines.append(line)

    return "\n".join(updated_lines)
