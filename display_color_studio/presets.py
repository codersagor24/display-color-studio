"""
Color profiles, calibration mathematics, and preset configurations.
"""

import os
import json
import math
import sys

CONFIG_DIR = os.path.expanduser('~/.config/display-color-studio')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

BUILTIN_PRESETS = {
    'studio': {
        'id': 'studio',
        'name': 'Studio Reference (D65)',
        'category': 'work',
        'tag': '100% Accurate',
        'desc_en': 'International designer & photo/video standard (Accurate 6500K sRGB/Rec.709)',
        'desc_bn': 'আন্তর্জাতিক ডিজাইনার ও ফটো/ভিডিও স্ট্যান্ডার্ড (নির্ভুল 6500K sRGB/Rec.709)',
        'kelvin': 6500,
        'brightness': 1.0,
        'contrast': 1.0,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#ffffff'
    },
    'd50': {
        'id': 'd50',
        'name': 'D50 Proofing (ISO 3664)',
        'category': 'work',
        'tag': 'Print Proofing',
        'desc_en': 'Graphic arts & ICC printing standard white point (5000K daylight simulator)',
        'desc_bn': 'গ্রাফিক আর্টস ও প্রিন্ট প্রুফিং স্ট্যান্ডার্ড (৫০০০K ডে-লাইট সিমুলেটর)',
        'kelvin': 5000,
        'brightness': 0.92,
        'contrast': 1.0,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 0.98,
        'b_gain': 0.95,
        'color_dot': '#fefae0'
    },
    'daylight': {
        'id': 'daylight',
        'name': 'Balanced Daylight',
        'category': 'work',
        'tag': 'Work & Office',
        'desc_en': 'Natural daylight tone, reduces strain during office & productivity tasks (5800K, 90%)',
        'desc_bn': 'স্বাভাবিক দিনের আলো, চোখে চাপমুক্ত অফিস ও কাজের জন্য (5800K, 90% ব্রাইটনেস)',
        'kelvin': 5800,
        'brightness': 0.90,
        'contrast': 1.0,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#fdf0d5'
    },
    'reading': {
        'id': 'reading',
        'name': 'Paper & Reading',
        'category': 'work',
        'tag': 'Eye Comfort',
        'desc_en': 'Soft warm paper tone for long reading & coding sessions (5000K, 82%)',
        'desc_bn': 'সফট পেপার টোন, দীর্ঘক্ষণ কোডিং ও টেক্সট পড়ার জন্য সেরা (5000K, 82% ব্রাইটনেস)',
        'kelvin': 5000,
        'brightness': 0.82,
        'contrast': 0.98,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#ffe3a8'
    },
    'coding': {
        'id': 'coding',
        'name': 'Late Night Coding',
        'category': 'work',
        'tag': 'Focus Mode',
        'desc_en': 'Optimized for dark IDEs with subdued blue light for marathon coding (4200K, 78%)',
        'desc_bn': 'ডার্ক আইডিই ও দীর্ঘ রাতের কোডিং সেশনের জন্য চোখের আরামদায়ক ফোকাস মোড (4200K, 78%)',
        'kelvin': 4200,
        'brightness': 0.78,
        'contrast': 1.02,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#fcd34d'
    },
    'cinema': {
        'id': 'cinema',
        'name': 'Cinema & Movie',
        'category': 'media',
        'tag': 'Entertainment',
        'desc_en': 'Rich cinematic contrast & deep shadows for movies & shows (4500K, 96%, +6% Contrast)',
        'desc_bn': 'সিনেমা ও ভিডিওর জন্য রিচ কনট্রাস্ট ও ডিপ ব্ল্যাক (4500K, 96% ব্রাইটনেস, 1.06 কনট্রাস্ট)',
        'kelvin': 4500,
        'brightness': 0.96,
        'contrast': 1.06,
        'gamma': 1.05,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#ffd28a'
    },
    'gaming': {
        'id': 'gaming',
        'name': 'Gaming & Vivid',
        'category': 'media',
        'tag': 'High Clarity',
        'desc_en': 'Enhanced contrast, shadow boost & vibrant colors for high-framerate gaming (6200K, 100%)',
        'desc_bn': 'উচ্চ কনট্রাস্ট, শ্যাডো ডিটেইল বুস্ট ও ভাইব্রেন্ট গেমিং কালার (6200K, 100% ব্রাইটনেস)',
        'kelvin': 6200,
        'brightness': 1.0,
        'contrast': 1.10,
        'gamma': 0.95,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#93c5fd'
    },
    'oled': {
        'id': 'oled',
        'name': 'OLED Deep Contrast',
        'category': 'media',
        'tag': 'Deep Inky Black',
        'desc_en': 'Deep blacks with punchy highlights and high micro-contrast (6500K, 1.15 Contrast)',
        'desc_bn': 'গভীর কালো ও উজ্জ্বল হাইলাইট সমৃদ্ধ হাই-কনট্রাস্ট মোড (6500K, 1.15 কনট্রাস্ট)',
        'kelvin': 6500,
        'brightness': 1.0,
        'contrast': 1.15,
        'gamma': 0.90,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#a5b4fc'
    },
    'evening': {
        'id': 'evening',
        'name': 'Warm Evening',
        'category': 'night',
        'tag': 'Relaxing Care',
        'desc_en': 'Gentle warm amber tone matching indoor evening ambient light (3800K, 72%)',
        'desc_bn': 'সন্ধ্যা ও হালকা ইনডোর বাতির আলোর জন্য মৃদু অ্যাম্বার উষ্ণতা (3800K, 72% ব্রাইটনেস)',
        'kelvin': 3800,
        'brightness': 0.72,
        'contrast': 0.96,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#ffbe6f'
    },
    'bedtime': {
        'id': 'bedtime',
        'name': 'Deep Night (Melatonin)',
        'category': 'night',
        'tag': 'Zero Blue Light',
        'desc_en': 'Zero blue-light sleep preservation mode for dark rooms (2800K, 50%)',
        'desc_bn': 'সম্পূর্ণ অন্ধকার রুমের জন্য ব্লু-লাইট মুক্ত রিল্যাক্স স্লিপ মোড (2800K, 50% ব্রাইটনেস)',
        'kelvin': 2800,
        'brightness': 0.50,
        'contrast': 0.90,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 1.0,
        'b_gain': 1.0,
        'color_dot': '#ff9e3b'
    },
    'candle': {
        'id': 'candle',
        'name': 'Candlelight Ultra Warm',
        'category': 'night',
        'tag': 'Ultra Soft',
        'desc_en': 'Ultra-warm amber flame spectrum for pitch black environments (2200K, 40%)',
        'desc_bn': 'সম্পূর্ণ অন্ধকার ঘরের জন্য মোমবাতির শিখার মতো অতি-উষ্ণ অ্যাম্বার টোন (2200K, 40%)',
        'kelvin': 2200,
        'brightness': 0.40,
        'contrast': 0.88,
        'gamma': 1.0,
        'r_gain': 1.0,
        'g_gain': 0.92,
        'b_gain': 0.85,
        'color_dot': '#fb923c'
    }
}

