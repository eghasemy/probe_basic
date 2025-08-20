#!/bin/bash
# SMB/CIFS Mount Helper Script
# Phase 9 - Settings, Profiles & Network
#
# Usage: mount_smb.sh <server> <share> <mount_point> [username] [password]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.pb-touch/logs/mount_smb.log"

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

# Check dependencies
check_dependencies() {
    if ! command -v mount.cifs >/dev/null 2>&1; then
        log "ERROR: cifs-utils not installed. Install with: sudo apt-get install cifs-utils"
        exit 1
    fi
}

# Parse arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <server> <share> <mount_point> [username] [password]"
    echo "Example: $0 192.168.1.100 shared_folder /home/user/mnt/network username password"
    exit 1
fi

SERVER="$1"
SHARE="$2"
MOUNT_POINT="$3"
USERNAME="${4:-}"
PASSWORD="${5:-}"

log "SMB mount request: //$SERVER/$SHARE -> $MOUNT_POINT"

# Validate inputs
if [ -z "$SERVER" ] || [ -z "$SHARE" ] || [ -z "$MOUNT_POINT" ]; then
    log "ERROR: Server, share, and mount point are required"
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

# Build mount options
MOUNT_OPTIONS="rw,nosuid,nodev,iocharset=utf8,file_mode=0664,dir_mode=0775"

# Add user/group options
MOUNT_OPTIONS="$MOUNT_OPTIONS,uid=$(id -u),gid=$(id -g)"

# Handle authentication
if [ -n "$USERNAME" ]; then
    MOUNT_OPTIONS="$MOUNT_OPTIONS,username=$USERNAME"
    if [ -n "$PASSWORD" ]; then
        # Create temporary credentials file for security
        CREDS_FILE=$(mktemp)
        echo "username=$USERNAME" > "$CREDS_FILE"
        echo "password=$PASSWORD" >> "$CREDS_FILE"
        chmod 600 "$CREDS_FILE"
        MOUNT_OPTIONS="$MOUNT_OPTIONS,credentials=$CREDS_FILE"
        
        # Cleanup function
        cleanup() {
            rm -f "$CREDS_FILE"
        }
        trap cleanup EXIT
    else
        # Username provided but no password - prompt for it
        MOUNT_OPTIONS="$MOUNT_OPTIONS,password="
    fi
else
    # No username - use guest access
    MOUNT_OPTIONS="$MOUNT_OPTIONS,guest"
fi

# Attempt mount
log "Mounting //$SERVER/$SHARE to $MOUNT_POINT with options: $(echo $MOUNT_OPTIONS | sed 's/password=[^,]*/password=***/g')"

if sudo mount -t cifs "//$SERVER/$SHARE" "$MOUNT_POINT" -o "$MOUNT_OPTIONS"; then
    log "SUCCESS: Mounted //$SERVER/$SHARE to $MOUNT_POINT"
    
    # Verify mount
    if mountpoint -q "$MOUNT_POINT"; then
        log "Mount verification successful"
        
        # Try to list directory to ensure it's working
        if ls "$MOUNT_POINT" >/dev/null 2>&1; then
            log "Directory listing successful"
        else
            log "WARNING: Mount successful but directory listing failed"
        fi
    else
        log "ERROR: Mount verification failed"
        exit 1
    fi
else
    log "ERROR: Failed to mount //$SERVER/$SHARE"
    exit 1
fi

log "SMB mount completed successfully"