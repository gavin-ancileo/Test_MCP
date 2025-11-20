#!/bin/bash
# Script to clear all GitHub Actions caches
# Repository: Ancileo-Lea/AAP-MCP

owner="Ancileo-Lea"
repo="AAP-MCP"

echo -e "\033[36mFetching all caches...\033[0m"

# Get all caches
caches_json=$(gh cache list --repo "$owner/$repo" --limit 1000 --json id,key,sizeInBytes,createdAt)

# Check if we have caches
cache_count=$(echo "$caches_json" | jq '. | length')

if [ "$cache_count" -eq 0 ]; then
    echo -e "\033[33mNo caches found.\033[0m"
    exit 0
fi

# Calculate total size
total_size=$(echo "$caches_json" | jq '[.[].sizeInBytes] | add')
total_size_gb=$(echo "scale=2; $total_size / 1073741824" | bc)

echo ""
echo -e "\033[33mFound $cache_count caches, total size: ${total_size_gb} GB\033[0m"
echo ""

# Show top 10 largest caches
echo -e "\033[36mTop 10 largest caches:\033[0m"
echo "$caches_json" | jq -r 'sort_by(-.sizeInBytes) | .[:10] | .[] | "  - \(.key) (\(.sizeInBytes / 1048576 | floor) MB) - Created: \(.createdAt)"'
echo ""

# Ask for confirmation
read -p "Do you want to delete ALL $cache_count caches? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "\033[33mCancelled.\033[0m"
    exit 0
fi

echo ""
echo -e "\033[31mDeleting caches...\033[0m"
deleted=0
failed=0

# Delete all caches
echo "$caches_json" | jq -r '.[].id' | while read cache_id; do
    if gh cache delete "$cache_id" --repo "$owner/$repo" --confirm &>/dev/null; then
        deleted=$((deleted + 1))
        if [ $((deleted % 10)) -eq 0 ]; then
            echo -e "\033[32mDeleted $deleted caches...\033[0m"
        fi
    else
        failed=$((failed + 1))
        echo -e "\033[31mFailed to delete cache $cache_id\033[0m"
    fi
done

echo ""
echo -e "\033[32m✓ Done!\033[0m"
echo -e "\033[32m  Deleted: $cache_count caches\033[0m"
if [ $failed -gt 0 ]; then
    echo -e "\033[31m  Failed: $failed caches\033[0m"
fi
echo -e "\033[36m  Freed space: ~${total_size_gb} GB\033[0m"
