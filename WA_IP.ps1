# WA_IP.ps1

# Function to list network adapters
function Get-NetworkAdapters {
    return Get-NetAdapter | Select-Object -Property Name, InterfaceDescription, Status
}

# Function to start Wireshark capture on a specific adapter
function Start-WiresharkCapture {
    param (
        [string]$AdapterName
    )

    # Path to Wireshark executable
    $wiresharkPath = "C:\Program Files\Wireshark\Wireshark.exe"

    # Check if Wireshark is installed
    if (-not (Test-Path $wiresharkPath)) {
        Write-Host "Wireshark is not installed at the specified path."
        exit
    }

    # Start Wireshark capture on the selected adapter
    Start-Process -FilePath $wiresharkPath -ArgumentList "-i `"$AdapterName`"" -NoNewWindow
}

# Main script logic
Write-Host "[+] Found $(Get-NetworkAdapters | Measure-Object).Count Network Adapters..."
Write-Host "Choose the right one:"

# Display network adapters with indices
$adapters = Get-NetworkAdapters
for ($i = 0; $i -lt $adapters.Count; $i++) {
    Write-Host "$($i + 1)) $($adapters[$i].Name) - $($adapters[$i].InterfaceDescription)"
}

# Prompt user for selection
$choice = Read-Host "Enter your choice"
if ($choice -ge 1 -and $choice -le $adapters.Count) {
    $selectedAdapter = $adapters[$choice - 1].Name
    Write-Host "[+] Choosing Network Adapter [$selectedAdapter] for Sniffing..."
    Start-WiresharkCapture -AdapterName $selectedAdapter
} else {
    Write-Host "Invalid choice. Exiting."
}