"""
Command-line interface (CLI) with rich formatting for Display & Color Studio.
"""

import sys
import json
import argparse

from .presets import BUILTIN_PRESETS, load_config, save_config
from .engine import DisplayEngine


def print_colored(text, color_code):
    """Print with ANSI color if stdout is a TTY."""
    if sys.stdout.isatty():
        print(f"\033[{color_code}m{text}\033[0m")
    else:
        print(text)


def format_table_row(key, val):
    return f"  \033[1;34m{key:<26}\033[0m : \033[1;37m{val}\033[0m"


def print_status(engine, config):
    print_colored("\n╭────────────────────────────────────────────────────────╮", "1;36")
    print_colored("│             Display & Color Studio Status              │", "1;36")
    print_colored("╰────────────────────────────────────────────────────────╯", "1;36")
    
    st = engine.display_state
    print(format_table_row("Active Monitor", st.get('display_name', engine.monitor_info)))
    print(format_table_row("Connector & Serial", f"{st.get('connector')} (SN: {st.get('serial')})"))
    print(format_table_row("Current Mode", f"{st.get('resolution')} @ {st.get('refresh_rate')}"))
    print(format_table_row("Graphics Processor (GPU)", engine.gpu_info))
    print(format_table_row("Compositor Engine", "GNOME Mutter Wayland Direct Hardware LUT"))
    print("  " + "─" * 52)
    
    act_id = config.get('active_preset', 'custom')
    pdata = BUILTIN_PRESETS.get(act_id) or config.get('custom_presets', {}).get(act_id, {})
    pname = pdata.get('name', 'Custom Tuning')
    
    print(format_table_row("Active Preset", f"{pname} ({act_id})"))
    print(format_table_row("Color Temperature", f"{config.get('kelvin', 6500)}K"))
    print(format_table_row("Display Brightness", f"{int(config.get('brightness', 1.0) * 100)}%"))
    print(format_table_row("Hardware Contrast", f"{int(config.get('contrast', 1.0) * 100)}%"))
    print(format_table_row("Gamma Factor", f"{config.get('gamma', 1.0):.2f}"))
    print(format_table_row("RGB Channel Gains", f"R: {int(config.get('r_gain', 1.0)*100)}%, G: {int(config.get('g_gain', 1.0)*100)}%, B: {int(config.get('b_gain', 1.0)*100)}%"))
    print()


def print_presets_list():
    print_colored("\n╭────────────────────────────────────────────────────────╮", "1;35")
    print_colored("│               Available Display Presets                │", "1;35")
    print_colored("╰────────────────────────────────────────────────────────╯", "1;35")
    for pid, p in BUILTIN_PRESETS.items():
        print(f"  \033[1;32m{pid:<12}\033[0m : \033[1;37m{p['name']:<24}\033[0m ({p['kelvin']}K, {int(p['brightness']*100)}% Lum)")
        print(f"               \033[0;37m{p['desc_en']}\033[0m")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Display & Color Studio: Professional Display Calibration & Color Profiles for Wayland"
    )
    parser.add_argument('--preset', help="Apply a predefined or custom color preset")
    parser.add_argument('--brightness', type=float, help="Set brightness percentage (20 to 100)")
    parser.add_argument('--kelvin', type=int, help="Set color temperature in Kelvin (2200 to 7500)")
    parser.add_argument('--contrast', type=float, help="Set contrast percentage (70 to 130)")
    parser.add_argument('--gamma', type=float, help="Set gamma factor (0.7 to 1.4)")
    parser.add_argument('--apply-saved', action='store_true', help="Apply previously saved configuration silently")
    parser.add_argument('--reset', action='store_true', help="Reset display to Studio Reference D65 (100%% neutral 6500K)")
    parser.add_argument('--status', action='store_true', help="Print display status and current configuration")
    parser.add_argument('--list-presets', action='store_true', help="List all built-in color presets")
    parser.add_argument('--gui', action='store_true', help="Launch the graphical interface")

    args = parser.parse_args()
    engine = DisplayEngine()
    config = load_config()

    if args.list_presets:
        print_presets_list()
        sys.exit(0)

    if args.status:
        print_status(engine, config)
        sys.exit(0)

    if args.reset:
        p = BUILTIN_PRESETS['studio']
        engine.apply_lut(
            brightness=p['brightness'],
            contrast=p['contrast'],
            gamma=p['gamma'],
            kelvin=p['kelvin'],
            r_gain=p['r_gain'],
            g_gain=p['g_gain'],
            b_gain=p['b_gain']
        )
        config.update(p)
        config['active_preset'] = 'studio'
        save_config(config)
        print_colored("✓ Display successfully reset to Studio Reference D65 (6500K).", "1;32")
        sys.exit(0)

    if args.apply_saved:
        engine.apply_lut(
            brightness=config.get('brightness', 1.0),
            contrast=config.get('contrast', 1.0),
            gamma=config.get('gamma', 1.0),
            kelvin=config.get('kelvin', 6500),
            r_gain=config.get('r_gain', 1.0),
            g_gain=config.get('g_gain', 1.0),
            b_gain=config.get('b_gain', 1.0)
        )
        sys.exit(0)

    if args.preset:
        p = None
        if args.preset in BUILTIN_PRESETS:
            p = BUILTIN_PRESETS[args.preset]
        elif args.preset in config.get('custom_presets', {}):
            p = config['custom_presets'][args.preset]
            
        if p:
            engine.apply_lut(
                brightness=p['brightness'],
                contrast=p.get('contrast', 1.0),
                gamma=p.get('gamma', 1.0),
                kelvin=p['kelvin'],
                r_gain=p.get('r_gain', 1.0),
                g_gain=p.get('g_gain', 1.0),
                b_gain=p.get('b_gain', 1.0)
            )
            config.update(p)
            config['active_preset'] = args.preset
            save_config(config)
            print_colored(f"✓ Preset '{p['name']}' ({p['kelvin']}K, {int(p['brightness']*100)}%) active.", "1;32")
        else:
            print_colored(f"✗ Error: Preset '{args.preset}' not found.", "1;31")
            print("Use --list-presets to view available presets.")
        sys.exit(0)

    has_cli_tuning = any(v is not None for v in [args.brightness, args.kelvin, args.contrast, args.gamma])
    if has_cli_tuning and not args.gui:
        if args.brightness is not None:
            config['brightness'] = max(0.2, min(1.0, args.brightness / 100.0))
        if args.kelvin is not None:
            config['kelvin'] = max(2200, min(7500, args.kelvin))
        if args.contrast is not None:
            config['contrast'] = max(0.7, min(1.3, args.contrast / 100.0))
        if args.gamma is not None:
            config['gamma'] = max(0.7, min(1.4, args.gamma))
        config['active_preset'] = 'custom'
        engine.apply_lut(
            brightness=config['brightness'],
            contrast=config['contrast'],
            gamma=config['gamma'],
            kelvin=config['kelvin'],
            r_gain=config.get('r_gain', 1.0),
            g_gain=config.get('g_gain', 1.0),
            b_gain=config.get('b_gain', 1.0)
        )
        save_config(config)
        print_colored(f"✓ Custom calibration applied: {config['kelvin']}K, {int(config['brightness']*100)}% Brightness, {int(config['contrast']*100)}% Contrast.", "1;32")
        sys.exit(0)

    # Launch GUI
    from .window import StudioApp
    app = StudioApp(engine, config)
    app.run([sys.argv[0]])
