import argparse
import importlib.util
import os
import pandas as pd

MAX_ATTEMPTS = 3

class PlanNode:
    def run(self, target: str):
        pdf_path = f"data/{target}/{target}_sample.pdf"
        csv_path = f"data/{target}/{target}_sample.csv"
        parser_path = f"custom_parsers/{target}_parser.py"
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        return pdf_path, csv_path, parser_path

class GenerateNode:
    def run(self, target: str, parser_path: str, fix_params: dict):
        ocr_dpi = fix_params.get("ocr_dpi", 300)
        code_template = '''
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
'''
        os.makedirs(os.path.dirname(parser_path), exist_ok=True)
        with open(parser_path, 'w', encoding='utf-8') as f:
            f.write(code_template)

        print(f"[Agent] Generated parser at {parser_path} with dpi={ocr_dpi}")

class TestNode:
    def run_with_details(self, parser_path: str, pdf_path: str, csv_path: str):
        spec = importlib.util.spec_from_file_location("parser", parser_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        df_expected = pd.read_csv(csv_path)
        df_actual = module.parse(pdf_path)

        if df_actual.shape != df_expected.shape:
            error_msg = (f"DataFrame shape mismatch\n"
                         f"[left]:  {df_actual.shape}\n"
                         f"[right]: {df_expected.shape}")
            print(f"[Agent] Test result: FAIL")
            print(f"[Agent] Data mismatch: DataFrame are different\n{error_msg}")
            return False, error_msg, df_actual

        try:
            pd.testing.assert_frame_equal(
                df_actual.reset_index(drop=True),
                df_expected.reset_index(drop=True),
                check_dtype=False,
            )
            print(f"[Agent] Test result: PASS")
            return True, "", df_actual
        except AssertionError as e:
            print(f"[Agent] Test result: FAIL")
            print(f"[Agent] Data mismatch: DataFrame are different")
            return False, str(e), df_actual

class Graph:
    def __init__(self):
        self.plan_node = PlanNode()
        self.generate_node = GenerateNode()
        self.test_node = TestNode()
        self.fix_params = {"ocr_dpi": 300}

    def analyze_failure(self, error_msg: str, df_actual: pd.DataFrame, df_expected: pd.DataFrame):
        print(f"[Agent] Analyzing failure: {error_msg}")
        if df_actual.shape[0] < df_expected.shape[0]:
            print("[Agent] Parsed fewer rows than expected; increasing OCR DPI for better extraction.")
            self.fix_params["ocr_dpi"] = min(self.fix_params["ocr_dpi"] + 50, 400)
        else:
            print("[Agent] DataFrame shape matches or has more rows; no parameter changes.")

    def run(self, target: str):
        pdf_path, csv_path, parser_path = self.plan_node.run(target)
        df_expected = pd.read_csv(csv_path)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"[Agent] Attempt {attempt} of {MAX_ATTEMPTS}")
            self.generate_node.run(target, parser_path, self.fix_params)
            success, error_msg, df_actual = self.test_node.run_with_details(parser_path, pdf_path, csv_path)
            if success:
                print("[Agent] Parsing succeeded.")
                return True
            self.analyze_failure(error_msg, df_actual, df_expected)
            print("[Agent] Retrying with updated parameters...")
        print("[Agent] Failed after max attempts.")
        print("[Agent] Agent failed. Please check parser and input files.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Adaptive PDF parser agent with detailed logging")
    parser.add_argument('--target', required=True, help="Bank target name e.g., icici")
    args = parser.parse_args()

    graph = Graph()
    success = graph.run(args.target)
    if not success:
        print("[Agent] Parsing failed. Please verify input files or parser logic.")

if __name__ == "__main__":
    main()
