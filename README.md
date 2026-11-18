# Display & Color Studio

**Display & Color Studio** is a modern display calibration, color temperature, and hardware LUT profile manager designed for Linux desktop environments running GNOME Wayland.

## Features

- **Direct Hardware CRTC Gamma LUT**: Sub-20ms instant color calibration without root permissions via Mutter D-Bus.
- **Dynamic Hardware Diagnostics**: Real-time detection of connected display models, resolutions, refresh rates (up to 180Hz+), GPU models, and drivers.
- **Curated Color Presets**:
  - `Studio Reference (D65)`: 6500K color-accurate sRGB/Rec.709 standard.
  - `D50 Proofing`: 5000K daylight print proofing standard.
  - `Balanced Daylight`: 5800K comfortable daytime office mode.
  - `Paper & Reading`: 5000K soft paper tone for long coding sessions.
  - `Late Night Coding`: 4200K dark-mode IDE eye-care profile.
  - `Cinema & Movie`: 4500K rich contrast movie profile.
  - `Gaming & Vivid`: 6200K high-clarity shadow-boost profile.
  - `Warm Evening`: 3800K ambient evening relaxation tone.
  - `Deep Night`: 2800K zero-blue-light melatonin preservation mode.
  - `Candlelight`: 2200K ultra-warm amber flame tone.
- **Hardware Calibration Controls**:
  - Precision brightness (luminance) slider & quick stepper buttons.
  - White point color temperature slider (2200K to 7500K).
  - Micro-contrast and gamma curve tuning.
  - Independent hardware Red, Green, and Blue channel gains.
- **Custom Presets**: Create, save, export, and import custom calibration profiles.
- **Bilingual Interface**: Quick one-click toggle between English and Bengali.
- **Autostart & Persistence**: Automatically restores your chosen calibration on system login.

## Quick Installation

Clone and install using the included installation script:

```bash
git clone https://github.com/codersagor24/display-color-studio.git
cd display-color-studio
chmod +x install.sh
./install.sh
```

## Usage

### Graphical Interface (GUI)

Launch from your application grid or dock by searching for **Display & Color Studio**, or run:

```bash
display-color-studio
```

### Command Line Interface (CLI)

```bash
# View active display status and hardware info
display-color-studio --status

# List available presets
display-color-studio --list-presets

# Apply a preset directly
display-color-studio --preset studio
display-color-studio --preset reading
display-color-studio --preset gaming

# Set custom brightness and color temperature
display-color-studio --brightness 85 --kelvin 5800

# Reset display to Studio Reference D65 (6500K)
display-color-studio --reset
```

## Keyboard Shortcuts

- `Ctrl + S`: Save current settings as startup default
- `Ctrl + R`: Reset display to Studio D65
- `Ctrl + 1 / 2 / 3`: Switch between Presets, Fine Tuning, and Hardware Info
- `Ctrl + Q`: Quit application

## Uninstallation

To remove the application and its desktop shortcuts:

```bash
cd display-color-studio
./uninstall.sh
```

## License

This project is licensed under the MIT License.
