"""
Main application window, UI components, and modern styling for Display & Color Studio.
"""

import sys
import os
import math
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, Gdk

from .presets import (
    BUILTIN_PRESETS,
    load_config,
    save_config,
    export_presets,
    import_presets,
    kelvin_to_hex,
    CONFIG_DIR
)

CUSTOM_CSS = """
/* Window & Base Colors */
window.background {
    background-color: #11111b;
}

/* Hero Status Banner */
.hero-card {
    background-color: #181825;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 12px 18px 4px 18px;
}

.hero-title {
    font-size: 17px;
    font-weight: 700;
    color: #cdd6f4;
}

.hero-subtitle {
    font-size: 12px;
    color: #a6adc8;
}

.metric-pill {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 600;
    color: #cdd6f4;
}

.status-active-pill {
    background-color: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.35);
    color: #4ade80;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 600;
}

/* Category Filter Bar */
.filter-bar {
    margin: 8px 18px 12px 18px;
}

.filter-btn {
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #a6adc8;
}

.filter-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #cdd6f4;
}

.filter-btn.active {
    background-color: #89b4fa;
    color: #11111b;
    border-color: #89b4fa;
}

/* Preset Cards */
.preset-card {
    background-color: #181825;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px 16px;
    transition: all 150ms ease-in-out;
}

.preset-card:hover {
    background-color: #1e1e2e;
    border-color: rgba(137, 180, 250, 0.35);
}

.preset-card.active-card {
    background-color: #1f233a;
    border: 2px solid #89b4fa;
    box-shadow: 0 0 12px rgba(137, 180, 250, 0.2);
}

.card-title {
    font-size: 15px;
    font-weight: 700;
    color: #cdd6f4;
}

.card-desc {
    font-size: 12px;
    color: #9399b2;
}

.card-tag {
    background-color: rgba(255, 255, 255, 0.06);
    color: #89b4fa;
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}

.check-pill {
    background-color: #89b4fa;
    color: #11111b;
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 700;
}

/* Controls Cards */
.control-card {
    background-color: #181825;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}

.control-title {
    font-size: 15px;
    font-weight: 700;
    color: #cdd6f4;
}

.control-subtitle {
    font-size: 12px;
    color: #9399b2;
}

.control-value {
    font-size: 16px;
    font-weight: 700;
    color: #89b4fa;
}

.stepper-btn {
    border-radius: 16px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}

.target-pill {
    border-radius: 14px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}

/* Hardware Info Cards */
.info-card {
    background-color: #181825;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}

.info-header {
    font-size: 15px;
    font-weight: 700;
    color: #cdd6f4;
    margin-bottom: 8px;
}

.info-label {
    font-size: 13px;
    color: #a6adc8;
}

.info-val {
    font-size: 13px;
    font-weight: 600;
    color: #89b4fa;
}
"""


