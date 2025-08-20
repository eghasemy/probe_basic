#!/bin/bash
# AppImage build script for Probe Basic
# Phase 10 - Packaging

set -e

echo "Building Probe Basic AppImage..."

# Configuration
APP_NAME="ProbeBasic"
APP_DIR="${APP_NAME}.AppDir"
PYTHON_VERSION="3.9"
BUILD_DIR="$(pwd)/appimage_build"

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Clean previous build
rm -rf "$APP_DIR"
rm -f "${APP_NAME}*.AppImage"

echo "Creating AppDir structure..."

# Create AppDir structure
mkdir -p "$APP_DIR"/{usr/{bin,lib,share/{applications,icons/hicolor/256x256/apps}},etc}

# Create desktop file
cat > "$APP_DIR/usr/share/applications/${APP_NAME}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Probe Basic
Comment=QtPyVCP-based CNC interface for LinuxCNC
Exec=probe_basic
Icon=probe_basic
Categories=Engineering;Science;
Keywords=CNC;LinuxCNC;Machining;Manufacturing;
StartupNotify=true
EOF

# Create AppRun script
cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash

# AppRun script for Probe Basic
HERE="$(dirname "$(readlink -f "${0}")")"

# Set up environment
export APPDIR="$HERE"
export PYTHONPATH="$HERE/usr/lib/python3/site-packages:$PYTHONPATH"
export LD_LIBRARY_PATH="$HERE/usr/lib:$LD_LIBRARY_PATH"
export PATH="$HERE/usr/bin:$PATH"
export XDG_DATA_DIRS="$HERE/usr/share:$XDG_DATA_DIRS"

# LinuxCNC environment
export LINUXCNC_HOME="${LINUXCNC_HOME:-/usr}"
export EMC2_HOME="$LINUXCNC_HOME"

# Qt environment
export QT_PLUGIN_PATH="$HERE/usr/lib/qt5/plugins:$QT_PLUGIN_PATH"
export QML2_IMPORT_PATH="$HERE/usr/lib/qt5/qml:$QML2_IMPORT_PATH"

# Start Probe Basic
cd "$HERE/usr/lib/python3/site-packages"
exec "$HERE/usr/bin/python3" -m probe_basic "$@"
EOF

chmod +x "$APP_DIR/AppRun"

# Copy application files
echo "Copying application files..."
cp -r "../src/"* "$APP_DIR/usr/lib/python3/site-packages/"

# Create launcher script
cat > "$APP_DIR/usr/bin/probe_basic" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
cd "$HERE/../lib/python3/site-packages"
exec python3 -m probe_basic "$@"
EOF

chmod +x "$APP_DIR/usr/bin/probe_basic"

# Create minimal Python environment
echo "Setting up Python environment..."

# Download Python if needed
if [ ! -f "python3" ]; then
    echo "Downloading portable Python..."
    # Use system Python for now - in production, use portable Python
    cp /usr/bin/python3 "$APP_DIR/usr/bin/"
fi

# Install required Python packages
echo "Installing Python dependencies..."
pip3 install --target "$APP_DIR/usr/lib/python3/site-packages" \
    PyQt5 \
    numpy \
    || echo "Warning: Some packages may not install in AppImage environment"

# Create basic icon (placeholder)
if command -v convert >/dev/null 2>&1; then
    convert -size 256x256 xc:blue -pointsize 72 -fill white -gravity center \
        -annotate +0+0 "PB" "$APP_DIR/usr/share/icons/hicolor/256x256/apps/probe_basic.png"
else
    # Create simple colored square as fallback
    echo "Creating placeholder icon..."
    cat > "$APP_DIR/usr/share/icons/hicolor/256x256/apps/probe_basic.png" << 'EOF'
# This is a placeholder - replace with actual icon
EOF
fi

# Copy icon to root for AppImage
cp "$APP_DIR/usr/share/icons/hicolor/256x256/apps/probe_basic.png" "$APP_DIR/"

# Copy desktop file to root
cp "$APP_DIR/usr/share/applications/${APP_NAME}.desktop" "$APP_DIR/"

# Create version info
cat > "$APP_DIR/usr/share/probe_basic_version.txt" << EOF
Probe Basic AppImage
Built: $(date)
Version: $(git describe --tags --always 2>/dev/null || echo "development")
Python: $PYTHON_VERSION
Host: $(uname -a)
EOF

echo "Preparing AppImage build..."

# Download appimagetool if not available
if [ ! -f "appimagetool" ]; then
    echo "Downloading appimagetool..."
    wget -q "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
        -O appimagetool
    chmod +x appimagetool
fi

# Build AppImage
echo "Building AppImage..."
if [ -f "appimagetool" ]; then
    ARCH=x86_64 ./appimagetool "$APP_DIR" "${APP_NAME}-x86_64.AppImage"
    
    if [ -f "${APP_NAME}-x86_64.AppImage" ]; then
        echo "✅ AppImage built successfully: ${APP_NAME}-x86_64.AppImage"
        
        # Test the AppImage
        echo "Testing AppImage..."
        if timeout 10 ./"${APP_NAME}-x86_64.AppImage" --version 2>/dev/null; then
            echo "✅ AppImage test passed"
        else
            echo "⚠️ AppImage test failed or timed out"
        fi
        
        # Show file info
        ls -lh "${APP_NAME}-x86_64.AppImage"
        
        # Move to parent directory
        mv "${APP_NAME}-x86_64.AppImage" ..
        echo "AppImage moved to: $(pwd)/../${APP_NAME}-x86_64.AppImage"
    else
        echo "❌ AppImage build failed"
        exit 1
    fi
else
    echo "❌ Could not download appimagetool"
    exit 1
fi

echo "AppImage build complete!"

# Cleanup
cd ..
if [ "$1" != "--keep-build" ]; then
    rm -rf "$BUILD_DIR"
    echo "Build directory cleaned up"
fi