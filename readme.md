# AD Automation: Power Automate → PowerShell REST API

Execute on-premises Active Directory PowerShell scripts securely from Power Automate using a **Flask REST API** (running via Waitress) and the **Microsoft On-Premises Data Gateway**.

This solution allows cloud-based flows to trigger sensitive AD tasks (Enable/Unlock) on a local Domain Controller without manual intervention.

---

## 📁 Repository Structure

```text
FlaskToPowerAutomate/
│
├── .venv/                         # Python Virtual Environment (Authorized Sandbox)
├── PowerShellScripts/
│   ├── UserAccountActionScript.ps1      # Main AD Logic (Enable/Unlock)
│   └── UserAccountActionLog.txt       # Local execution logs
│
├── .env                           # API Key storage (Create manually!)
├── .gitignore                     # Git configuration to ignore sensitive files
├── requirements.txt               # Python dependencies list
└── RestAPIunattended.py           # Production Flask API (Waitress)
```

---

## ⚙️ Prerequisites & Setup

### 1. Identity & Permissions
* **Service Account:** Create a dedicated AD service account (e.g., `svc_automation`).
* **Delegation:** Delegate "Reset Password" and "Read/Write UserAccountControl" permissions to this account for the target Organizational Unit (OU).

### 2. Software Requirements
* **Git:** To clone the repository.
* **Python 3.10+:** Ensure "Add to PATH" is selected during installation.
* **On-Premises Data Gateway:** [Download Standard Mode Here](https://aka.ms/onpremgateway). Install it and link it to your Power Automate environment.

### 3. Environment Initialization
Clone the repository and set up the isolated Python environment to prevent conflicts:

```powershell
# 1. Clone the repository
git clone https://github.com/LuzCabreraRios/Flask C:\RestAPI

# 2. Go to your project folder
cd C:\RestAPI

# 3. Create the virtual environment (folder named 'venv')
python -m venv venv

# 4. Activate it (You will see (venv) appear in the prompt)
.\venv\Scripts\activate

# 5. Install the required libraries ONLY inside this bubble
pip install flask python-dotenv waitress
```

### 4. Configuration (.env)
Create a file named `.env` in the root folder to store your secrets:
```ini
API_KEY=YourSuperSecretKeyHere
```

---

## 🚀 Deployment (Unattended Mode)

To ensure the API runs 24/7 without a user logged in, use the **Windows Task Scheduler**.

### Step 1: Create Task
* **Name:** `AD Automation API`
* **Security:** Select **"Run whether user is logged on or not"** and check **"Run with highest privileges"**.
* **Configure for:** Windows Server 2022.

### Step 2: Trigger
* Set to **"At Startup"**.

### Step 3: Action
* **Action:** Start a program.
* **Program/script:** Browse to your venv Python executable:
    `C:\RestAPI\venv\Scripts\python.exe`
* **Add arguments:** `RestAPIunattended.py`
* **Start in:** `C:\RestAPI`
    *(Crucial: Python needs this to find the .env file)*

### Step 4: Reliability (Settings)
* Uncheck "Stop the task if it runs longer than...".
* Set **"If the task fails, restart every:"** to **1 minute**.

---

## 🔌 Power Automate Integration

### Custom Connector Setup
1.  **General:** Enable **"Connect via on-premises data gateway"**.
2.  **Security:** API Key (`x-api-key`).
3.  **Definition (POST):**
    * **Body Schema:** `{"upn": "user@wsc.local", "action": "Unlock"}`
    * **Response Schema:** `{"upn": "string", "action": "string", "status": "string", "stderr": "string"}`

### Local Testing (PowerShell)
You can test the API locally before connecting it to the cloud:

```powershell
$uri = "http://localhost:5000/run-script"
$apiKey = "YourSuperSecretKeyHere"

$body = @{
    upn    = "temp30@wsc.local"
    action = "Unlock"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri $uri -Method Post -Headers @{"x-api-key"=$apiKey} -ContentType "application/json" -Body $body
$response
```

---

## 🛡️ Security Features
* **Validation Gatekeeper:** Both Python and PowerShell scripts only allow `"Enable"` and `"Unlock"` actions. `"Disable"` or `"Delete"` commands are strictly blocked.
* **Process Isolation:** The API runs within a `venv` to prevent global library conflicts.
* **Audit Logging:** Every action is logged with a timestamp to `UserAccountActionLog.txt`.