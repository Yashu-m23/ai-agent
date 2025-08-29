# AI-Agent: Custom Bank Statement PDF Parser Generator

An adaptive agent that automatically writes custom parsers to extract transactions from bank statement PDFs. Leveraging Python's pdfplumber for PDF text and table extraction, the agent iteratively tests and improves parser accuracy to generate structured CSV-like output.

## Agent Architecture Overview

The agent orchestrates a 3-node pipeline:

- **PlanNode:** Determines input data paths and output parser location.
- **GenerateNode:** Dynamically writes Python parser code based on target bank and parameters (e.g., OCR DPI).
- **TestNode:** Executes the parser on the PDF and compares output to expected CSV to validate accuracy.

The agent runs multiple attempts, analyzing failure causes (e.g., fewer rows parsed) and adapts parameters (like increasing OCR DPI) to improve parsing until success or max retries.

## Getting Started

### Prerequisites

- Python 3.8+
- Install required packages:

```bash
pip install -r requirements.txt
```


### 5-Step Run Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Yashu-m23/ai-agent.git
   cd ai-agent
   ```

3. **Prepare your input data:**
   Place your bank statement PDF and expected CSV in the folder format:  
   `data/<target>/<target>_sample.pdf`  
   `data/<target>/<target>_sample.csv`  
   For example: `data/icici/icici_sample.pdf` & `data/icici/icici_sample.csv`

4. **Run the agent for your target bank:**
   ```bash
   python agent.py --target icici
   ```

5. **View console output:**
   The agent will generate parsers, run validation tests, retry if necessary, and display pass/fail logs with detailed diagnostics.

6. **Check generated parsers:**
   Custom parser scripts are saved under `custom_parsers/<target>_parser.py`.


**Output/Results**

`[Agent] Attempt 1 of 3`                                           
`[Agent] Generated parser at custom_parsers/icici_parser.py with dpi=300`
`[Agent] Test result: PASS`
`[Agent] Parsing succeeded.`

**Note**
accuracy.py evaluates parser performance by comparing the parsed DataFrame to the expected CSV using tolerant field-level checks for minor numeric and text differences. It outputs a percentage accuracy reflecting correctly parsed fields and dynamically loads the parser to run on the given PDF.
