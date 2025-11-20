#!/usr/bin/env pwsh
##
# Clear SSL/TLS Cache and DNS on Windows
# Fix certificate caching issues
##

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " CLEARING SSL CACHE & DNS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Clear DNS cache
Write-Host "1. Clearing DNS cache..." -ForegroundColor Yellow
ipconfig /flushdns
Write-Host "   ✓ DNS cache cleared" -ForegroundColor Green
Write-Host ""

# 2. Clear SSL/TLS state (Windows Internet Explorer/Edge cache)
Write-Host "2. Clearing SSL/TLS state..." -ForegroundColor Yellow
certutil -urlcache * delete 2>$null
Write-Host "   ✓ SSL certificate cache cleared" -ForegroundColor Green
Write-Host ""

# 3. Clear Chrome SSL cache (if Chrome is installed)
Write-Host "3. Instructions for clearing browser caches:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   CHROME:" -ForegroundColor Cyan
Write-Host "   - Go to: chrome://net-internals/#sockets"
Write-Host "   - Click: 'Close idle sockets'"
Write-Host "   - Click: 'Flush socket pools'"
Write-Host "   - Then go to: chrome://net-internals/#ssl"
Write-Host "   - Click: 'Clear SSL session cache'"
Write-Host ""
Write-Host "   EDGE:" -ForegroundColor Cyan
Write-Host "   - Go to: edge://net-internals/#sockets"
Write-Host "   - Click: 'Close idle sockets'"
Write-Host "   - Click: 'Flush socket pools'"
Write-Host "   - Then go to: edge://net-internals/#ssl"
Write-Host "   - Click: 'Clear SSL session cache'"
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ✅ SYSTEM CACHE CLEARED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close ALL browser windows"
Write-Host "2. Reopen browser in INCOGNITO mode"
Write-Host "3. Visit: https://internal.assistant.leacare.ai"
Write-Host ""
