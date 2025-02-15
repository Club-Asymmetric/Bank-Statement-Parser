# Bank Statement Parser

## Overview
This project provides a bank statement parsing solution for multiple Indian banks. The parser efficiently processes bank statements and extracts relevant financial data.

## Supported Banks
✅ Currently Supporting:
- State Bank of India (SBI)
- ICICI Bank
- Canara Bank
- TMB (Tamilnad Mercantile Bank)

🚧 In Development:
- KVB (Karur Vysya Bank)

## Features
- **Multi-Bank Support**: Process statements from different banks
- **Standardized Output**: Unified data format across banks
- **Easy Integration**: Simple to incorporate into existing systems

| Bank  | Status |
|-------|--------|
| SBI   | ✅ |
| ICICI | ✅ |
| Canara | ✅ |
| TMB   | ✅ |
| KVB   | 🚧 |

---

## How to Run

### 1. Install Dependencies
Ensure you have Python installed (preferably Python 3.8 or later). Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 2. Start the Flask Server
Run the following command to start the backend server:

```bash
python server.py
```

### 3. Open the Web Interface
- Open `static/index.html` in a web browser.
- Upload a password-protected bank statement and enter the correct password.
- The system will unlock the PDF, process the data, and save it in the `output/` folder.

### 4. Process Bank Statements Manually
If you want to process bank statements manually without using the web interface, run:

```bash
python main.py
```

---

## `requirements.txt`
The following dependencies should be added to `requirements.txt`:

```
Flask
pypdf
pdfplumber
openpyxl
pandas
```

Install them using:
```bash
pip install -r requirements.txt
```

---

**Note**: This project is under active development. Future updates will include more bank support and additional features.

