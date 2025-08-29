import pandas as pd
import pdfplumber
import numpy as np
from pdf2image import convert_from_path
import pytesseract

def ocr_parse(pdf_path: str, ocr_dpi=300) -> pd.DataFrame:
    try:
        pages = convert_from_path(pdf_path, dpi=ocr_dpi)
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
                        return np.nan
                    return val
                except:
                    return np.nan

            transactions.append({
                "Date": date,
                "Description": description,
                "Debit Amt": clean_num(debit),
                "Credit Amt": clean_num(credit),
                "Balance": clean_num(balance),
            })

        return pd.DataFrame(transactions)

    except Exception as e:
        print(f"[OCR Parser] Error: {e}")
        return pd.DataFrame()


def pdfplumber_parse(pdf_path: str) -> pd.DataFrame:
    def clean_num(value):
        if value is None:
            return np.nan
        s = str(value).replace(",", "").replace("(", "-").replace(")", "").strip()
        try:
            val = float(s)
            return np.nan if val == 0.0 else val
        except:
            return np.nan

    try:
        rows = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if len(row) != 5:
                            continue
                        if row[0] is None or row[0].strip().lower() == "date":
                            continue
                        date = row[0].strip()
                        desc = row[1].strip() if row[1] else ''
                        debit = clean_num(row[2])
                        credit = clean_num(row[3])
                        balance = clean_num(row[4])

                        rows.append({
                            "Date": date,
                            "Description": desc,
                            "Debit Amt": debit,
                            "Credit Amt": credit,
                            "Balance": balance,
                        })
        return pd.DataFrame(rows)

    except Exception as e:
        print(f"[pdfplumber Parser] Error: {e}")
        return pd.DataFrame()

def combined_parse(pdf_path: str, min_rows=20, ocr_dpi=300) -> pd.DataFrame:
    df = pdfplumber_parse(pdf_path)
    if len(df) < min_rows:
        print(f"[Combined Parser] Direct parsing returned {len(df)} rows which is less than {min_rows}, falling back to OCR.")
        df_ocr = ocr_parse(pdf_path, ocr_dpi=ocr_dpi)
        if len(df_ocr) >= min_rows:
            print(f"[Combined Parser] OCR parser returned {len(df_ocr)} rows. Using OCR output.")
            return df_ocr
        else:
            print(f"[Combined Parser] OCR parser returned only {len(df_ocr)} rows. Using original output.")
    else:
        print(f"[Combined Parser] Direct parsing successful with {len(df)} rows.")
    return df
