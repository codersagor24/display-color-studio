#!/usr/bin/env bash
set -e

echo -e "\033[1;36m╭────────────────────────────────────────────────────────╮\033[0m"
echo -e "\033[1;36m│          Display & Color Studio Installer              │\033[0m"
echo -e "\033[1;36m╰────────────────────────────────────────────────────────╯\033[0m"

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
AUTOSTART_DIR="$HOME/.config/autostart"

mkdir -p "$BIN_DIR" "$APP_DESKTOP_DIR" "$ICON_DIR" "$AUTOSTART_DIR"

echo -e "\033[1;34m[1/5]\033[0m Installing binary launcher to $BIN_DIR/display-color-studio..."
cp "$APP_DIR/bin/display-color-studio" "$BIN_DIR/display-color-studio"
chmod +x "$BIN_DIR/display-color-studio"

# Also install python package files into ~/.local/share/display-color-studio or via pip
SHARED_LIB="$HOME/.local/share/display-color-studio"
mkdir -p "$SHARED_LIB"
cp -r "$APP_DIR/display_color_studio" "$SHARED_LIB/"

# Create wrapper script in ~/.local/bin if needed
cat << 'EOF' > "$BIN_DIR/display-color-studio"
#!/usr/bin/env python3
import sys
import os

app_lib = os.path.expanduser('~/.local/share/display-color-studio')
if os.path.exists(app_lib):
    sys.path.insert(0, app_lib)

from display_color_studio.cli import main

if __name__ == '__main__':
    main()
EOF
chmod +x "$BIN_DIR/display-color-studio"

echo -e "\033[1;34m[2/5]\033[0m Installing high-res application icon..."
cp "$APP_DIR/data/com.antigravity.DisplayColorStudio.svg" "$ICON_DIR/com.antigravity.DisplayColorStudio.svg"
cp "$APP_DIR/data/com.antigravity.DisplayColorStudio.svg" "$ICON_DIR/display-color-studio.svg"
gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo -e "\033[1;34m[3/5]\033[0m Installing desktop entries..."
cp "$APP_DIR/data/com.antigravity.DisplayColorStudio.desktop" "$APP_DESKTOP_DIR/com.antigravity.DisplayColorStudio.desktop"
cp "$APP_DIR/data/com.antigravity.DisplayColorStudio.desktop" "$APP_DESKTOP_DIR/display-color-studio.desktop"

if [ -d "$HOME/Desktop" ]; then
    cp "$APP_DIR/data/com.antigravity.DisplayColorStudio.desktop" "$HOME/Desktop/display-color-studio.desktop"
    chmod +x "$HOME/Desktop/display-color-studio.desktop"
    gio set "$HOME/Desktop/display-color-studio.desktop" metadata::trusted true 2>/dev/null || true
fi

echo -e "\033[1;34m[4/5]\033[0m Setting up login autostart..."
cp "$APP_DIR/data/com.antigravity.DisplayColorStudio.autostart.desktop" "$AUTOSTART_DIR/com.antigravity.DisplayColorStudio.autostart.desktop"

update-desktop-database "$APP_DESKTOP_DIR" 2>/dev/null || true

echo -e "\033[1;34m[5/5]\033[0m Applying saved calibration settings..."
"$BIN_DIR/display-color-studio" --apply-saved 2>/dev/null || true

echo -e "\n\033[1;32m✓ Installation completed successfully!\033[0m"
echo -e "You can now launch Display & Color Studio from:"
echo -e "  • Your Application Grid / Dock (search 'Display & Color Studio')"
echo -e "  • Terminal: \033[1mdisplay-color-studio\033[0m"
echo -e "  • Desktop Shortcut on ~/Desktop"
