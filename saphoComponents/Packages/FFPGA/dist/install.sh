#!/bin/bash
# Enhanced Fractal Visualizer Installer

echo "Installing Enhanced Fractal Visualizer..."

# Create application directory
APP_DIR="$HOME/Applications/Enhanced_Fractal_Visualizer"
mkdir -p "$APP_DIR"

# Copy files
cp -r dist/* "$APP_DIR/"

# Create desktop entry (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    DESKTOP_FILE="$HOME/.local/share/applications/enhanced_fractal_visualizer.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Enhanced Fractal Visualizer
Comment=Advanced fractal visualization tool with real-time rendering
Exec=$APP_DIR/Enhanced_Fractal_Visualizer
Icon=$APP_DIR/icon.ico
Terminal=false
Categories=Graphics;Science;
EOF
    chmod +x "$DESKTOP_FILE"
    echo "Desktop entry created"
fi

echo "Installation completed!"
echo "Application installed to: $APP_DIR"
