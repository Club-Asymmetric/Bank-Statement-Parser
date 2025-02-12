import pdfplumber
import pandas as pd
import re

def extract_icici_axis_bank(pdf_path, excel_path):
    transactions = []
    previous_balance = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Match transaction date
                date_match = re.search(r'\d{2}-\d{2}-\d{4}', line)
                if date_match:
                    date = date_match.group(0)
                    numbers = re.findall(r'[-+]?\d{1,3}(?:,\d{3})*\.\d+', line)
                    
                    if len(numbers) >= 1:
                        try:
                            amount = float(numbers[0].replace(',', ''))
                            transaction_type = "DR" if "DR" in line else "CR" if "CR" in line else None
                            
                            deposit, withdrawal = 0.0, 0.0
                            if transaction_type == "CR":
                                deposit = amount
                                if previous_balance is not None:
                                    previous_balance += deposit
                            elif transaction_type == "DR":
                                withdrawal = amount
                                if previous_balance is not None:
                                    previous_balance -= withdrawal

                            transactions.append({
                                'Date': date,
                                'Transaction Details': 'Transaction',
                                'Deposits': deposit,
                                'Withdrawals': withdrawal,
                                'Balance': previous_balance if previous_balance is not None else "Unknown"
                            })

                        except ValueError:
                            continue
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    # Save to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ICICI_Axis Bank Statement')

    print(f"Successfully extracted {len(transactions)} transactions to {excel_path}")
    return df
