$logs = Get-EventLog -LogName Security -Newest 1000
$logs | Export-Csv -Path "C:\logs\SecurityLogs.csv"
