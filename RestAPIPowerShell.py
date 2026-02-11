from flask import Flask, request, jsonify
import subprocess, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")

@app.route('/run-script', methods=['POST'])
def run_script():
    # Check API key
    received_key = request.headers.get("x-api-key")
    if received_key != API_KEY:
        return jsonify({"error": "Unauthorized - Invalid API Key"}), 401

    try:
        data = request.json or {}

        upn = data.get("upn")
        action = data.get("action")

        # Basic validation
        if not upn or not action:
            return jsonify({
                "error": "Missing required fields",
                "required": ["upn", "action"]
            }), 400

        if action not in ["Enable", "Unlock"]:
            return jsonify({
                "error": "Invalid action",
                "allowed_actions": ["Enable", "Unlock"]
            }), 400

        script_path = r".\PowerShellScripts\UserAccountActionScript.ps1" #NEEDS CHANGE

        result = subprocess.run(
            [
                r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", script_path,
                "-UPN", upn,
                "-Action", action
            ],
            capture_output=True, #This is the output send back from PowerShell
            text=True
        )

        status = result.stdout.strip()

        return jsonify({
            "upn": upn,
            "action": action,
            "status": status,
            "stderr": result.stderr.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

'''
Test endpoint in PowerShell on cmd

$uri = "http://localhost:5000/run-script"
$apiKey = "Paste API key here"

$body = @{
    upn    = "user@domain.com"
    action = "Unlock"
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri $uri `
    -Method Post `
    -Headers @{ "x-api-key" = $apiKey } `
    -ContentType "application/json" `
    -Body $body

$response
'''