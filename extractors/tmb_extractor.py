import pdfplumber
import pandas as pd
import re

def extract_tmb_bank(pdf_path, excel_path):
    transactions = []
    previous_balance = None
    opening_balance_found = False
    last_balance = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Match opening balance explicitly mentioned
                if "Opening Balance" in line and not opening_balance_found:
                    numbers = re.findall(r'[-+]?\d{1,3}(?:,\d{3})*\.\d+', line)
                    if numbers:
                        opening_balance = float(numbers[-1].replace(',', ''))
                        previous_balance = opening_balance
                        opening_balance_found = True
                        transactions.append({
                            'Date': '',
                            'Transaction Details': 'Opening Balance',
                            'Deposits': 0.0,
                            'Withdrawals': 0.0,
                            'Balance': opening_balance
                        })
                    continue
                
                # Match transaction date (Formats: DD-MM-YYYY)
                date_match = re.search(r'\d{2}-\d{2}-\d{4}', line)
                if date_match:
                    date = date_match.group(0)
                    numbers = re.findall(r'[-+]?\d{1,3}(?:,\d{3})*\.\d+', line)
                    
                    if len(numbers) >= 1:
                        try:
                            amount = float(numbers[0].replace(',', ''))
                            transaction_type = "Deposit" if "Deposits" in line else "Withdrawal"
                            deposit, withdrawal = (amount, 0.0) if transaction_type == "Deposit" else (0.0, amount)
                            
                            if previous_balance is not None:
                                previous_balance += deposit - withdrawal
                            
                            transactions.append({
                                'Date': date,
                                'Transaction Details': 'Transaction',
                                'Deposits': deposit,
                                'Withdrawals': withdrawal,
                                'Balance': previous_balance if previous_balance is not None else "Unknown"
                            })

                        except ValueError:
                            continue
    
    # Append Closing Balance if available
    if last_balance is not None:
        transactions.append({
            'Date': transactions[-1]['Date'],
            'Transaction Details': 'Closing Balance',
            'Deposits': 0.0,
            'Withdrawals': 0.0,
            'Balance': last_balance
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    # Save to Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='TMB Bank Statement')

    print(f"Successfully extracted {len(transactions)} transactions to {excel_path}")
    return df
