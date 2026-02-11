# 1. Define the password
$Password = ConvertTo-SecureString "l0ck3d0ut!" -AsPlainText -Force

# 2. Create 'temp30' in the College/Users OU
New-ADUser `
    -Name "Temp 30" `
    -GivenName "Temp" `
    -Surname "30" `
    -SamAccountName "temp30" `
    -UserPrincipalName "temp30@wsc.local" `
    -Path "OU=Users,OU=College,DC=wsc,DC=local" `
    -AccountPassword $Password `
    -Enabled $true `
    -ChangePasswordAtLogon $false

# 3. Confirm they exist
Get-ADUser -Identity temp30