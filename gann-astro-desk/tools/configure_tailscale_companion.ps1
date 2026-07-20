[CmdletBinding()]
param(
    [string]$MsiPath = '',

    [string]$InstallDirectory = 'D:\Tailscale',

    [Parameter(Mandatory = $true)]
    [string]$GatewayExecutable,

    [string]$ResultPath = 'D:\GannFinancialAstro\tmp\tailscale_companion_setup.json',

    [switch]$SkipInstall
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this script from an elevated PowerShell process.'
}

$resolvedGateway = (Resolve-Path -LiteralPath $GatewayExecutable).Path
$resultDirectory = Split-Path -Parent $ResultPath
New-Item -ItemType Directory -Force -Path $resultDirectory | Out-Null
$resolvedMsi = $null
$signature = $null
$installerExitCode = 0
if (-not $SkipInstall) {
    if (-not $MsiPath) {
        throw 'MsiPath is required unless SkipInstall is set.'
    }
    $resolvedMsi = (Resolve-Path -LiteralPath $MsiPath).Path
    $signature = Get-AuthenticodeSignature -LiteralPath $resolvedMsi
    if ($signature.Status -ne [System.Management.Automation.SignatureStatus]::Valid -or
        $signature.SignerCertificate.Subject -notmatch 'O=Tailscale Inc\.') {
        throw "Refusing to install an unsigned or unexpected MSI signer: $($signature.Status) $($signature.SignerCertificate.Subject)"
    }
    New-Item -ItemType Directory -Force -Path $InstallDirectory | Out-Null
    $logPath = Join-Path $resultDirectory 'tailscale_msi_install.log'
    $msiArguments = @(
        '/i'
        "`"$resolvedMsi`""
        '/qn'
        '/norestart'
        "INSTALLDIR=`"$InstallDirectory`""
        'TS_UNATTENDEDMODE="always"'
        'TS_INSTALLUPDATES="always"'
        'TS_ALLOWINCOMINGCONNECTIONS="always"'
        '/L*v'
        "`"$logPath`""
    )
    $installer = Start-Process -FilePath 'msiexec.exe' -ArgumentList $msiArguments -Wait -PassThru -WindowStyle Hidden
    $installerExitCode = $installer.ExitCode
    if ($installerExitCode -notin @(0, 3010)) {
        throw "Tailscale MSI installation failed with exit code $installerExitCode. See $logPath"
    }
}

$disabledRules = @()
Get-NetFirewallApplicationFilter -PolicyStore PersistentStore |
    Where-Object { $_.Program -ieq $resolvedGateway } |
    Get-NetFirewallRule | ForEach-Object {
    $rule = $_
    $port = $rule | Get-NetFirewallPortFilter -ErrorAction SilentlyContinue
    if ($rule.Direction -eq 'Inbound' -and
        $rule.Action -eq 'Block' -and
        $port.Protocol -eq 'TCP') {
        Disable-NetFirewallRule -Name $rule.Name | Out-Null
        $disabledRules += $rule.Name
    }
}

$ruleName = 'Gann Astro Companion HTTPS 9443 - Tailscale only'
Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue |
    Remove-NetFirewallRule -ErrorAction SilentlyContinue
New-NetFirewallRule `
    -DisplayName $ruleName `
    -Direction Inbound `
    -Action Allow `
    -Enabled True `
    -Profile Any `
    -Program $resolvedGateway `
    -Protocol TCP `
    -LocalPort 9443 `
    -RemoteAddress '100.64.0.0/10' | Out-Null

$lanRuleName = 'Gann Astro Companion HTTPS 9443 - private LAN'
Get-NetFirewallRule -DisplayName $lanRuleName -ErrorAction SilentlyContinue |
    Remove-NetFirewallRule -ErrorAction SilentlyContinue
New-NetFirewallRule `
    -DisplayName $lanRuleName `
    -Direction Inbound `
    -Action Allow `
    -Enabled True `
    -Profile Private `
    -Program $resolvedGateway `
    -Protocol TCP `
    -LocalPort 9443 `
    -RemoteAddress 'LocalSubnet' | Out-Null

$service = Get-Service -Name 'Tailscale'
$tailscaleExe = Join-Path $InstallDirectory 'tailscale.exe'
$result = [ordered]@{
    completedAtUtc = [DateTime]::UtcNow.ToString('o')
    msiPath = $resolvedMsi
    msiSha256 = if ($resolvedMsi) { (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedMsi).Hash } else { $null }
    signer = if ($signature) { $signature.SignerCertificate.Subject } else { $null }
    installSkipped = [bool]$SkipInstall
    installDirectory = $InstallDirectory
    tailscaleExe = $tailscaleExe
    serviceStatus = [string]$service.Status
    unattendedPolicy = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Policies\Tailscale' -ErrorAction SilentlyContinue).UnattendedMode
    gatewayExecutable = $resolvedGateway
    disabledExactTcpBlockRules = $disabledRules
    firewallRule = $ruleName
    lanFirewallRule = $lanRuleName
    firewallRemoteAddress = '100.64.0.0/10'
    firewallPort = 9443
    rebootRequired = $installerExitCode -eq 3010
}
$result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ResultPath -Encoding UTF8
$result | ConvertTo-Json -Depth 5
