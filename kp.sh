$bad_processes = @("malware.exe", "suspicious.exe")
Get-Process | Where-Object { $bad_processes -contains $_.Name } | Stop-Process -Force
