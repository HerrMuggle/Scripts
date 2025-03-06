Get-WmiObject -Query "SELECT * FROM Win32_Product" | Select-Object Name, Version
