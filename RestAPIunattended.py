from flask import Flask, request, jsonify
import subprocess, os
import sys
from dotenv import load_dotenv
from waitress import serve # pip install waitress

# 1. Force Absolute Paths
# Get the folder where this python script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
SCRIPT_PATH = os.path.join(BASE_DIR, "PowerShellScripts", "UserAccountActionScript.ps1")

load_dotenv(ENV_PATH)
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")

@app.route('/run-script', methods=['POST'])
def run_script():
    received_key = request.headers.get("x-api-key")
    if received_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.json or {}
        upn = data.get("upn")
        action = data.get("action")

        if not upn or not action:
            return jsonify({"error": "Missing fields"}), 400

        # ... (Validation logic remains the same) ...

        # 2. Run PowerShell
        # Note: We do NOT pass credentials here. The Service (Phase 3) handles auth.
        result = subprocess.run(
            [
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "-NoProfile",
                "-NonInteractive", # Important for background tasks
                "-ExecutionPolicy", "Bypass",
                "-File", SCRIPT_PATH, # Uses absolute path
                "-UPN", upn,
                "-Action", action
            ],
            capture_output=True,
            text=True
        )
        
        # Check standard error for PowerShell specific errors
        if result.returncode != 0:
             return jsonify({"error": "Script failed", "details": result.stderr}), 500

        return jsonify({
            "upn": upn,
            "status": result.stdout.strip(),
            "stderr": result.stderr.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 3. Use Waitress for Production
    print("Starting server on port 5000...")
    serve(app, host="0.0.0.0", port=5000)