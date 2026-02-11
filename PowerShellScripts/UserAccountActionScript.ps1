param(
    [Parameter(Mandatory = $true)]
    [string]$UPN,

    [Parameter(Mandatory = $true)]
    [ValidateSet("Enable", "Unlock")]
    [string]$Action
)

# Get the folder where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Log file inside the same folder
$logPath = Join-Path $scriptDir "UserAccountActionLog.txt"

# Ensure log file exists
if (!(Test-Path $logPath)) {
    New-Item -ItemType File -Path $logPath | Out-Null
}

try {
    # 1. Perform the Action
    switch ($Action) {
        "Unlock" {
            Unlock-ADAccount -Identity $UPN -ErrorAction Stop
            $detail = "Account unlocked"
        }

        "Enable" {
            Enable-ADAccount -Identity $UPN -ErrorAction Stop
            $detail = "Account enabled"
        }
    }

    # 2. Build the structured message (Matches your FAILED format)
    # Format: SUCCESS - Action - UPN - Detail
    $message = "SUCCESS - $Action - $UPN - $detail"

    # 3. Log it with Timestamp
    "$(Get-Date) : $message" | Out-File $logPath -Append

    # 4. Return it to Python (Standard Output)
    Write-Output $message
}
catch {
    $errorMessage = $_.Exception.Message
    
    # Build the structured failure message
    $failureMessage = "FAILED - $Action - $UPN - $errorMessage"

    # Log it
    "$(Get-Date) : $failureMessage" | Out-File $logPath -Append

    # Return it to Python
    Write-Output $failureMessage
}