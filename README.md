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

`pip install -r requirements.txt`


### 5-Step Run Instructions

1. **Clone the repository:**
   `git clone https://github.com/Yashu-m23/ai-agent.git`
   `cd ai-agent`

2. **Prepare your input data:**
   Place your bank statement PDF and expected CSV in the folder format:  
   `data/<target>/<target>_sample.pdf`  
   `data/<target>/<target>_sample.csv`  
   For example: `data/icici/icici_sample.pdf` & `data/icici/icici_sample.csv`

3. **Run the agent for your target bank:**
   `python agent.py --target icici`

4. **View console output:**
   The agent will generate parsers, run validation tests, retry if necessary, and display pass/fail logs with detailed diagnostics.

5. **Check generated parsers:**
   Custom parser scripts are saved under `custom_parsers/<target>_parser.py`.
