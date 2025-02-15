import pdfplumber
import pandas as pd
import re
    
def extract_icici_bank(pdf_path, excel_path):
    transactions = []
    current_transaction = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")

                for i, line in enumerate(lines):
                    # Match date
                    date_match = re.match(r"(\d{2}-\d{2}-\d{4})", line)
                    type_match = re.search(r"(DR|CR)", line)

                    if date_match:
                        # Save previous transaction if exists
                        if current_transaction:
                            transactions.append(current_transaction)
                        
                        # Start a new transaction
                        current_transaction = {
                            "Date": date_match.group(1),
                            "Transaction Details": "Transaction",  # Default value
                            "Withdraw": "0.00",  # Default to 0.00 if no value
                            "Deposit": "0.00",   # Default to 0.00 if no value
                        }

                    # If "DR" or "CR" is found, capture the transaction type
                    if type_match:
                        transaction_type = type_match.group(1)

                        # The amount is on the next line, so extract it
                        if i + 1 < len(lines):
                            amount_match = re.search(r"(\d+\.\d{2})", lines[i + 1])
                            if amount_match:
                                amount = amount_match.group(1)

                                if transaction_type == "DR":
                                    current_transaction["Withdraw"] = amount
                                else:
                                    current_transaction["Deposit"] = amount

                # Append last transaction
                if current_transaction:
                    transactions.append(current_transaction)

    # Convert to DataFrame
    df = pd.DataFrame(transactions)
    
    # Save to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bank Statement')

    print(f"Successfully extracted {len(transactions)} transactions to {excel_path}")
    return df