import pdfplumber
import pandas as pd
import re

def extract_canara_tmb_bank(pdf_path, excel_path):
    transactions = []
    previous_balance = None
    opening_balance = None
    last_balance = None
    opening_balance_found = False

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

                # Match transaction date (Formats: DD MMM YYYY, DD-MM-YYYY)
                date_match = re.match(r'\d{2} [A-Za-z]{3} \d{4}|\d{2}-\d{2}-\d{4}', line)
                if date_match:
                    date = date_match.group(0)
                    numbers = re.findall(r'[-+]?\d{1,3}(?:,\d{3})*\.\d+', line)

                    if len(numbers) >= 2:
                        try:
                            balance = float(numbers[-1].replace(',', ''))
                            amount = float(numbers[-2].replace(',', ''))

                            # Determine if deposit or withdrawal based on balance comparison
                            deposit, withdrawal = 0.0, 0.0
                            if previous_balance is not None:
                                if balance > previous_balance:
                                    deposit = amount
                                elif balance < previous_balance:
                                    withdrawal = amount

                            transactions.append({
                                'Date': date,
                                'Transaction Details': 'Transaction',
                                'Deposits': deposit,
                                'Withdrawals': withdrawal,
                                'Balance': balance
                            })
                            previous_balance = balance
                            last_balance = balance
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
        df.to_excel(writer, index=False, sheet_name='Canara Bank Statement')

    print(f"Successfully extracted {len(transactions)} transactions to {excel_path}")
    return df