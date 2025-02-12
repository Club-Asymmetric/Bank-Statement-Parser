import pdfplumber
import pandas as pd
from datetime import datetime

def extract_sbi_bank(pdf_path, excel_path):
    transactions = []
    opening_balance = None
    closing_balance = None
    balance = None  # Store the current balance

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split('\n'):
                if 'Balance as on' in line:
                    balance = float(line.split()[-1])
                    if opening_balance is None:
                        opening_balance = balance
                    closing_balance = balance
                elif 'TRANSFER' in line:
                    parts = line.split()
                    
                    # Extract date from parts[0:3] (Example: "11 Feb 2025")
                    raw_date = " ".join(parts[0:3])  # Takes Day, Month, Year
                    
                    # Format the date to "DD-MM-YYYY"
                    try:
                        date = datetime.strptime(raw_date, "%d %b %Y").strftime("%d-%m-%Y")
                    except ValueError:
                        date = raw_date  # Keep original format if parsing fails

                    details = 'Transaction'  # Extracting details
                    balance = float(parts[-1].replace(',', ''))  # Extracting balance

                    # Try to determine the correct amount position
                    try:
                        if parts[-1].replace(',', '').replace('.', '').isdigit():  # If last item is a number (balance)
                            if parts[-2].replace(',', '').replace('.', '').isdigit():  # If second last item is a number (withdrawal)
                                amount_str = parts[-2]  # Amount at -2
                            else:
                                amount_str = parts[-3]  # Amount at -3
                    except IndexError:
                        amount_str = "0"

                    # Convert amount to float
                    try:
                        amount = float(amount_str.replace(',', ''))
                    except ValueError:
                        amount = 0.0  # Default if parsing fails

                    # Determine transaction type
                    if 'TRANSFER TO' in line:  # Withdrawal
                        deposits = 0.0
                        withdrawals = amount
                    elif 'TRANSFER FROM' in line:  # Deposit
                        deposits = amount
                        withdrawals = 0.0
                    else:
                        deposits = 0.0
                        withdrawals = 0.0

                    # Append the transaction to the list
                    transactions.append([date, details, deposits, withdrawals, balance])

    # Create a DataFrame from the extracted transactions
    df = pd.DataFrame(transactions, columns=['Date', 'Transaction Details', 'Deposits', 'Withdrawals', 'Balance'])
    
    # Add opening and closing balances
    df = pd.concat([pd.DataFrame([[None, 'Opening Balance', 0.0, 0.0, opening_balance]], columns=df.columns), df])
    last_balance = df['Balance'].iloc[-1] if not df.empty else 0.0
    df = pd.concat([df, pd.DataFrame([[None, 'Closing Balance', 0.0, 0.0, last_balance]], columns=df.columns)])
    
    # Save the DataFrame to an Excel file
    df.to_excel(excel_path, index=False)

    print(f"Successfully extracted transactions to {excel_path}")
    return df
