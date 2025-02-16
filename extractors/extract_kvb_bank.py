import pdfplumber
import pandas as pd
import re

def extract_kvb_bank(pdf_path, excel_path):
    transactions = []
    previous_balance = None
    opening_balance = None
    last_balance = None
    opening_balance_found = False

    # Month mapping for formatting dates
    month_map = {
        "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
        "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
    }

    def format_date(date_str):
        match = re.match(r'(\d{2})-([A-Za-z]{3})-(\d{4})', date_str.upper())
        if match:
            day, month, year = match.groups()
            return f"{day}-{month_map.get(month, month)}-{year}"
        return date_str

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            lines = page.extract_text().split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Match opening balance explicitly mentioned
                if "B/F" in line and not opening_balance_found:
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

                # Match transaction date (Format: DD-MMM-YYYY or similar)
                date_match = re.match(r'\d{2}-[A-Za-z]{3}-\d{4}', line)
                if date_match:
                    date = format_date(date_match.group(0))
                    numbers = re.findall(r'[-+]?\d{1,3}(?:,\d{3})*\.\d+', line)

                    if len(numbers) == 3:
                        try:
                            debit, credit, balance = map(lambda x: float(x.replace(',', '')), numbers)

                            transactions.append({
                                'Date': date,
                                'Transaction Details': 'Transaction',
                                'Deposits': credit,
                                'Withdrawals': debit,
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

    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    print(f"Successfully extracted {len(transactions)} transactions to {excel_path}")
    return df