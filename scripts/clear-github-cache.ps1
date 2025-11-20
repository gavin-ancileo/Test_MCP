# Script to clear all GitHub Actions caches
# Repository: Ancileo-Lea/AAP-MCP

$owner = "Ancileo-Lea"
$repo = "AAP-MCP"
$gh = "C:\Program Files\GitHub CLI\gh.exe"

Write-Host "Fetching all caches..." -ForegroundColor Cyan

# Get all caches
$caches = & $gh cache list --repo "$owner/$repo" --limit 1000 --json id,key,sizeInBytes,createdAt | ConvertFrom-Json

if ($caches.Count -eq 0) {
    Write-Host "No caches found." -ForegroundColor Yellow
    exit 0
}

# Calculate total size
$totalSize = ($caches | Measure-Object -Property sizeInBytes -Sum).Sum
$totalSizeGB = [math]::Round($totalSize / 1GB, 2)

Write-Host "`nFound $($caches.Count) caches, total size: $totalSizeGB GB" -ForegroundColor Yellow
Write-Host ""

# Show top 10 largest caches
Write-Host "Top 10 largest caches:" -ForegroundColor Cyan
$caches | Sort-Object -Property sizeInBytes -Descending | Select-Object -First 10 | ForEach-Object {
    $sizeMB = [math]::Round($_.sizeInBytes / 1MB, 2)
    Write-Host "  - $($_.key) ($sizeMB MB) - Created: $($_.createdAt)"
}
Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Do you want to delete ALL $($caches.Count) caches? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nDeleting caches..." -ForegroundColor Red
$deleted = 0
$failed = 0

foreach ($cache in $caches) {
    try {
        & $gh cache delete $cache.id --repo "$owner/$repo" --confirm 2>&1 | Out-Null
        $deleted++
        if ($deleted % 10 -eq 0) {
            Write-Host "Deleted $deleted caches..." -ForegroundColor Green
        }
    }
    catch {
        $failed++
        Write-Host "Failed to delete cache $($cache.id): $_" -ForegroundColor Red
    }
}

Write-Host "`nDone!" -ForegroundColor Green
Write-Host "  Deleted: $deleted caches" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "  Failed: $failed caches" -ForegroundColor Red
}
Write-Host "  Freed space: approximately $totalSizeGB GB" -ForegroundColor Cyan
