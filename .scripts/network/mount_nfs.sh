#!/bin/bash
# NFS Mount Helper Script
# Phase 9 - Settings, Profiles & Network
#
# Usage: mount_nfs.sh <server> <export_path> <mount_point>

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.pb-touch/logs/mount_nfs.log"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# Check dependencies
check_dependencies() {
    if ! command -v mount.nfs >/dev/null 2>&1; then
        log "ERROR: nfs-common not installed. Install with: sudo apt-get install nfs-common"
        exit 1
    fi
}

# Parse arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <server> <export_path> <mount_point>"
    echo "Example: $0 192.168.1.100 /exports/shared /home/user/mnt/nfs"
    exit 1
fi

SERVER="$1"
EXPORT_PATH="$2"
MOUNT_POINT="$3"

log "NFS mount request: $SERVER:$EXPORT_PATH -> $MOUNT_POINT"

# Validate inputs
if [ -z "$SERVER" ] || [ -z "$EXPORT_PATH" ] || [ -z "$MOUNT_POINT" ]; then
    log "ERROR: Server, export path, and mount point are required"
    exit 1
fi

# Check dependencies
check_dependencies

# Create mount point if it doesn't exist
if [ ! -d "$MOUNT_POINT" ]; then
    log "Creating mount point: $MOUNT_POINT"
    mkdir -p "$MOUNT_POINT" || {
        log "ERROR: Failed to create mount point: $MOUNT_POINT"
        exit 1
    }
fi

# Check if already mounted
if mountpoint -q "$MOUNT_POINT"; then
    log "WARNING: $MOUNT_POINT is already mounted"
    exit 0
fi

# Build mount options for NFS
MOUNT_OPTIONS="rw,nosuid,nodev,soft,intr,timeo=10,retrans=3"

# Add version and protocol options
MOUNT_OPTIONS="$MOUNT_OPTIONS,vers=3,proto=tcp"

# Test NFS server connectivity
log "Testing NFS server connectivity..."
if ! timeout 10 rpcinfo -t "$SERVER" nfs >/dev/null 2>&1; then
    log "WARNING: NFS server may not be responding, attempting mount anyway..."
fi

# Attempt mount
log "Mounting $SERVER:$EXPORT_PATH to $MOUNT_POINT with options: $MOUNT_OPTIONS"

if sudo mount -t nfs "$SERVER:$EXPORT_PATH" "$MOUNT_POINT" -o "$MOUNT_OPTIONS"; then
    log "SUCCESS: Mounted $SERVER:$EXPORT_PATH to $MOUNT_POINT"
    
    # Verify mount
    if mountpoint -q "$MOUNT_POINT"; then
        log "Mount verification successful"
        
        # Try to list directory to ensure it's working
        if timeout 5 ls "$MOUNT_POINT" >/dev/null 2>&1; then
            log "Directory listing successful"
        else
            log "WARNING: Mount successful but directory listing failed"
        fi
    else
        log "ERROR: Mount verification failed"
        exit 1
    fi
else
    log "ERROR: Failed to mount $SERVER:$EXPORT_PATH"
    exit 1
fi

log "NFS mount completed successfully"