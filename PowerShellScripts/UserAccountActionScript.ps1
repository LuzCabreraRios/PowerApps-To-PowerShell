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
    switch ($Action) {
        "Unlock" {
            Unlock-ADAccount -Identity $UPN -ErrorAction Stop
            $message = "SUCCESS - $UPN was unlocked."
        }

        "Enable" {
            Enable-ADAccount -Identity $UPN -ErrorAction Stop
            $message = "SUCCESS - $UPN was enabled."
        }
    }

    "$(Get-Date) : $message" | Out-File $logPath -Append
    Write-Output "Success"
}
catch {
    $errorMessage = $_.Exception.Message
    "$(Get-Date) : FAILED - $Action - $UPN - $errorMessage" | Out-File $logPath -Append
    Write-Output "Failed: $errorMessage"
}