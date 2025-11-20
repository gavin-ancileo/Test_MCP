#!/usr/bin/env pwsh
##
# Test DNS resolution on PC
##

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " TESTING DNS & SSL ON YOUR PC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Testing DNS resolution..." -ForegroundColor Yellow
Write-Host ""
nslookup internal.assistant.leacare.ai
Write-Host ""

Write-Host "2. Testing direct IP resolution..." -ForegroundColor Yellow
Write-Host ""
$ips = @("16.176.191.212", "54.252.157.58")
foreach ($ip in $ips) {
    Write-Host "   Resolving IP: $ip" -ForegroundColor Cyan
    nslookup $ip
    Write-Host ""
}

Write-Host "3. Checking proxy settings..." -ForegroundColor Yellow
netsh winhttp show proxy
Write-Host ""

Write-Host "4. Checking hosts file..." -ForegroundColor Yellow
$hostsContent = Get-Content "C:\Windows\System32\drivers\etc\hosts" | Where-Object { $_ -match "internal.assistant.leacare.ai" }
if ($hostsContent) {
    Write-Host "   WARNING: FOUND entries in hosts file:" -ForegroundColor Red
    Write-Host "   $hostsContent" -ForegroundColor Red
} else {
    Write-Host "   OK: No entries found in hosts file" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps based on results above:" -ForegroundColor Yellow
Write-Host "- If DNS resolves to WRONG IP -> Check antivirus/firewall" -ForegroundColor White
Write-Host "- If proxy is set -> Disable proxy temporarily" -ForegroundColor White
Write-Host "- If hosts file has entry -> Remove it" -ForegroundColor White
Write-Host ""
