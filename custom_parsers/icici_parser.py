import pandas as pd
import pdfplumber
import numpy as np

def parse(pdf_path: str) -> pd.DataFrame:
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
        print(f"[Parser] Error: {e}")
        return pd.DataFrame()
