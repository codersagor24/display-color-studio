#!/usr/bin/env bash
set -e

echo -e "\033[1;33mUninstalling Display & Color Studio...\033[0m"

rm -f "$HOME/.local/bin/display-color-studio"
rm -rf "$HOME/.local/share/display-color-studio"
rm -f "$HOME/.local/share/applications/com.antigravity.DisplayColorStudio.desktop"
rm -f "$HOME/.local/share/applications/display-color-studio.desktop"
rm -f "$HOME/Desktop/display-color-studio.desktop"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/com.antigravity.DisplayColorStudio.svg"
rm -f "$HOME/.local/share/icons/hicolor/scalable/apps/display-color-studio.svg"
rm -f "$HOME/.config/autostart/com.antigravity.DisplayColorStudio.autostart.desktop"

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo -e "\033[1;32m✓ Display & Color Studio has been uninstalled.\033[0m"
