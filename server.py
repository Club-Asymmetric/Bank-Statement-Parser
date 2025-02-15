import os
import subprocess
from flask import Flask, request, jsonify
from pypdf import PdfReader, PdfWriter

UPLOAD_FOLDER = "uploads"
BANK_STATEMENTS_FOLDER = "bank_statements"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BANK_STATEMENTS_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files or "password" not in request.form:
        return jsonify({"success": False, "message": "Missing file or password"}), 400
    
    file = request.files["file"]
    password = request.form["password"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    unlocked_file_path = os.path.join(BANK_STATEMENTS_FOLDER, file.filename)

    if unlock_pdf(file_path, unlocked_file_path, password):
        # Run main.py to process the bank statements
        subprocess.run(["python", "main.py"])
        
        return jsonify({"success": True, "message": "PDF unlocked & processing started!"})
    else:
        return jsonify({"success": False, "message": "Incorrect password or failed to unlock PDF"}), 400

def unlock_pdf(file_path, output_path, password):
    """Tries to unlock a password-protected PDF file."""
    try:
        reader = PdfReader(file_path)
        
        if reader.is_encrypted:
            if reader.decrypt(password):  
                writer = PdfWriter()
                
                for page in reader.pages:
                    writer.add_page(page)
                
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                return True
            else:
                return False
        else:
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    app.run(debug=True)