DEFAULT_CONFIG = {
    'active_preset': 'studio',
    'kelvin': 6500,
    'brightness': 1.0,
    'contrast': 1.0,
    'gamma': 1.0,
    'r_gain': 1.0,
    'g_gain': 1.0,
    'b_gain': 1.0,
    'language': 'bn',  # 'bn' or 'en'
    'custom_presets': {}
}


def kelvin_to_rgb(temp):
    """
    Tanner Helland algorithm for Planckian locus blackbody temperature.
    Returns (r, g, b) normalized 0.0 to 255.0.
    """
    temp = temp / 100.0
    if temp <= 66:
        r = 255.0
        g = 99.4708025861 * math.log(temp) - 161.1195681661
    else:
        r = 329.698727446 * ((temp - 60) ** -0.1332047592)
        g = 288.1221695283 * ((temp - 60) ** -0.0755148492)
    
    if temp >= 66:
        b = 255.0
    elif temp <= 19:
        b = 0.0
    else:
        b = 138.5177312231 * math.log(temp - 10) - 305.0447927307
        
    return max(0.0, min(255.0, r)), max(0.0, min(255.0, g)), max(0.0, min(255.0, b))


def kelvin_to_hex(temp):
    """
    Returns hex color string (e.g. '#ffe3a8') for given Kelvin temperature.
    """
    r, g, b = kelvin_to_rgb(temp)
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def generate_lut(brightness=1.0, contrast=1.0, gamma=1.0, kelvin=6500, r_gain=1.0, g_gain=1.0, b_gain=1.0, lut_size=1024):
    """
    Generate 16-bit hardware CRTC gamma lookup tables for display driver.
    """
    ref_r, ref_g, ref_b = kelvin_to_rgb(6500)
    kr, kg, kb = kelvin_to_rgb(kelvin)
    
    nr = min(1.0, kr / ref_r) * r_gain
    ng = min(1.0, kg / ref_g) * g_gain
    nb = min(1.0, kb / ref_b) * b_gain

    red_lut, green_lut, blue_lut = [], [], []
    for i in range(lut_size):
        x = i / (lut_size - 1.0)
        # Apply Contrast centering around mid-gray 0.5
        xc = (x - 0.5) * contrast + 0.5
        xc = max(0.0, min(1.0, xc))
        # Apply Gamma curve
        xg = xc ** (1.0 / gamma) if (gamma != 1.0 and xc > 0.0) else xc
        
        # Apply individual channel gain & brightness scaling
        r_val = int(round(max(0.0, min(1.0, xg * nr * brightness)) * 65535))
        g_val = int(round(max(0.0, min(1.0, xg * ng * brightness)) * 65535))
        b_val = int(round(max(0.0, min(1.0, xg * nb * brightness)) * 65535))
        
        red_lut.append(r_val)
        green_lut.append(g_val)
        blue_lut.append(b_val)
        
    return red_lut, green_lut, blue_lut


def load_config():
    """Load configuration from disk with defaults fallback."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                config = dict(DEFAULT_CONFIG)
                config.update(data)
                if 'custom_presets' not in config:
                    config['custom_presets'] = {}
                return config
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config):
    """Save configuration atomically to disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    tmp_file = CONFIG_FILE + '.tmp'
    try:
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.replace(tmp_file, CONFIG_FILE)
    except Exception as e:
        print(f"Error saving config: {e}", file=sys.stderr)


def export_presets(file_path):
    """Export custom presets to a JSON file."""
    config = load_config()
    presets_data = config.get('custom_presets', {})
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(presets_data, f, indent=2, ensure_ascii=False)


def import_presets(file_path):
    """Import custom presets from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        imported = json.load(f)
    if isinstance(imported, dict):
        config = load_config()
        config['custom_presets'].update(imported)
        save_config(config)
        return len(imported)
    return 0
