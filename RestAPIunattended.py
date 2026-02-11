from flask import Flask, request, jsonify
import subprocess, os
import sys
from dotenv import load_dotenv
from waitress import serve 

# 1. Force Absolute Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
SCRIPT_PATH = os.path.join(BASE_DIR, "PowerShellScripts", "UserAccountActionScript.ps1")

load_dotenv(ENV_PATH)
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("WARNING: API_KEY not found in .env file.")

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
        
        # Security validation
        if action not in ["Enable", "Unlock"]:
             return jsonify({"error": "Invalid action"}), 400

        # 2. Run PowerShell
        result = subprocess.run(
            [
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "-NoProfile",
                "-NonInteractive", 
                "-ExecutionPolicy", "Bypass",
                "-File", SCRIPT_PATH,
                "-UPN", upn,
                "-Action", action
            ],
            capture_output=True, # REQUIRED to populate stdout
            text=True            # REQUIRED to make it a string, not bytes
        )
        
        # 3. Capture the Output safely
        stdout_text = result.stdout.strip() if result.stdout else ""
        stderr_text = result.stderr.strip() if result.stderr else ""

        # If the script failed (non-zero exit code), return error 500
        if result.returncode != 0:
             return jsonify({
                 "error": "Script execution failed", 
                 "details": stderr_text or "No error message captured."
             }), 500

        # 4. Success Response
        return jsonify({
            "upn": upn,
            "action": action,
            "status": stdout_text or "Success (No output returned)", # Fallback text
            "stderr": stderr_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"Server starting on port 5000...")
    print(f"Looking for script at: {SCRIPT_PATH}")
    serve(app, host="0.0.0.0", port=5000)