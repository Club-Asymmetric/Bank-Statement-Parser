import pdfplumber
import os
from extractors.canara_tmb_extractor import extract_canara_tmb_bank
from extractors.sbi_extractor import extract_sbi_bank
from extractors.icici_extractor import extract_icici_bank
from extractors.extract_kvb_bank import extract_kvb_bank

def detect_bank_type(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages[:2]:  # Read first 2 pages for detection
            text += page.extract_text() + "\n"
        text = text.lower()
        if "canara bank" in text or "opening balance" in text:
            return "Canara TMB (Format)"
        elif "state bank of india" in text:
            return "SBI"
        elif "b/f" in text:
            return "KVB (Format)"
        elif "icici bank" in text or "cr" in text or "dr" in text:
            return "ICICI"

    return None

def main():
    pdf_folder = "bank_statements/"
    output_folder = "output/"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for pdf_file in os.listdir(pdf_folder):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, pdf_file)
            bank_type = detect_bank_type(pdf_path)

            if not bank_type:
                print(f"Unknown bank format for {pdf_file}. Skipping...")
                continue

            excel_path = os.path.join(output_folder, pdf_file.replace(".pdf", ".xlsx"))
            print(f"Processing {pdf_file} as {bank_type}...")

            if bank_type == "Canara TMB (Format)":
                extract_canara_tmb_bank(pdf_path, excel_path)
            elif bank_type == "SBI":
                extract_sbi_bank(pdf_path, excel_path)
            elif bank_type == "ICICI":
                extract_icici_bank(pdf_path, excel_path)
            elif bank_type == "KVB (Format)":
                extract_kvb_bank(pdf_path, excel_path)
            else:
                print(f"No extractor found for {bank_type}. Skipping...")

if __name__ == "__main__":
    main()
