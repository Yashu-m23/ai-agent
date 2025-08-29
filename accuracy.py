import pandas as pd
import numpy as np

def approximately_equal(a, b, tol=0.01):
    if pd.isna(a) and pd.isna(b):
        return True
    try:
        return abs(float(a) - float(b)) <= tol
    except:
        return str(a).strip().lower() == str(b).strip().lower()

def detailed_field_accuracy(df_expected, df_actual):
    df_expected = df_expected.reset_index(drop=True)
    df_actual = df_actual.reset_index(drop=True)

    df_actual = df_actual[df_expected.columns]

    total_fields = df_expected.size  
    match_count = 0

    for i in range(len(df_expected)):
        for col in df_expected.columns:
            val_exp = df_expected.at[i, col]
            val_act = df_actual.at[i, col] if i < len(df_actual) else None
            if approximately_equal(val_exp, val_act):
                match_count += 1

    accuracy = (match_count / total_fields) * 100 if total_fields > 0 else 0.0
    print(f"Detailed field-level accuracy: {accuracy:.2f}%")
    return accuracy


if __name__ == "__main__":
    import importlib.util

    expected_df = pd.read_csv('data/icici/icici_sample.csv')

    parser_path = 'custom_parsers/icici_parser.py'
    spec = importlib.util.spec_from_file_location("icici_parser", parser_path)
    parser_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser_module)

    parsed_df = parser_module.parse('data/icici/icici_sample.pdf')

    detailed_field_accuracy(expected_df, parsed_df)
