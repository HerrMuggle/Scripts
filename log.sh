Get-EventLog -LogName Security -InstanceId 4625 -Newest 20 | Format-Table TimeGenerated, Message -AutoSize
