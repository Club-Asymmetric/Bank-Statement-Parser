import pdfplumber
import os
from extractors.canara_extractor import extract_canara_bank
from extractors.sbi_extractor import extract_sbi_bank
from extractors.icici_axis_extractor import extract_icici_axis_bank
from extractors.tmb_extractor import extract_tmb_bank

def detect_bank_type(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages[:2]:  # Read first 2 pages for detection
            text += page.extract_text() + "\n"

        text = text.lower()

        if "canara bank" in text or "opening balance" in text:
            return "Canara Bank"
        elif "state bank of india" in text or "ifs code sbin" in text or "savingsaccount" in text:
            return "SBI"
        elif "icici bank" in text or "axis bank" in text or "upi/dr" in text:
            return "ICICI_Axis"
        elif "tamilnad mercantile bank" in text or "tmbl" in text:
            return "TMB"
    
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

            if bank_type == "Canara Bank":
                extract_canara_bank(pdf_path, excel_path)
            elif bank_type == "SBI":
                extract_sbi_bank(pdf_path, excel_path)
            elif bank_type == "ICICI_Axis":
                extract_icici_axis_bank(pdf_path, excel_path)
            elif bank_type == "TMB":
                extract_tmb_bank(pdf_path, excel_path)
            else:
                print(f"No extractor found for {bank_type}. Skipping...")

if __name__ == "__main__":
    main()
