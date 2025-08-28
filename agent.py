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
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")
        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"CSV file not found at {csv_path}")
        return pdf_path, csv_path, parser_path

class GenerateNode:
    def run(self, target: str, parser_path: str, fix_params: dict):
        ocr_dpi = fix_params.get("ocr_dpi", 300)

        code_template = '''
import pandas as pd
from pdf2image import convert_from_path
import pytesseract

def parse(pdf_path: str) -> pd.DataFrame:
    try:
        pages = convert_from_path(pdf_path, dpi={ocr_dpi})
        text = ""
        for page in pages:
            text += pytesseract.image_to_string(page) + "\\n"

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

            transactions.append({{
                "Date": date,
                "Description": description,
                "Debit Amt": clean_num(debit),
                "Credit Amt": clean_num(credit),
                "Balance": clean_num(balance),
            }})

        return pd.DataFrame(transactions)

    except Exception as e:
        print(f"[Parser] Error: {{e}}")
        return pd.DataFrame()
'''

        code = code_template.format(ocr_dpi=ocr_dpi)

        os.makedirs(os.path.dirname(parser_path), exist_ok=True)
        with open(parser_path, 'w', encoding='utf-8') as f:
            f.write(code)

        print(f"[Agent] Generated parser at {parser_path} with dpi={ocr_dpi}")

class TestNode:
    def run_with_details(self, parser_path: str, pdf_path: str, csv_path: str):
        spec = importlib.util.spec_from_file_location("parser", parser_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        df_expected = pd.read_csv(csv_path)
        df_actual = module.parse(pdf_path)
        try:
            pd.testing.assert_frame_equal(
                df_actual.reset_index(drop=True),
                df_expected.reset_index(drop=True),
                check_dtype=False,
            )
            print("[Agent] Test result: PASS")
            return True, "", df_actual
        except AssertionError as e:
            print("[Agent] Test result: FAIL")
            print(f"[Agent] Data mismatch: {e}")
            return False, str(e), df_actual

class Graph:
    def __init__(self):
        self.plan_node = PlanNode()
        self.generate_node = GenerateNode()
        self.test_node = TestNode()
        self.fix_params = {
            "ocr_dpi": 300,
        }

    def analyze_failure(self, error_msg: str, df_actual: pd.DataFrame, df_expected: pd.DataFrame):
        print(f"[Agent] Analyzing failure: {error_msg}")
        if len(df_actual) < len(df_expected) * 0.8:
            print("[Agent] Parsed fewer rows than expected; increasing OCR DPI for better extraction.")
            self.fix_params["ocr_dpi"] = min(self.fix_params["ocr_dpi"] + 50, 400)
        else:
            print("[Agent] No significant mismatch in row count; no parameter changes.")

    def run(self, target: str):
        pdf_path, csv_path, parser_path = self.plan_node.run(target)
        df_expected = pd.read_csv(csv_path)

        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"[Agent] Attempt {attempt} of {MAX_ATTEMPTS}")
            self.generate_node.run(target, parser_path, self.fix_params)
            success, error_msg, df_actual = self.test_node.run_with_details(parser_path, pdf_path, csv_path)
            if success:
                print("[Agent] Success! Parser validated.")
                return True
            self.analyze_failure(error_msg, df_actual, df_expected)
            print("[Agent] Retrying with updated parameters...")
        print("[Agent] Failed after max attempts.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Adaptive OCR Agent for ICICI PDF")
    parser.add_argument('--target', required=True, help="Bank target (e.g., icici)")
    args = parser.parse_args()

    graph = Graph()
    success = graph.run(args.target)
    if not success:
        print("[Agent] Agent failed. Please check parser and input files.")

if __name__ == "__main__":
    main()
