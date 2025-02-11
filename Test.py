import pdfplumber
import pandas as pd
import re

def extract_transactions(pdf_path, excel_path):
    transactions = []
    previous_balance = None
    opening_balance = None
    last_balance = None
    opening_balance_found = False
    first_transaction_date = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Try to find explicit opening balance first
                if "Opening Balance" in line and not opening_balance_found:
                    numbers = re.findall(r'[\d,]+\.\d+', line)
                    if numbers:
                        opening_balance = float(numbers[-1].replace(',', ''))
                        previous_balance = opening_balance
                        opening_balance_found = True
                        
                        # Extract date if available in opening balance line
                        date_match = re.search(r'(\d{2}-\d{2}-\d{4})|(\d{1,2}\s?[A-Za-z]{3}\s?\d{4})', line)
                        opening_date = date_match.group(0) if date_match else ''
                        
                        transactions.append({
                            'Date': opening_date,
                            'Transaction Details': 'Opening Balance',
                            'Deposits': 0.0,
                            'Withdrawals': 0.0,
                            'Balance': opening_balance
                        })
                    continue

                # Match date pattern (DD-MM-YYYY or DD MMM YYYY)
                date_match = re.match(r'(\d{2}-\d{2}-\d{4})|(\d{1,2}\s?[A-Za-z]{3}\s?\d{4})', line)

                if date_match:
                    date = date_match.group(0)
                    
                    # Capture first transaction date
                    if first_transaction_date is None:
                        first_transaction_date = date

                    # Extract numerical values (amounts & balance)
                    numbers = re.findall(r'[\d,]+\.\d+', line)

                    if len(numbers) >= 2:  # We need at least amount and balance
                        try:
                            balance = float(numbers[-1].replace(',', ''))
                            amount = float(numbers[-2].replace(',', ''))

                            # If no opening balance was found, use the logic for first transaction
                            if not opening_balance_found and len(transactions) == 0:
                                # For first transaction, determine if it's deposit or withdrawal
                                opening_balance = balance - amount
                                previous_balance = opening_balance
                                
                                # Add opening balance entry
                                transactions.append({
                                    'Date': date,
                                    'Transaction Details': 'Opening Balance',
                                    'Deposits': 0.0,
                                    'Withdrawals': 0.0,
                                    'Balance': opening_balance
                                })
                                
                                # Now add the first transaction
                                deposit = amount if balance > opening_balance else 0.0
                                withdrawal = amount if balance < opening_balance else 0.0
                                
                                transactions.append({
                                    'Date': date,
                                    'Transaction Details': 'Transaction',
                                    'Deposits': deposit,
                                    'Withdrawals': withdrawal,
                                    'Balance': balance
                                })
                                
                                previous_balance = balance
                                continue

                            # For subsequent transactions
                            deposit = 0.0
                            withdrawal = 0.0

                            if previous_balance is not None:
                                if balance < previous_balance:
                                    withdrawal = previous_balance - balance
                                elif balance > previous_balance:
                                    deposit = balance - previous_balance

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

    # Append Closing Balance
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
        df.to_excel(writer, index=False, sheet_name='Bank Statement')

    print(f"Successfully extracted {len(transactions)} transactions to {excel_path}")
    return df

# Example Usage
pdf_path = "bank_statement.pdf"
excel_path = "bank_statement.xlsx"
df = extract_transactions(pdf_path, excel_path)

# Print first few transactions for verification
print(df.head())