class StudioWindow(Adw.ApplicationWindow):
    def __init__(self, app, engine, initial_config):
        super().__init__(application=app, title="Display & Color Studio")
        self.set_default_size(900, 760)
        self.engine = engine
        self.config = initial_config
        self.lang = self.config.get('language', 'bn')
        self.update_timeout_id = None
        self.preset_cards = {}
        self.current_category = 'all'
        self.search_query = ''

        self._setup_keybindings()
        self._build_ui()
        self._sync_all_from_config()

    def _setup_keybindings(self):
        controller = Gtk.EventControllerKey()
        controller.connect('key-pressed', self._on_key_pressed)
        self.add_controller(controller)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl:
            if keyval == Gdk.KEY_s or keyval == Gdk.KEY_S:
                self._on_save_clicked(None)
                return True
            elif keyval == Gdk.KEY_r or keyval == Gdk.KEY_R:
                self.select_preset('studio')
                return True
            elif keyval == Gdk.KEY_1:
                self.view_stack.set_visible_child_name('presets')
                return True
            elif keyval == Gdk.KEY_2:
                self.view_stack.set_visible_child_name('tuner')
                return True
            elif keyval == Gdk.KEY_3:
                self.view_stack.set_visible_child_name('info')
                return True
            elif keyval == Gdk.KEY_q or keyval == Gdk.KEY_Q:
                self.close()
                return True
        return False

    def _t(self, bn_text, en_text):
        """Localization helper."""
        return bn_text if self.lang == 'bn' else en_text

    def _build_ui(self):
        # 1. Header Bar with ViewSwitcher & Action Buttons
        header = Adw.HeaderBar()
        
        # Left Chip: Monitor & Refresh Rate
        mon_chip = Gtk.Label()
        refresh_str = self.engine.display_state.get('refresh_rate', '100Hz')
        mon_label = self.engine.display_state.get('display_name', self.engine.monitor_info)
        mon_chip.set_markup(f"<span foreground='#89b4fa' font_desc='11'><b>🖥️ {mon_label} • {refresh_str}</b></span>")
        mon_chip.set_css_classes(["metric-pill"])
        header.pack_start(mon_chip)

        # Center: ViewStack & ViewSwitcher
        self.view_stack = Adw.ViewStack()
        
        switcher = Adw.ViewSwitcher()
        switcher.set_stack(self.view_stack)
        switcher.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        header.set_title_widget(switcher)

        # Right Actions
        # Language Switcher
        self.lang_btn = Gtk.Button(label="BN" if self.lang == 'bn' else "EN")
        self.lang_btn.set_tooltip_text("Switch language / ভাষা পরিবর্তন করুন (English / বাংলা)")
        self.lang_btn.set_css_classes(["pill"])
        self.lang_btn.connect('clicked', self._on_toggle_language)
        header.pack_end(self.lang_btn)

        # Reset button
        reset_btn = Gtk.Button(label="Reset (D65)")
        reset_btn.set_tooltip_text(self._t("রিসেট করে ১০০% স্টুডিও D65 রেফারেন্স মোডে ফিরে যান", "Reset display to Studio Reference D65 (6500K)"))
        reset_btn.connect('clicked', lambda _: self.select_preset('studio'))
        header.pack_end(reset_btn)

        # Save Default button
        save_btn = Gtk.Button(label="💾 " + self._t("সেভ ডিফল্ট", "Save Default"))
        save_btn.set_css_classes(["suggested-action", "pill"])
        save_btn.set_tooltip_text(self._t("বর্তমান সেটিংস ডিফল্ট ও স্টার্টআপ হিসেবে সংরক্ষণ করুন", "Save current calibration as startup default"))
        save_btn.connect('clicked', self._on_save_clicked)
        header.pack_end(save_btn)

        # Root vertical box
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root_box.append(header)

        # 2. Hero Card (Persistent Overview across all tabs)
        self.hero_card = self._build_hero_card()
        root_box.append(self.hero_card)

        # 3. ViewStack content pages
        # Page 1: Presets Gallery
        presets_page = self._build_presets_page()
        self.view_stack.add_titled_with_icon(presets_page, 'presets', self._t('প্রিসেট গ্যালারি', 'Presets Gallery'), 'view-grid-symbolic')

        # Page 2: Fine Calibration
        tuner_page = self._build_tuner_page()
        self.view_stack.add_titled_with_icon(tuner_page, 'tuner', self._t('ফাইন টিউনিং', 'Fine Calibration'), 'preferences-color-symbolic')

        # Page 3: Display Diagnostics
        info_page = self._build_info_page()
        self.view_stack.add_titled_with_icon(info_page, 'info', self._t('মনিটর ইনফো', 'Hardware Diagnostics'), 'video-display-symbolic')

        root_box.append(self.view_stack)

        # Bottom Toast Overlay
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(root_box)
        self.set_content(self.toast_overlay)

    def _build_hero_card(self):
        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        hero.set_css_classes(["hero-card"])

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

        # Left Info
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        left_box.set_hexpand(True)

        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.hero_title = Gtk.Label(label="Studio Reference (D65)")
        self.hero_title.set_css_classes(["hero-title"])
        self.hero_title.set_halign(Gtk.Align.START)
        title_box.append(self.hero_title)

        status_pill = Gtk.Label(label="● " + self._t("লাইভ অ্যাক্টিভ", "Live Active"))
        status_pill.set_css_classes(["status-active-pill"])
        title_box.append(status_pill)
        left_box.append(title_box)

        self.hero_desc = Gtk.Label(label="International designer & photo/video standard (6500K sRGB)")
        self.hero_desc.set_css_classes(["hero-subtitle"])
        self.hero_desc.set_halign(Gtk.Align.START)
        left_box.append(self.hero_desc)

        top_row.append(left_box)

        # Right Metric Pills
        metrics_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.hero_bright_pill = Gtk.Label(label="🔆 100%")
        self.hero_bright_pill.set_css_classes(["metric-pill"])
        metrics_box.append(self.hero_bright_pill)

        self.hero_temp_pill = Gtk.Label(label="🌡️ 6500K")
        self.hero_temp_pill.set_css_classes(["metric-pill"])
        metrics_box.append(self.hero_temp_pill)

        self.hero_contrast_pill = Gtk.Label(label="⚖️ 100%")
        self.hero_contrast_pill.set_css_classes(["metric-pill"])
        metrics_box.append(self.hero_contrast_pill)

        self.hero_gamma_pill = Gtk.Label(label="🎛️ 1.00γ")
        self.hero_gamma_pill.set_css_classes(["metric-pill"])
        metrics_box.append(self.hero_gamma_pill)

        top_row.append(metrics_box)
        hero.append(top_row)

        # Bottom Calibration Strip
        calib_strip = self._build_calibration_strip()
        hero.append(calib_strip)

        return hero

    def _build_calibration_strip(self):
        calib_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        calib_box.set_homogeneous(True)

        steps = [
            ("#000000", "0%"),
            ("#1a1a1a", "15%"),
            ("#404040", "35%"),
            ("#808080", "50%"),
            ("#bfbfbf", "75%"),
            ("#ffffff", "100%"),
            ("#ef4444", "Red"),
            ("#22c55e", "Green"),
            ("#3b82f6", "Blue"),
            ("#f59e0b", "Warm"),
            ("#8b5cf6", "Violet")
        ]

        for color, lbl_text in steps:
            lbl = Gtk.Label()
            fg = "#ffffff" if color in ["#000000", "#1a1a1a", "#404040", "#3b82f6", "#8b5cf6", "#ef4444"] else "#000000"
            lbl.set_markup(f"<span background='{color}' foreground='{fg}' font_desc='8.5'> <b>{lbl_text}</b> </span>")
            lbl.set_size_request(-1, 16)
            calib_box.append(lbl)

        return calib_box

    def _build_presets_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        page_box.set_margin_start(18)
        page_box.set_margin_end(18)
        page_box.set_margin_top(8)
        page_box.set_margin_bottom(24)

        # Filter & Search Row
        top_filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        top_filter_box.set_margin_bottom(6)

        categories = [
            ('all', self._t('সবগুলো', 'All')),
            ('work', self._t('💼 কাজ ও রিডিং', '💼 Work & Read')),
            ('media', self._t('🎬 মিডিয়া ও গেমিং', '🎬 Media & Gaming')),
            ('night', self._t('🌙 নাইট ও কেয়ার', '🌙 Night Care')),
            ('custom', self._t('⭐ কাস্টম', '⭐ Custom'))
        ]
        self.category_buttons = {}
        for cid, clabel in categories:
            btn = Gtk.Button(label=clabel)
            btn.set_css_classes(["filter-btn"])
            if cid == 'all':
                btn.add_css_class("active")
            btn.connect('clicked', lambda _, c=cid: self._on_filter_changed(c))
            top_filter_box.append(btn)
            self.category_buttons[cid] = btn

        # Search entry
        search_entry = Gtk.SearchEntry()
        search_entry.set_placeholder_text(self._t("প্রিসেট খুঁজুন...", "Search presets..."))
        search_entry.connect('search-changed', self._on_search_changed)
        search_entry.set_hexpand(True)
        top_filter_box.append(search_entry)

        page_box.append(top_filter_box)

        # Presets FlowBox
        self.presets_flow = Gtk.FlowBox()
        self.presets_flow.set_valign(Gtk.Align.START)
        self.presets_flow.set_max_children_per_line(2)
        self.presets_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.presets_flow.set_column_spacing(12)
        self.presets_flow.set_row_spacing(12)
        self.presets_flow.set_homogeneous(True)

        self._populate_preset_cards()
        page_box.append(self.presets_flow)

        # Custom Preset Creator Section
        creator_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        creator_card.set_css_classes(["control-card"])
        creator_card.set_margin_top(16)

        creator_label_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        creator_label_box.set_hexpand(True)
        lbl_c_title = Gtk.Label(label="➕ " + self._t("নতুন কাস্টম প্রিসেট তৈরি করুন", "Create New Custom Preset"))
        lbl_c_title.set_css_classes(["control-title"])
        lbl_c_title.set_halign(Gtk.Align.START)
        lbl_c_desc = Gtk.Label(label=self._t("বর্তমান স্লাইডারের মান দিয়ে নিজের পছন্দের প্রিসেট বানিয়ে রাখুন", "Save current brightness, temperature & contrast values as your custom preset"))
        lbl_c_desc.set_css_classes(["control-subtitle"])
        lbl_c_desc.set_halign(Gtk.Align.START)
        creator_label_box.append(lbl_c_title)
        creator_label_box.append(lbl_c_desc)
        creator_card.append(creator_label_box)

        self.custom_entry = Gtk.Entry()
        self.custom_entry.set_placeholder_text(self._t("প্রিসেটের নাম...", "Preset name..."))
        self.custom_entry.set_size_request(200, -1)
        creator_card.append(self.custom_entry)

        save_custom_btn = Gtk.Button(label=self._t("সেভ করুন", "Save"))
        save_custom_btn.set_css_classes(["suggested-action", "pill"])
        save_custom_btn.connect('clicked', self._on_add_custom_preset)
        creator_card.append(save_custom_btn)

        # Export & Import buttons
        export_btn = Gtk.Button(label="📤 " + self._t("এক্সপোর্ট", "Export"))
        export_btn.set_tooltip_text(self._t("কাস্টম প্রিসেট ব্যাকআপ নিন", "Export custom presets to JSON"))
        export_btn.set_css_classes(["pill"])
        export_btn.connect('clicked', self._on_export_presets)
        creator_card.append(export_btn)

        import_btn = Gtk.Button(label="📥 " + self._t("ইমপোর্ট", "Import"))
        import_btn.set_tooltip_text(self._t("কাস্টম প্রিসেট রিস্টোর করুন", "Import custom presets from JSON"))
        import_btn.set_css_classes(["pill"])
        import_btn.connect('clicked', self._on_import_presets)
        creator_card.append(import_btn)

        page_box.append(creator_card)

        scrolled.set_child(page_box)
        return scrolled

    def _populate_preset_cards(self):
        while True:
            child = self.presets_flow.get_first_child()
            if not child:
                break
            self.presets_flow.remove(child)
        self.preset_cards = {}

        # Built-in presets
        for pid, pdata in BUILTIN_PRESETS.items():
            card = self._create_preset_card(pdata, is_custom=False)
            self.presets_flow.append(card)

        # Custom presets
        custom_presets = self.config.get('custom_presets', {})
        for cid, cdata in custom_presets.items():
            card = self._create_preset_card(cdata, is_custom=True)
            self.presets_flow.append(card)

        self._filter_cards()

    def _create_preset_card(self, pdata, is_custom=False):
        pid = pdata['id']
        category = pdata.get('category', 'custom' if is_custom else 'work')

        card_btn = Gtk.Button()
        card_btn.set_css_classes(["preset-card"])
        card_btn.set_cursor_from_name("pointer")

        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header Row
        header_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Color dot indicator
        dot_color = pdata.get('color_dot', '#ffffff')
        dot_lbl = Gtk.Label()
        dot_lbl.set_markup(f"<span foreground='{dot_color}' font_desc='18'>●</span>")
        header_row.append(dot_lbl)

        name_lbl = Gtk.Label(label=pdata['name'])
        name_lbl.set_css_classes(["card-title"])
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_hexpand(True)
        header_row.append(name_lbl)

        tag_lbl = Gtk.Label(label=pdata.get('tag', 'Custom'))
        tag_lbl.set_css_classes(["card-tag"])
        header_row.append(tag_lbl)

        if is_custom:
            del_btn = Gtk.Button(label="🗑️")
            del_btn.set_tooltip_text(self._t("এই কাস্টম প্রিসেটটি মুছুন", "Delete this custom preset"))
            del_btn.set_css_classes(["flat"])
            del_btn.connect('clicked', lambda _, p_id=pid: self._delete_custom_preset(p_id))
            header_row.append(del_btn)

        card_box.append(header_row)

        # Description
        desc_text = pdata.get('desc_bn' if self.lang == 'bn' else 'desc_en', pdata.get('desc', f"{pdata['kelvin']}K • {int(pdata['brightness']*100)}% Brightness"))
        desc_lbl = Gtk.Label(label=desc_text)
        desc_lbl.set_wrap(True)
        desc_lbl.set_halign(Gtk.Align.START)
        desc_lbl.set_css_classes(["card-desc"])
        card_box.append(desc_lbl)

        # Bottom row with pills and status
        foot_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        foot_row.set_margin_top(4)

        k_pill = Gtk.Label(label=f"{pdata['kelvin']}K")
        k_pill.set_css_classes(["metric-pill"])
        foot_row.append(k_pill)

        b_pill = Gtk.Label(label=f"{int(pdata['brightness']*100)}% 🔆")
        b_pill.set_css_classes(["metric-pill"])
        foot_row.append(b_pill)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        foot_row.append(spacer)

        active_badge = Gtk.Label(label="✓ " + self._t("সক্রিয়", "Active"))
        active_badge.set_css_classes(["check-pill"])
        active_badge.set_visible(pid == self.config.get('active_preset'))
        foot_row.append(active_badge)

        card_box.append(foot_row)
        card_btn.set_child(card_box)

        card_btn.connect('clicked', lambda _: self.select_preset(pid))
        
        self.preset_cards[pid] = {
            'widget': card_btn,
            'active_badge': active_badge,
            'category': category,
            'name': pdata['name'].lower(),
            'desc': desc_text.lower(),
            'pdata': pdata
        }
        return card_btn

    def _on_filter_changed(self, cat):
        self.current_category = cat
        for cid, btn in self.category_buttons.items():
            if cid == cat:
                btn.add_css_class("active")
            else:
                btn.remove_css_class("active")
        self._filter_cards()

    def _on_search_changed(self, entry):
        self.search_query = entry.get_text().strip().lower()
        self._filter_cards()

    def _filter_cards(self):
        cat = self.current_category
        q = self.search_query
        for pid, data in self.preset_cards.items():
            w = data['widget']
            c = data['category']
            name = data['name']
            desc = data['desc']

            match_cat = (cat == 'all') or (cat == c) or (cat == 'custom' and c == 'custom')
            match_search = (not q) or (q in name) or (q in desc)
            w.set_visible(match_cat and match_search)

    def _build_tuner_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_box.set_margin_start(18)
        page_box.set_margin_end(18)
        page_box.set_margin_top(12)
        page_box.set_margin_bottom(24)

        # 1. Brightness Card
        bright_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        bright_card.set_css_classes(["control-card"])

        b_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        b_title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        b_title_box.set_hexpand(True)
        lbl_b_title = Gtk.Label(label="🔆 " + self._t("ডিসপ্লে উজ্জ্বলতা (Luminance & Brightness)", "Display Brightness & Luminance"))
        lbl_b_title.set_css_classes(["control-title"])
        lbl_b_title.set_halign(Gtk.Align.START)
        lbl_b_sub = Gtk.Label(label=self._t("স্ক্রিনের সামগ্রিক লুমিন্যান্স ও আলো নিয়ন্ত্রণ (২০% থেকে ১০০%)", "Overall display backlight and luminance control (20% to 100%)"))
        lbl_b_sub.set_css_classes(["control-subtitle"])
        lbl_b_sub.set_halign(Gtk.Align.START)
        b_title_box.append(lbl_b_title)
        b_title_box.append(lbl_b_sub)
        b_header.append(b_title_box)

        self.tuner_bright_val = Gtk.Label(label="100%")
        self.tuner_bright_val.set_css_classes(["control-value"])
        b_header.append(self.tuner_bright_val)
        bright_card.append(b_header)

        # Slider + Steppers row
        b_control_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        b_m10 = Gtk.Button(label="-10%")
        b_m10.set_css_classes(["stepper-btn"])
        b_m10.connect('clicked', lambda _: self._step_bright(-10))
        b_m5 = Gtk.Button(label="-5%")
        b_m5.set_css_classes(["stepper-btn"])
        b_m5.connect('clicked', lambda _: self._step_bright(-5))

        self.bright_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 20, 100, 1)
        self.bright_slider.set_hexpand(True)
        self.bright_slider.set_value(self.config['brightness'] * 100)
        self.bright_slider.connect('value-changed', self._on_bright_changed)

        b_p5 = Gtk.Button(label="+5%")
        b_p5.set_css_classes(["stepper-btn"])
        b_p5.connect('clicked', lambda _: self._step_bright(5))
        b_p10 = Gtk.Button(label="+10%")
        b_p10.set_css_classes(["stepper-btn"])
        b_p10.connect('clicked', lambda _: self._step_bright(10))

        b_control_row.append(b_m10)
        b_control_row.append(b_m5)
        b_control_row.append(self.bright_slider)
        b_control_row.append(b_p5)
        b_control_row.append(b_p10)
        bright_card.append(b_control_row)

        # Target Quick Pills
        b_targets_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_bt = Gtk.Label(label=self._t("কুইক টার্গেট: ", "Quick Targets: "))
        lbl_bt.set_css_classes(["card-desc"])
        b_targets_row.append(lbl_bt)
        for pct in [40, 60, 80, 100]:
            btn_t = Gtk.Button(label=f"{pct}%")
            btn_t.set_css_classes(["target-pill"])
            btn_t.connect('clicked', lambda _, v=pct: self.bright_slider.set_value(v))
            b_targets_row.append(btn_t)
        bright_card.append(b_targets_row)

        page_box.append(bright_card)

        # 2. Color Temperature Card
        temp_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        temp_card.set_css_classes(["control-card"])

        t_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        t_title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        t_title_box.set_hexpand(True)
        lbl_t_title = Gtk.Label(label="🌡️ " + self._t("কালার টেম্পারেচার ও হোয়াইট পয়েন্ট (Kelvin White Point)", "Color Temperature & White Point"))
        lbl_t_title.set_css_classes(["control-title"])
        lbl_t_title.set_halign(Gtk.Align.START)
        lbl_t_sub = Gtk.Label(label=self._t("সাদা রঙের উষ্ণতা (২২০০K মোমবাতির শিখা থেকে ৭৫০০K শীতল ডে-লাইট)", "White point temperature (2200K warm candle flame to 7500K cool daylight)"))
        lbl_t_sub.set_css_classes(["control-subtitle"])
        lbl_t_sub.set_halign(Gtk.Align.START)
        t_title_box.append(lbl_t_title)
        t_title_box.append(lbl_t_sub)
        t_header.append(t_title_box)

        self.tuner_temp_val = Gtk.Label(label="6500K")
        self.tuner_temp_val.set_css_classes(["control-value"])
        t_header.append(self.tuner_temp_val)
        temp_card.append(t_header)

        # Slider + Steppers row
        t_control_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        t_warm = Gtk.Button(label="Warm -100K")
        t_warm.set_css_classes(["stepper-btn"])
        t_warm.connect('clicked', lambda _: self._step_temp(-100))

        self.temp_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 2200, 7500, 50)
        self.temp_slider.set_hexpand(True)
        self.temp_slider.set_value(self.config['kelvin'])
        self.temp_slider.connect('value-changed', self._on_temp_changed)

        t_cool = Gtk.Button(label="Cool +100K")
        t_cool.set_css_classes(["stepper-btn"])
        t_cool.connect('clicked', lambda _: self._step_temp(100))

        t_control_row.append(t_warm)
        t_control_row.append(self.temp_slider)
        t_control_row.append(t_cool)
        temp_card.append(t_control_row)

        # Quick Kelvin Pills
        t_targets_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        lbl_tt = Gtk.Label(label=self._t("কুইক টোন: ", "Quick Tones: "))
        lbl_tt.set_css_classes(["card-desc"])
        t_targets_row.append(lbl_tt)
        kelvin_presets = [
            (2200, "🕯️ 2200K"),
            (2800, "🌙 2800K"),
            (3800, "🌆 3800K"),
            (5000, "📖 5000K"),
            (5800, "☀️ 5800K"),
            (6500, "🎯 6500K D65")
        ]
        for k_val, k_text in kelvin_presets:
            btn_k = Gtk.Button(label=k_text)
            btn_k.set_css_classes(["target-pill"])
            btn_k.connect('clicked', lambda _, v=k_val: self.temp_slider.set_value(v))
            t_targets_row.append(btn_k)
        temp_card.append(t_targets_row)

        page_box.append(temp_card)

        # 3. Contrast & Gamma Card
        cg_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        cg_card.set_css_classes(["control-card"])

        cg_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        lbl_cg_title = Gtk.Label(label="⚖️ " + self._t("কনট্রাস্ট ও গামা ব্যালান্স (Contrast & Gamma Curve)", "Contrast & Gamma Curve Calibration"))
        lbl_cg_title.set_css_classes(["control-title"])
        lbl_cg_title.set_halign(Gtk.Align.START)
        lbl_cg_sub = Gtk.Label(label=self._t("কালো ও সাদার গভীরতা এবং মিডটোন ব্যালান্স টিউন করুন", "Tune deep shadow tones and sRGB 2.2 midtone distribution"))
        lbl_cg_sub.set_css_classes(["control-subtitle"])
        lbl_cg_sub.set_halign(Gtk.Align.START)
        cg_header.append(lbl_cg_title)
        cg_header.append(lbl_cg_sub)
        cg_card.append(cg_header)

        # Contrast Row
        c_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl_c_name = Gtk.Label(label=self._t("কনট্রাস্ট:", "Contrast:"))
        lbl_c_name.set_size_request(80, -1)
        lbl_c_name.set_halign(Gtk.Align.START)
        c_row.append(lbl_c_name)

        self.contrast_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 70, 130, 1)
        self.contrast_slider.set_hexpand(True)
        self.contrast_slider.set_value(self.config['contrast'] * 100)
        self.contrast_slider.connect('value-changed', self._on_contrast_changed)
        c_row.append(self.contrast_slider)

        self.tuner_contrast_val = Gtk.Label(label="100%")
        self.tuner_contrast_val.set_size_request(45, -1)
        self.tuner_contrast_val.set_css_classes(["control-value"])
        c_row.append(self.tuner_contrast_val)

        btn_c_rst = Gtk.Button(label="100%")
        btn_c_rst.set_css_classes(["target-pill"])
        btn_c_rst.connect('clicked', lambda _: self.contrast_slider.set_value(100))
        c_row.append(btn_c_rst)
        cg_card.append(c_row)

        # Gamma Row
        g_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        lbl_g_name = Gtk.Label(label=self._t("গামা কার্ভ:", "Gamma:"))
        lbl_g_name.set_size_request(80, -1)
        lbl_g_name.set_halign(Gtk.Align.START)
        g_row.append(lbl_g_name)

        self.gamma_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.70, 1.40, 0.05)
        self.gamma_slider.set_hexpand(True)
        self.gamma_slider.set_value(self.config['gamma'])
        self.gamma_slider.connect('value-changed', self._on_gamma_changed)
        g_row.append(self.gamma_slider)

        self.tuner_gamma_val = Gtk.Label(label="1.00")
        self.tuner_gamma_val.set_size_request(45, -1)
        self.tuner_gamma_val.set_css_classes(["control-value"])
        g_row.append(self.tuner_gamma_val)

        btn_g_rst = Gtk.Button(label="1.00 sRGB")
        btn_g_rst.set_css_classes(["target-pill"])
        btn_g_rst.connect('clicked', lambda _: self.gamma_slider.set_value(1.0))
        g_row.append(btn_g_rst)
        cg_card.append(g_row)

        page_box.append(cg_card)

        # 4. RGB Fine-Tuning Card
        rgb_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        rgb_card.set_css_classes(["control-card"])

        rgb_head = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        rgb_title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        rgb_title_box.set_hexpand(True)
        lbl_rgb_t = Gtk.Label(label="🎨 " + self._t("আরজিবি চ্যানেল ব্যালান্স (Hardware RGB Channel Gains)", "Hardware RGB Channel Gains"))
        lbl_rgb_t.set_css_classes(["control-title"])
        lbl_rgb_t.set_halign(Gtk.Align.START)
        lbl_rgb_sub = Gtk.Label(label=self._t("রেড, গ্রিন ও ব্লু চ্যানেল স্বাধীনভাবে নিয়ন্ত্রণ করে যেকোনো সূক্ষ্ম রঙের আভা সংশোধন করুন", "Independently adjust Red, Green, and Blue gains to eliminate panel color cast"))
        lbl_rgb_sub.set_css_classes(["control-subtitle"])
        lbl_rgb_sub.set_halign(Gtk.Align.START)
        rgb_title_box.append(lbl_rgb_t)
        rgb_title_box.append(lbl_rgb_sub)
        rgb_head.append(rgb_title_box)

        btn_rgb_rst = Gtk.Button(label="Reset RGB (100%)")
        btn_rgb_rst.set_css_classes(["stepper-btn"])
        btn_rgb_rst.connect('clicked', self._reset_rgb)
        rgb_head.append(btn_rgb_rst)
        rgb_card.append(rgb_head)

        # Red Channel
        r_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_r = Gtk.Label()
        lbl_r.set_markup("<span foreground='#ef4444'><b>🔴 Red:</b></span>")
        lbl_r.set_size_request(70, -1)
        lbl_r.set_halign(Gtk.Align.START)
        r_box.append(lbl_r)

        self.r_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 75, 125, 1)
        self.r_slider.set_hexpand(True)
        self.r_slider.set_value(self.config.get('r_gain', 1.0) * 100)
        self.r_slider.connect('value-changed', self._on_rgb_changed)
        r_box.append(self.r_slider)

        self.tuner_r_val = Gtk.Label(label="100%")
        self.tuner_r_val.set_size_request(45, -1)
        r_box.append(self.tuner_r_val)
        rgb_card.append(r_box)

        # Green Channel
        g_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_g = Gtk.Label()
        lbl_g.set_markup("<span foreground='#22c55e'><b>🟢 Green:</b></span>")
        lbl_g.set_size_request(70, -1)
        lbl_g.set_halign(Gtk.Align.START)
        g_box.append(lbl_g)

        self.g_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 75, 125, 1)
        self.g_slider.set_hexpand(True)
        self.g_slider.set_value(self.config.get('g_gain', 1.0) * 100)
        self.g_slider.connect('value-changed', self._on_rgb_changed)
        g_box.append(self.g_slider)

        self.tuner_g_val = Gtk.Label(label="100%")
        self.tuner_g_val.set_size_request(45, -1)
        g_box.append(self.tuner_g_val)
        rgb_card.append(g_box)

        # Blue Channel
        b_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_b = Gtk.Label()
        lbl_b.set_markup("<span foreground='#3b82f6'><b>🔵 Blue:</b></span>")
        lbl_b.set_size_request(70, -1)
        lbl_b.set_halign(Gtk.Align.START)
        b_box.append(lbl_b)

        self.b_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 75, 125, 1)
        self.b_slider.set_hexpand(True)
        self.b_slider.set_value(self.config.get('b_gain', 1.0) * 100)
        self.b_slider.connect('value-changed', self._on_rgb_changed)
        b_box.append(self.b_slider)

        self.tuner_b_val = Gtk.Label(label="100%")
        self.tuner_b_val.set_size_request(45, -1)
        b_box.append(self.tuner_b_val)
        rgb_card.append(b_box)

        page_box.append(rgb_card)

        scrolled.set_child(page_box)
        return scrolled

    def _build_info_page(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_start(18)
        box.set_margin_end(18)
        box.set_margin_top(12)
        box.set_margin_bottom(24)

        # Card 1: Monitor Identity
        card1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card1.set_css_classes(["info-card"])
        lbl1 = Gtk.Label(label="🖥️ " + self._t("মনিটর ও ডিসপ্লে আইডেন্টিটি (Display Identity)", "Display & Monitor Identity"))
        lbl1.set_css_classes(["info-header"])
        lbl1.set_halign(Gtk.Align.START)
        card1.append(lbl1)

        st = self.engine.display_state
        details1 = [
            (self._t("মনিটরের মডেল (Model):", "Monitor Model:"), st.get('display_name', self.engine.monitor_info)),
            (self._t("কানেকশন পোর্ট (Interface):", "Interface Connector:"), st.get('connector', 'HDMI')),
            (self._t("বর্তমান রেজোলিউশন (Resolution):", "Current Resolution:"), st.get('resolution', '1920 × 1080')),
            (self._t("রিফ্রেশ রেট (Refresh Rate):", "Refresh Rate:"), st.get('refresh_rate', '100.00 Hz')),
            (self._t("সিরিয়াল নম্বর (Serial):", "Serial Number:"), st.get('serial', 'N/A'))
        ]
        for k, v in details1:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            lk = Gtk.Label(label=k)
            lk.set_css_classes(["info-label"])
            lk.set_halign(Gtk.Align.START)
            lk.set_hexpand(True)
            lv = Gtk.Label(label=v)
            lv.set_css_classes(["info-val"])
            row.append(lk)
            row.append(lv)
            card1.append(row)
        box.append(card1)

        # Card 2: GPU & Graphics Pipeline
        card2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card2.set_css_classes(["info-card"])
        lbl2 = Gtk.Label(label="⚡ " + self._t("গ্রাফিক্স কার্ড ও ক্যালিব্রেশন পাইপলাইন (Graphics Pipeline)", "GPU & Calibration Pipeline"))
        lbl2.set_css_classes(["info-header"])
        lbl2.set_halign(Gtk.Align.START)
        card2.append(lbl2)

        details2 = [
            (self._t("গ্রাফিক্স প্রসেসর (GPU):", "Graphics Processor (GPU):"), self.engine.gpu_info),
            (self._t("ডিসপ্লে সার্ভার (Compositor):", "Display Server (Compositor):"), "GNOME Shell (Wayland Native)"),
            (self._t("ক্যালিব্রেশন ইঞ্জিন (Engine):", "Calibration Engine:"), "Mutter Direct CRTC Hardware Gamma LUT"),
            (self._t("লুকআপ টেবিল রেজোলিউশন (LUT Size):", "Lookup Table Precision (LUT):"), "1024-step 16-bit (Precision Color Pipeline)"),
            (self._t("হার্ডওয়্যার রেসপন্স ল্যাটেন্সি (Latency):", "Hardware Response Latency:"), "< 20 ms (Zero-latency instant sync)")
        ]
        for k, v in details2:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            lk = Gtk.Label(label=k)
            lk.set_css_classes(["info-label"])
            lk.set_halign(Gtk.Align.START)
            lk.set_hexpand(True)
            lv = Gtk.Label(label=v)
            lv.set_css_classes(["info-val"])
            row.append(lk)
            row.append(lv)
            card2.append(row)
        box.append(card2)

        # Card 3: Color Standards & Health Guide
        card3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card3.set_css_classes(["info-card"])
        lbl3 = Gtk.Label(label="🎯 " + self._t("কালার স্ট্যান্ডার্ড ও স্বাস্থ্য নির্দেশিকা (Color & Health Guide)", "Color Standards & Health Guide"))
        lbl3.set_css_classes(["info-header"])
        lbl3.set_halign(Gtk.Align.START)
        card3.append(lbl3)

        tips = [
            ("🎯 D65 (6500K):", self._t("ফটো, ভিডিও, গ্রাফিক্স ও ওয়েব ডিজাইনের জন্য ১০০% আন্তর্জাতিক sRGB/Rec.709 স্ট্যান্ডার্ড।", "100% industry reference sRGB / Rec.709 white point for digital art, photo, and video editing.")),
            ("☀️ Daylight (5800K):", self._t("দিনের বেলা অফিস কাজ ও ব্রাউজিংয়ের জন্য চোখের জন্য অত্যন্ত আরামদায়ক ও প্রাণবন্ত।", "Comfortable, crisp daylight illumination for day-to-day productivity and text clarity.")),
            ("📖 Reading & Focus (4200K-5000K):", self._t("প্রোগ্রামিং ও দীর্ঘ সময় পড়াশোনার জন্য চোখ শান্ত রাখা সফট রিডিং টোন।", "Reduces harsh blue light for marathon coding sessions and document review.")),
            ("🌙 Deep Night (2200K-2800K):", self._t("রাতে অন্ধকার ঘরে নীল আলো দূর করে মেলাটোনিন রক্ষা করে এবং গভীর ঘুমে সহায়তা করে।", "Minimizes circadian-disrupting blue wavelength to protect natural melatonin production before sleep."))
        ]
        for k, v in tips:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            lk = Gtk.Label(label=k)
            lk.set_css_classes(["info-label"])
            lk.set_halign(Gtk.Align.START)
            lv = Gtk.Label(label=v)
            lv.set_css_classes(["card-desc"])
            lv.set_hexpand(True)
            lv.set_halign(Gtk.Align.START)
            row.append(lk)
            row.append(lv)
            card3.append(row)
        box.append(card3)

        scrolled.set_child(box)
        return scrolled

    def _on_toggle_language(self, _):
        self.lang = 'en' if self.lang == 'bn' else 'bn'
        self.config['language'] = self.lang
        save_config(self.config)
        self.lang_btn.set_label("BN" if self.lang == 'bn' else "EN")
        
        # Refresh window
        self._populate_preset_cards()
        self._sync_all_from_config()

        toast = Adw.Toast.new(f"Language changed to {'বাংলা' if self.lang == 'bn' else 'English'}")
        self.toast_overlay.add_toast(toast)

    def select_preset(self, pid):
        pdata = None
        if pid in BUILTIN_PRESETS:
            pdata = BUILTIN_PRESETS[pid]
        elif pid in self.config.get('custom_presets', {}):
            pdata = self.config['custom_presets'][pid]
        
        if not pdata:
            return

        self.config['active_preset'] = pid
        self.config['kelvin'] = pdata['kelvin']
        self.config['brightness'] = pdata['brightness']
        self.config['contrast'] = pdata.get('contrast', 1.0)
        self.config['gamma'] = pdata.get('gamma', 1.0)
        self.config['r_gain'] = pdata.get('r_gain', 1.0)
        self.config['g_gain'] = pdata.get('g_gain', 1.0)
        self.config['b_gain'] = pdata.get('b_gain', 1.0)

        self._sync_all_from_config()
        self._apply_current_settings()

        escaped_title = GLib.markup_escape_text(f"{self._t('সক্রিয়', 'Active')}: {pdata['name']} ({pdata['kelvin']}K, {int(pdata['brightness']*100)}%)")
        toast = Adw.Toast.new(escaped_title)
        self.toast_overlay.add_toast(toast)

    def _sync_all_from_config(self):
        # 1. Update Tuner Sliders
        self.bright_slider.set_value(self.config['brightness'] * 100)
        self.temp_slider.set_value(self.config['kelvin'])
        self.contrast_slider.set_value(self.config['contrast'] * 100)
        self.gamma_slider.set_value(self.config['gamma'])
        self.r_slider.set_value(self.config.get('r_gain', 1.0) * 100)
        self.g_slider.set_value(self.config.get('g_gain', 1.0) * 100)
        self.b_slider.set_value(self.config.get('b_gain', 1.0) * 100)

        # 2. Update Tuner Labels
        b_pct = int(self.config['brightness'] * 100)
        k_val = int(self.config['kelvin'])
        c_pct = int(self.config['contrast'] * 100)
        g_val = self.config['gamma']
        r_pct = int(self.config.get('r_gain', 1.0) * 100)
        g_pct = int(self.config.get('g_gain', 1.0) * 100)
        b_pct_val = int(self.config.get('b_gain', 1.0) * 100)

        self.tuner_bright_val.set_label(f"{b_pct}%")
        self.tuner_temp_val.set_label(f"{k_val}K")
        self.tuner_contrast_val.set_label(f"{c_pct}%")
        self.tuner_gamma_val.set_label(f"{g_val:.2f}")
        self.tuner_r_val.set_label(f"{r_pct}%")
        self.tuner_g_val.set_label(f"{g_pct}%")
        self.tuner_b_val.set_label(f"{b_pct_val}%")

        # 3. Update Hero Card
        act_id = self.config.get('active_preset', 'custom')
        pdata = BUILTIN_PRESETS.get(act_id) or self.config.get('custom_presets', {}).get(act_id)
        if pdata:
            self.hero_title.set_label(pdata['name'])
            desc_text = pdata.get('desc_bn' if self.lang == 'bn' else 'desc_en', pdata.get('desc', ''))
            self.hero_desc.set_label(desc_text)
        else:
            self.hero_title.set_label(self._t("কাস্টম মোড (Custom Mode)", "Custom Calibration Mode"))
            self.hero_desc.set_label(self._t("ব্যবহারকারীর পছন্দের কাস্টম ব্রাইটনেস ও কালার টিউনিং", "User fine-tuned live brightness and color temperature calibration"))

        self.hero_bright_pill.set_label(f"🔆 {b_pct}%")
        self.hero_temp_pill.set_label(f"🌡️ {k_val}K")
        self.hero_contrast_pill.set_label(f"⚖️ {c_pct}%")
        self.hero_gamma_pill.set_label(f"🎛️ {g_val:.2f}γ")

        # 4. Highlight Active Preset Card
        for pid, data in self.preset_cards.items():
            btn = data['widget']
            badge = data['active_badge']
            if pid == act_id:
                btn.add_css_class("active-card")
                badge.set_visible(True)
            else:
                btn.remove_css_class("active-card")
                badge.set_visible(False)

    def _step_bright(self, delta):
        cur = self.bright_slider.get_value()
        self.bright_slider.set_value(max(20, min(100, cur + delta)))

    def _step_temp(self, delta):
        cur = self.temp_slider.get_value()
        self.temp_slider.set_value(max(2200, min(7500, cur + delta)))

    def _on_bright_changed(self, scale):
        val = scale.get_value()
        self.config['brightness'] = val / 100.0
        self.config['active_preset'] = 'custom'
        self.tuner_bright_val.set_label(f"{int(val)}%")
        self.hero_bright_pill.set_label(f"🔆 {int(val)}%")
        self.hero_title.set_label(self._t("কাস্টম মোড (Custom Mode)", "Custom Mode"))
        self._schedule_apply()

    def _on_temp_changed(self, scale):
        val = int(scale.get_value())
        self.config['kelvin'] = val
        self.config['active_preset'] = 'custom'
        self.tuner_temp_val.set_label(f"{val}K")
        self.hero_temp_pill.set_label(f"🌡️ {val}K")
        self.hero_title.set_label(self._t("কাস্টম মোড (Custom Mode)", "Custom Mode"))
        self._schedule_apply()

    def _on_contrast_changed(self, scale):
        val = scale.get_value()
        self.config['contrast'] = val / 100.0
        self.config['active_preset'] = 'custom'
        self.tuner_contrast_val.set_label(f"{int(val)}%")
        self.hero_contrast_pill.set_label(f"⚖️ {int(val)}%")
        self.hero_title.set_label(self._t("কাস্টম মোড (Custom Mode)", "Custom Mode"))
        self._schedule_apply()

    def _on_gamma_changed(self, scale):
        val = scale.get_value()
        self.config['gamma'] = round(val, 2)
        self.config['active_preset'] = 'custom'
        self.tuner_gamma_val.set_label(f"{val:.2f}")
        self.hero_gamma_pill.set_label(f"🎛️ {val:.2f}γ")
        self.hero_title.set_label(self._t("কাস্টম মোড (Custom Mode)", "Custom Mode"))
        self._schedule_apply()

    def _on_rgb_changed(self, scale):
        r = self.r_slider.get_value() / 100.0
        g = self.g_slider.get_value() / 100.0
        b = self.b_slider.get_value() / 100.0
        self.config['r_gain'] = r
        self.config['g_gain'] = g
        self.config['b_gain'] = b
        self.config['active_preset'] = 'custom'
        self.tuner_r_val.set_label(f"{int(r*100)}%")
        self.tuner_g_val.set_label(f"{int(g*100)}%")
        self.tuner_b_val.set_label(f"{int(b*100)}%")
        self.hero_title.set_label(self._t("কাস্টম মোড (Custom Mode)", "Custom Mode"))
        self._schedule_apply()

    def _reset_rgb(self, _):
        self.r_slider.set_value(100)
        self.g_slider.set_value(100)
        self.b_slider.set_value(100)

    def _schedule_apply(self):
        if self.update_timeout_id is not None:
            GLib.source_remove(self.update_timeout_id)
        self.update_timeout_id = GLib.timeout_add(15, self._apply_current_settings)

    def _apply_current_settings(self):
        self.update_timeout_id = None
        self.engine.apply_lut(
            brightness=self.config['brightness'],
            contrast=self.config['contrast'],
            gamma=self.config['gamma'],
            kelvin=self.config['kelvin'],
            r_gain=self.config.get('r_gain', 1.0),
            g_gain=self.config.get('g_gain', 1.0),
            b_gain=self.config.get('b_gain', 1.0)
        )
        return False

    def _on_add_custom_preset(self, _):
        name = self.custom_entry.get_text().strip()
        if not name:
            toast = Adw.Toast.new(self._t("দয়া করে প্রিসেটের একটি নাম লিখুন!", "Please enter a preset name!"))
            self.toast_overlay.add_toast(toast)
            return
        
        cid = "custom_" + str(int(GLib.get_real_time() / 1000000))
        color_dot = kelvin_to_hex(self.config['kelvin'])
        new_preset = {
            'id': cid,
            'name': name,
            'category': 'custom',
            'tag': 'Custom Preset',
            'desc_en': f"{self.config['kelvin']}K • {int(self.config['brightness']*100)}% Brightness",
            'desc_bn': f"{self.config['kelvin']}K • {int(self.config['brightness']*100)}% ব্রাইটনেস",
            'kelvin': self.config['kelvin'],
            'brightness': self.config['brightness'],
            'contrast': self.config['contrast'],
            'gamma': self.config['gamma'],
            'r_gain': self.config.get('r_gain', 1.0),
            'g_gain': self.config.get('g_gain', 1.0),
            'b_gain': self.config.get('b_gain', 1.0),
            'color_dot': color_dot
        }
        
        if 'custom_presets' not in self.config:
            self.config['custom_presets'] = {}
        self.config['custom_presets'][cid] = new_preset
        self.config['active_preset'] = cid
        save_config(self.config)
        
        self.custom_entry.set_text("")
        self._populate_preset_cards()
        self._sync_all_from_config()

        escaped_title = GLib.markup_escape_text(f"'{name}' " + self._t("প্রিসেট সংরক্ষিত হয়েছে!", "preset saved!"))
        toast = Adw.Toast.new(escaped_title)
        self.toast_overlay.add_toast(toast)

    def _delete_custom_preset(self, pid):
        if pid in self.config.get('custom_presets', {}):
            name = self.config['custom_presets'][pid]['name']
            del self.config['custom_presets'][pid]
            if self.config.get('active_preset') == pid:
                self.config['active_preset'] = 'studio'
            save_config(self.config)
            self._populate_preset_cards()
            self._sync_all_from_config()
            escaped_title = GLib.markup_escape_text(f"'{name}' " + self._t("মুছে ফেলা হয়েছে", "removed"))
            toast = Adw.Toast.new(escaped_title)
            self.toast_overlay.add_toast(toast)

    def _on_export_presets(self, _):
        export_file = os.path.join(CONFIG_DIR, 'presets_export.json')
        export_presets(export_file)
        toast = Adw.Toast.new(f"{self._t('প্রিসেট এক্সপোর্ট সম্পন্ন:', 'Presets exported to:')} {export_file}")
        self.toast_overlay.add_toast(toast)

    def _on_import_presets(self, _):
        export_file = os.path.join(CONFIG_DIR, 'presets_export.json')
        if os.path.exists(export_file):
            count = import_presets(export_file)
            self.config = load_config()
            self._populate_preset_cards()
            toast = Adw.Toast.new(f"{count} " + self._t("টি প্রিসেট ইমপোর্ট হয়েছে!", "presets imported successfully!"))
        else:
            toast = Adw.Toast.new(self._t("কোনো এক্সপোর্ট ফাইল পাওয়া যায়নি!", "No export file found!"))
        self.toast_overlay.add_toast(toast)

    def _on_save_clicked(self, _):
        save_config(self.config)
        toast = Adw.Toast.new(self._t("বর্তমান সেটিংস ডিফল্ট হিসেবে সংরক্ষিত হয়েছে!", "Current settings saved as startup default!"))
        self.toast_overlay.add_toast(toast)


class StudioApp(Adw.Application):
    def __init__(self, engine, config):
        super().__init__(
            application_id='com.antigravity.DisplayColorStudio',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.engine = engine
        self.config = config

    def do_activate(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CUSTOM_CSS.encode('utf-8'))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        win = self.props.active_window
        if not win:
            win = StudioWindow(self, self.engine, self.config)
        win.present()
