#!/bin/bash
# Network Share Unmount Helper Script
# Phase 9 - Settings, Profiles & Network
#
# Usage: unmount_share.sh <mount_point>

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.pb-touch/logs/unmount_share.log"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# Parse arguments
if [ $# -lt 1 ]; then
    echo "Usage: $0 <mount_point>"
    echo "Example: $0 /home/user/mnt/network"
    exit 1
fi

MOUNT_POINT="$1"

log "Unmount request: $MOUNT_POINT"

# Validate input
if [ -z "$MOUNT_POINT" ]; then
    log "ERROR: Mount point is required"
    exit 1
fi

# Check if mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    log "ERROR: Mount point does not exist: $MOUNT_POINT"
    exit 1
fi

# Check if actually mounted
if ! mountpoint -q "$MOUNT_POINT"; then
    log "WARNING: $MOUNT_POINT is not mounted"
    exit 0
fi

# Get mount information for logging
MOUNT_INFO=$(mount | grep "$MOUNT_POINT" || echo "Unknown")
log "Mount info: $MOUNT_INFO"

# Force unmount if needed
FORCE_UNMOUNT=false

# Try normal unmount first
log "Attempting normal unmount of $MOUNT_POINT"
if sudo umount "$MOUNT_POINT" 2>/dev/null; then
    log "SUCCESS: Normal unmount successful"
else
    log "Normal unmount failed, trying lazy unmount..."
    
    # Try lazy unmount
    if sudo umount -l "$MOUNT_POINT" 2>/dev/null; then
        log "SUCCESS: Lazy unmount successful"
    else
        log "Lazy unmount failed, trying force unmount..."
        
        # Try force unmount as last resort
        if sudo umount -f "$MOUNT_POINT" 2>/dev/null; then
            log "SUCCESS: Force unmount successful"
            FORCE_UNMOUNT=true
        else
            log "ERROR: All unmount attempts failed"
            
            # Show what's using the mount point
            log "Processes using mount point:"
            if command -v lsof >/dev/null 2>&1; then
                lsof +D "$MOUNT_POINT" 2>/dev/null | tee -a "$LOG_FILE" || true
            elif command -v fuser >/dev/null 2>&1; then
                fuser -vm "$MOUNT_POINT" 2>&1 | tee -a "$LOG_FILE" || true
            fi
            
            exit 1
        fi
    fi
fi

# Verify unmount
sleep 1
if mountpoint -q "$MOUNT_POINT"; then
    log "ERROR: Unmount verification failed - still mounted"
    exit 1
else
    log "Unmount verification successful"
fi

# Optional: Remove empty mount point directory
if [ -d "$MOUNT_POINT" ] && [ -z "$(ls -A "$MOUNT_POINT" 2>/dev/null)" ]; then
    log "Mount point is empty, considering removal"
    # Only remove if it's in a typical mount directory
    if [[ "$MOUNT_POINT" == *"/mnt/"* ]] || [[ "$MOUNT_POINT" == *"/.pb-touch/"* ]]; then
        log "Removing empty mount point: $MOUNT_POINT"
        rmdir "$MOUNT_POINT" 2>/dev/null || log "Could not remove mount point directory"
    fi
fi

if [ "$FORCE_UNMOUNT" = true ]; then
    log "Unmount completed (forced)"
else
    log "Unmount completed successfully"
fi