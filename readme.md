# **Power Automate → PowerShell Integration with REST API**

Execute on-premises PowerShell scripts securely from Power Automate using a **Flask REST API** and the **Microsoft On-Premises Data Gateway**.

This repository contains my step-by-step guide on how I allowed cloud-based Power Automate flows to trigger PowerShell tasks in my personal laptop, for implementation in AD in a later stage.

---

## **📁 Repository Structure**
```
FlaskToPowerautomate/
│── .venv/
│    ├── RestAPIPowerShell.py                  # Flask REST API
│    └── PowerShellScripts/
│           └── UserAccountActionScript.ps1         # Example AD PowerShell script
```

---

## **📌 Key Files**
- **Flask API (Python):**  
  [`.venv/RestAPIPowerShell.py`](.venv/RestAPIPowerShell.py)

- **PowerShell Script (AD Example):**  
  [`.venv/PowerShellScripts/UserAccountActionScript.ps1`](.venv/PowerShellScripts/UserAccountActionScript.ps1)

---

## **📌 Overview**
This solution enables Power Automate to execute PowerShell `.ps1` scripts on-premises by using:

- A PowerShell script stored locally  
- A lightweight Flask REST API  
- A Microsoft On-Premises Data Gateway  
- A Custom Connector in Power Automate  

Use cases include:  
✔ Disabling or unlocking AD accounts  
✔ Running admin or maintenance scripts  
✔ Returning logs or execution status to Power Automate  

---

# **🧩 Step 1 – Create a Local PowerShell Script**

Below is the example validation script.  
Your production script (e.g., `DisableUser.ps1`) should follow similar structure.

### **📄 Example Script (DisableUser.ps1)**  
[`DisableUser.ps1`](.venv/PowerShellScripts/DisableUser.ps1)

```powershell
# DisableUser.ps1
param(
    [string]$UserUPN
)

Disable-ADAccount -Identity $UserUPN

Write-Output "User $UserUPN has been disabled."
```

---

# **🖥 Step 2 – Flask REST API**

The Python API is located at:

**📄 Flask API File:**  
[`RestAPIPowerShell.py`](.venv/RestAPIPowerShell.py)

This API:

- Validates an API Key  
- Receives a username or UPN from Power Automate  
- Executes the PowerShell script  
- Returns body to Power Automate
- Test your endpoint locally
```powershell
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
```

---

# **🔌 Step 3 – Install & Configure the On-Premises Data Gateway**

1. Download: https://aka.ms/onpremgateway  
2. Install on the machine running the Flask API  
3. Sign in using your Power Automate account/Service Account 
4. Select or create a gateway  
5. Confirm the gateway status is **Online**  

The gateway provides secure connectivity between cloud and on-prem systems.

---

# **⚙ Step 4 – Create a Custom Connector in Power Automate**

1. Go to **Power Automate → Custom Connectors → New → From blank**
2. **Security:** Basic Authentication (Username and Password), or Windows Auth 
3. **Definition:**
   - Create a POST action  
   - Request headers:  
     - `Content-Type: application/json`  
     - `x-api-key:` *(leave blank)*
   - Request body: {"ADusername": "ADusername", "ADusername": "ADusername"}
   - Response schema: `ADusername`, `stderr`, `status`
   - After creating SHARE CONNECTOR WITH ORGANIZATION
   - Add the connection to your flow or Power App
4. **Test:**  
   - Select your **On-Prem Data Gateway**  
   - Enter your API key  
   - Execute the connector → PowerShell runs locally  

---

# **🚀 Summary**

This repository demonstrates how to trigger internal PowerShell scripts from Power Automate through:

✔ A secure Flask REST API that executes a PowerShell Script  
✔ API Key authentication  
✔ The Microsoft On-Premises Data Gateway  
✔ A Power Automate Custom Connector  

