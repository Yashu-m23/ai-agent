
import pandas as pd
from pdf2image import convert_from_path
import pytesseract

def parse(pdf_path: str) -> pd.DataFrame:
    try:
        pages = convert_from_path(pdf_path, dpi=400)
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page) + "\n"

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        start_index = 0
        for i, line in enumerate(lines):
            if line.lower() == "date":
                start_index = i + 1
                break

        transactions = []
        for idx in range(start_index, len(lines), 5):
            block = lines[idx:idx+5]
            if len(block) < 5:
                break

            date, description, debit, credit, balance = block

            def clean_num(s):
                s = s.replace(",", "").replace("(", "-").replace(")", "").strip()
                try:
                    val = float(s)
                    if val == 0.0:
                        return ""
                    return val
                except:
                    return ""

            transactions.append({
                "Date": date,
                "Description": description,
                "Debit Amt": clean_num(debit),
                "Credit Amt": clean_num(credit),
                "Balance": clean_num(balance),
            })

        return pd.DataFrame(transactions)

    except Exception as e:
        print(f"[Parser] Error: {e}")
        return pd.DataFrame()
