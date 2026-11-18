"""
Direct Hardware CRTC Gamma LUT and Display Config Engine for GNOME / Wayland
"""

import subprocess
import gi

gi.require_version('Gio', '2.0')
from gi.repository import Gio, GLib

from .presets import generate_lut


class DisplayEngine:
    """
    Communicates with org.gnome.Mutter.DisplayConfig via D-Bus
    to control hardware color lookup tables (LUT) directly with sub-20ms latency.
    """

    def __init__(self):
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.proxy = Gio.DBusProxy.new_sync(
            self.bus,
            Gio.DBusProxyFlags.NONE,
            None,
            'org.gnome.Mutter.DisplayConfig',
            '/org/gnome/Mutter/DisplayConfig',
            'org.gnome.Mutter.DisplayConfig',
            None
        )
        self.monitor_info = self._detect_monitor()
        self.display_state = self._detect_display_state()
        self.gpu_info = self._detect_gpu()

    def _detect_monitor(self):
        """Extract vendor, product, and connector dynamically from Mutter."""
        try:
            res = self.proxy.call_sync('GetResources', None, Gio.DBusCallFlags.NONE, -1, None)
            outputs = res[2]
            for out in outputs:
                if len(out) >= 8:
                    props = out[7]
                    vendor = props.get('vendor', '')
                    product = props.get('product', '')
                    name = out[4] if len(out) > 4 else ''
                    if vendor or product:
                        v_str = vendor.get_string() if hasattr(vendor, 'get_string') else str(vendor)
                        p_str = product.get_string() if hasattr(product, 'get_string') else str(product)
                        return f"{v_str} {p_str} ({name})"
            return "Primary Display"
        except Exception as e:
            return f"Display ({e})"

    def _detect_display_state(self):
        """Extract detailed current mode, resolution, refresh rate, and product info."""
        info = {
            'monitor': self.monitor_info,
            'display_name': 'Unknown Display',
            'resolution': '1920 × 1080',
            'refresh_rate': '60.00 Hz',
            'connector': 'HDMI-1',
            'serial': 'N/A'
        }
        try:
            state = self.proxy.call_sync('GetCurrentState', None, Gio.DBusCallFlags.NONE, -1, None)
            monitors = state[1]
            for mon in monitors:
                ident, modes, mon_props = mon[0], mon[1], mon[2]
                connector, vendor, product, mon_serial = ident[0], ident[1], ident[2], ident[3]
                disp_name = mon_props.get('display-name', '')

                for m in modes:
                    mode_id, w, h, refresh, scale, sup_scales, mode_props = m[0], m[1], m[2], m[3], m[4], m[5], m[6]
                    if mode_props.get('is-current', False):
                        info['resolution'] = f"{w} × {h}"
                        info['refresh_rate'] = f"{refresh:.2f} Hz"
                        break

                info['connector'] = connector
                info['serial'] = str(mon_serial)
                if disp_name:
                    info['display_name'] = str(disp_name)
                else:
                    info['display_name'] = f"{vendor} {product}"
                break
        except Exception:
            pass
        return info

    def _detect_gpu(self):
        """Detect GPU name and active graphics driver."""
        try:
            out = subprocess.check_output(
                ['nvidia-smi', '--query-gpu=name,driver_version', '--format=csv,noheader'],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if out:
                parts = [p.strip() for p in out.split(',')]
                return f"{parts[0]} (Driver: {parts[1]})"
        except Exception:
            pass

        try:
            out = subprocess.check_output(
                'lspci | grep -E "VGA|3D|Display"',
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            if out:
                lines = out.split('\n')
                first = lines[0].split(':')[-1].strip()
                return first
        except Exception:
            pass

        return "Universal Linux GPU"

    def disable_gnome_nightlight_conflict(self):
        """Turn off GNOME Night Light to prevent it from resetting hardware gamma."""
        try:
            settings = Gio.Settings(schema='org.gnome.settings-daemon.plugins.color')
            if settings.get_boolean('night-light-enabled'):
                settings.set_boolean('night-light-enabled', False)
        except Exception:
            pass

    def apply_lut(self, brightness=1.0, contrast=1.0, gamma=1.0, kelvin=6500, r_gain=1.0, g_gain=1.0, b_gain=1.0):
        """
        Calculates and applies 1024-step 16-bit gamma lookup tables to all active CRTCs.
        Returns the number of CRTCs calibrated.
        """
        self.disable_gnome_nightlight_conflict()
        res = self.proxy.call_sync('GetResources', None, Gio.DBusCallFlags.NONE, -1, None)
        serial = res[0]
        crtcs = res[1]

        red_lut, green_lut, blue_lut = generate_lut(
            brightness=brightness,
            contrast=contrast,
            gamma=gamma,
            kelvin=kelvin,
            r_gain=r_gain,
            g_gain=g_gain,
            b_gain=b_gain,
            lut_size=1024
        )

        applied = 0
        for crtc in crtcs:
            crtc_idx = crtc[0]
            width = crtc[4]
            height = crtc[5]
            mode = crtc[6]
            if mode != -1 and width > 0 and height > 0:
                var = GLib.Variant('(uuaqaqaq)', (serial, crtc_idx, red_lut, green_lut, blue_lut))
                self.proxy.call_sync('SetCrtcGamma', var, Gio.DBusCallFlags.NONE, -1, None)
                applied += 1
        return applied
