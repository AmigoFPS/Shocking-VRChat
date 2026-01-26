"""
Shocking VRChat GUI Application
Design Style: Nothing Phone (minimalist, monochrome with dot accents)
Full replacement for CMD application - runs server internally
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import yaml
import os
import sys
import socket
import uuid
import qrcode
from PIL import Image, ImageTk
from io import BytesIO
import threading
import webbrowser
from datetime import datetime
import queue
import asyncio

# Constants
CONFIG_FILE_VERSION = 'v0.2'
CONFIG_FILENAME = f'settings-advanced-{CONFIG_FILE_VERSION}.yaml'
CONFIG_FILENAME_BASIC = f'settings-{CONFIG_FILE_VERSION}.yaml'

# Default Settings
SETTINGS_BASIC_DEFAULT = {
    'dglab3': {
        'channel_a': {
            'avatar_params': [
                '/avatar/parameters/pcs/contact/enterPass',
                '/avatar/parameters/TouchAreaA',
                '/avatar/parameters/TouchAreaB',
                '/avatar/parameters/wildcard/*',
            ],
            'mode': 'distance',
            'strength_limit': 100,      # Pattern power multiplier (0-100)
            'device_power_limit': 100,  # Hardware device limit (0-200)
            'power_settings_enabled': True,
        },
        'channel_b': {
            'avatar_params': [
                '/avatar/parameters/pcs/contact/enterPass',
                '/avatar/parameters/lms-penis-proximityA*',
                '/avatar/parameters/TouchAreaC',
                '/avatar/parameters/TouchAreaD',
            ],
            'mode': 'distance',
            'strength_limit': 100,      # Pattern power multiplier (0-100)
            'device_power_limit': 100,  # Hardware device limit (0-200)
            'power_settings_enabled': True,
        }
    },
    'version': CONFIG_FILE_VERSION,
}

SETTINGS_DEFAULT = {
    'SERVER_IP': None,
    'dglab3': {
        'channel_a': {
            'mode_config': {
                'shock': {
                    'duration': 2,
                    'wave': '["0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464"]',
                },
                'distance': {
                    'freq_ms': 10,
                },
                'trigger_range': {
                    'bottom': 0.0,
                    'top': 1.0,
                },
                'touch': {
                    'freq_ms': 10,
                    'n_derivative': 1,
                    'derivative_params': [
                        {"top": 1, "bottom": 0},
                        {"top": 5, "bottom": 0},
                        {"top": 50, "bottom": 0},
                        {"top": 500, "bottom": 0},
                    ]
                },
            }
        },
        'channel_b': {
            'mode_config': {
                'shock': {
                    'duration': 2,
                    'wave': '["0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464"]',
                },
                'distance': {
                    'freq_ms': 10,
                },
                'trigger_range': {
                    'bottom': 0.0,
                    'top': 1.0,
                },
                'touch': {
                    'freq_ms': 10,
                    'n_derivative': 1,
                    'derivative_params': [
                        {"top": 1, "bottom": 0},
                        {"top": 5, "bottom": 0},
                        {"top": 50, "bottom": 0},
                        {"top": 500, "bottom": 0},
                    ]
                },
            }
        },
    },
    'ws': {
        'master_uuid': None,
        'listen_host': '0.0.0.0',
        'listen_port': 28846
    },
    'osc': {
        'listen_host': '127.0.0.1',
        'listen_port': 9001,
    },
    'web_server': {
        'listen_host': '127.0.0.1',
        'listen_port': 8800
    },
    'log_level': 'INFO',
    'version': CONFIG_FILE_VERSION,
    'general': {
        'auto_open_qr_web_page': False,
        'local_ip_detect': {
            'host': '223.5.5.5',
            'port': 80,
        }
    }
}


class NothingPhoneStyle:
    """Nothing Phone inspired color palette and styling"""
    # Colors
    BG_PRIMARY = "#0A0A0A"
    BG_SECONDARY = "#141414"
    BG_TERTIARY = "#1E1E1E"
    
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#808080"
    TEXT_MUTED = "#4A4A4A"
    
    ACCENT_RED = "#FF3B30"
    ACCENT_ORANGE = "#FF6B35"
    ACCENT_DOT = "#FF3B30"
    
    # Gradient colors for power slider
    GRADIENT_LOW = "#00FF7F"      # Green
    GRADIENT_MID = "#FFD700"      # Yellow
    GRADIENT_HIGH = "#FF6B35"     # Orange
    GRADIENT_MAX = "#FF3B30"      # Red
    
    # Log colors
    LOG_INFO = "#00BFFF"
    LOG_SUCCESS = "#00FF7F"
    LOG_WARNING = "#FFD700"
    LOG_ERROR = "#FF3B30"
    
    BORDER_COLOR = "#2A2A2A"
    BORDER_ACTIVE = "#FF3B30"
    
    @staticmethod
    def get_gradient_color(progress):
        """Get color from gradient based on progress (0.0 to 1.0)"""
        if progress <= 0.33:
            # Green to Yellow
            t = progress / 0.33
            r = int(0 + t * 255)
            g = int(255 - t * 40)
            b = int(127 - t * 127)
        elif progress <= 0.66:
            # Yellow to Orange
            t = (progress - 0.33) / 0.33
            r = 255
            g = int(215 - t * 108)
            b = int(0 + t * 53)
        else:
            # Orange to Red
            t = (progress - 0.66) / 0.34
            r = 255
            g = int(107 - t * 48)
            b = int(53 - t * 5)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def get_scaled_fonts(scale=1.0):
        """Get fonts scaled by factor"""
        base_title = int(24 * scale)
        base_heading = int(14 * scale)
        base_body = int(11 * scale)
        base_small = int(9 * scale)
        base_mono = int(10 * scale)
        
        return {
            'title': ("Segoe UI", max(16, base_title), "bold"),
            'heading': ("Segoe UI", max(11, base_heading), "bold"),
            'body': ("Segoe UI", max(9, base_body)),
            'small': ("Segoe UI", max(8, base_small)),
            'mono': ("Consolas", max(9, base_mono)),
        }


class LogHandler:
    """Custom log handler that outputs to GUI"""
    
    def __init__(self):
        self.log_queue = queue.Queue()
        self.callbacks = []
    
    def add_callback(self, callback):
        self.callbacks.append(callback)
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level.upper(),
            'message': message
        }
        self.log_queue.put(log_entry)
        for callback in self.callbacks:
            try:
                callback(log_entry)
            except:
                pass
    
    def info(self, message):
        self.log("INFO", message)
    
    def success(self, message):
        self.log("SUCCESS", message)
    
    def warning(self, message):
        self.log("WARNING", message)
    
    def error(self, message):
        self.log("ERROR", message)


class ModernScrollbar(tk.Canvas):
    """Custom modern scrollbar implementation using Canvas"""
    
    def __init__(self, master, command=None, orient=tk.VERTICAL, **kwargs):
        # Set default colors matching the theme
        self.bg_color = kwargs.pop('bg', NothingPhoneStyle.BG_SECONDARY)
        self.trough_color = kwargs.pop('trough_color', NothingPhoneStyle.BG_SECONDARY)
        self.thumb_color = kwargs.pop('thumb_color', NothingPhoneStyle.BG_TERTIARY)
        self.thumb_active_color = kwargs.pop('active_color', NothingPhoneStyle.ACCENT_RED)
        
        # Dimensions
        width = kwargs.pop('width', 10) if orient == tk.VERTICAL else None
        height = kwargs.pop('height', 10) if orient == tk.HORIZONTAL else None
        
        super().__init__(master, width=width, height=height, bg=self.bg_color, highlightthickness=0, **kwargs)
        
        self.command = command
        self.orient = orient
        
        # State
        self.thumb_rect = None
        self.start_pos = None
        self.start_pixel = 0
        self.top = 0.0
        self.bottom = 1.0
        
        # Bind events
        self.bind('<Configure>', self._draw_thumb)
        self.bind('<Button-1>', self._on_press)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def set(self, lo, hi):
        """Set the scrollbar position (called by the scrollable widget)"""
        f_lo = float(lo)
        f_hi = float(hi)
        
        if f_lo <= 0.0 and f_hi >= 1.0:
            # Content fits entirely, hide thumb sometimes? For now just show full
            pass
            
        self.top = f_lo
        self.bottom = f_hi
        self._draw_thumb()
    
    def _draw_thumb(self, event=None):
        self.delete('all')
        
        w = self.winfo_width()
        h = self.winfo_height()
        
        if self.orient == tk.VERTICAL:
            # Draw trough (optional, can just be background)
            self.create_rectangle(0, 0, w, h, fill=self.trough_color, outline="")
            
            # Calculate thumb geometry
            full_height = h
            thumb_height = max(20, (self.bottom - self.top) * full_height)
            start_y = self.top * full_height
            
            # Draw thumb
            self.thumb_rect = self.create_rectangle(
                2, start_y, w-2, start_y + thumb_height,
                fill=self.thumb_color, outline="", tags="thumb"
            )
        else:
            # Horizontal
            self.create_rectangle(0, 0, w, h, fill=self.trough_color, outline="")
            
            full_width = w
            thumb_width = max(20, (self.bottom - self.top) * full_width)
            start_x = self.top * full_width
            
            self.thumb_rect = self.create_rectangle(
                start_x, 2, start_x + thumb_width, h-2,
                fill=self.thumb_color, outline="", tags="thumb"
            )
    
    def _on_press(self, event):
        self.start_pos = (event.x, event.y)
        
        if self.orient == tk.VERTICAL:
            thumb_coords = self.coords("thumb")
            if not thumb_coords: return
            
            # Check if clicked on thumb
            if thumb_coords[1] <= event.y <= thumb_coords[3]:
                self.start_pixel = event.y
                self.start_top = self.top
                self.itemconfig("thumb", fill=self.thumb_active_color)
            else:
                # Page jump behavior could be implemented here
                pass
        else:
            thumb_coords = self.coords("thumb")
            if not thumb_coords: return
            
            if thumb_coords[0] <= event.x <= thumb_coords[2]:
                self.start_pixel = event.x
                self.start_top = self.top
                self.itemconfig("thumb", fill=self.thumb_active_color)
    
    def _on_drag(self, event):
        if self.start_pos is None:
            return
            
        if self.orient == tk.VERTICAL:
            h = self.winfo_height()
            pixel_range = h * (1.0 - (self.bottom - self.top))
            if pixel_range <= 0: return
            
            delta_pixels = event.y - self.start_pixel
            delta_scale = delta_pixels / h
            
            new_top = self.start_top + delta_scale
            if self.command:
                self.command('moveto', new_top)
        else:
            w = self.winfo_width()
            # Simplified horizontal drag logic
            delta_pixels = event.x - self.start_pixel
            delta_scale = delta_pixels / w
            
            new_top = self.start_top + delta_scale
            if self.command:
                self.command('moveto', new_top)
    
    def _on_enter(self, event):
        self.itemconfig("thumb", fill=NothingPhoneStyle.TEXT_SECONDARY)
        
    def _on_leave(self, event):
        self.itemconfig("thumb", fill=self.thumb_color)


# Global logger
gui_logger = LogHandler()


class PowerSlider(tk.Frame):
    """Custom power slider with gradient and arrow controls"""
    
    def __init__(self, parent, label, channel, min_val=0, max_val=200, initial=100, 
                 callback=None, test_shock_callback=None, fonts=None, compact=False):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.channel = channel
        self.min_val = min_val
        self.max_val = max_val
        self.callback = callback
        self.test_shock_callback = test_shock_callback
        self.value = tk.IntVar(value=initial)
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.compact = compact
        
        self._create_widgets(label)
        
    def _create_widgets(self, label):
        pad_y = (8, 5) if self.compact else (15, 10)
        pad_x = 10 if self.compact else 15
        
        # Header with label and value
        header = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=pad_x, pady=pad_y)
        
        # Channel indicator dot
        self.dot_canvas = tk.Canvas(header, width=10, height=10, 
                                    bg=NothingPhoneStyle.BG_SECONDARY, 
                                    highlightthickness=0)
        self.dot_canvas.pack(side=tk.LEFT, padx=(0, 8))
        self._update_dot_color()
        
        label_widget = tk.Label(header, text=label,
                                font=self.fonts['heading'],
                                bg=NothingPhoneStyle.BG_SECONDARY,
                                fg=NothingPhoneStyle.TEXT_PRIMARY)
        label_widget.pack(side=tk.LEFT)
        
        # Value display with max indicator
        value_frame = tk.Frame(header, bg=NothingPhoneStyle.BG_SECONDARY)
        value_frame.pack(side=tk.RIGHT)
        
        self.value_label = tk.Label(value_frame, textvariable=self.value,
                                    font=self.fonts['heading'],
                                    bg=NothingPhoneStyle.BG_SECONDARY,
                                    fg=NothingPhoneStyle.ACCENT_RED,
                                    width=4)
        self.value_label.pack(side=tk.LEFT)
        
        max_label = tk.Label(value_frame, text=f"/{self.max_val}",
                             font=self.fonts['small'],
                             bg=NothingPhoneStyle.BG_SECONDARY,
                             fg=NothingPhoneStyle.TEXT_MUTED)
        max_label.pack(side=tk.LEFT)
        
        # Controls frame
        controls = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        controls.pack(fill=tk.X, padx=pad_x, pady=(0, 5 if self.compact else 10))
        
        # Left arrow button
        self.btn_left = tk.Button(controls, text="◀",
                                  font=self.fonts['body'],
                                  bg=NothingPhoneStyle.BG_TERTIARY,
                                  fg=NothingPhoneStyle.TEXT_PRIMARY,
                                  activebackground=NothingPhoneStyle.ACCENT_RED,
                                  activeforeground=NothingPhoneStyle.TEXT_PRIMARY,
                                  bd=0, width=3, height=1,
                                  cursor="hand2",
                                  command=self._decrease)
        self.btn_left.pack(side=tk.LEFT, padx=(0, 5))
        
        # Slider frame
        slider_frame = tk.Frame(controls, bg=NothingPhoneStyle.BG_SECONDARY)
        slider_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        slider_height = 24 if self.compact else 30
        self.slider_canvas = tk.Canvas(slider_frame, height=slider_height,
                                       bg=NothingPhoneStyle.BG_SECONDARY,
                                       highlightthickness=0)
        self.slider_canvas.pack(fill=tk.X, expand=True)
        self.slider_canvas.bind("<Configure>", self._draw_slider)
        self.slider_canvas.bind("<Button-1>", self._on_click)
        self.slider_canvas.bind("<B1-Motion>", self._on_drag)
        
        # Right arrow button
        self.btn_right = tk.Button(controls, text="▶",
                                   font=self.fonts['body'],
                                   bg=NothingPhoneStyle.BG_TERTIARY,
                                   fg=NothingPhoneStyle.TEXT_PRIMARY,
                                   activebackground=NothingPhoneStyle.ACCENT_RED,
                                   activeforeground=NothingPhoneStyle.TEXT_PRIMARY,
                                   bd=0, width=3, height=1,
                                   cursor="hand2",
                                   command=self._increase)
        self.btn_right.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Fine control buttons
        fine_controls = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        fine_controls.pack(fill=tk.X, padx=pad_x, pady=(0, 8 if self.compact else 15))
        
        btn_width = 4 if self.compact else 5
        
        btn_minus10 = tk.Button(fine_controls, text="-10",
                                font=self.fonts['small'],
                                bg=NothingPhoneStyle.BG_TERTIARY,
                                fg=NothingPhoneStyle.TEXT_SECONDARY,
                                activebackground=NothingPhoneStyle.ACCENT_RED,
                                bd=0, width=btn_width,
                                cursor="hand2",
                                command=lambda: self._adjust(-10))
        btn_minus10.pack(side=tk.LEFT, padx=1)
        
        btn_minus5 = tk.Button(fine_controls, text="-5",
                               font=self.fonts['small'],
                               bg=NothingPhoneStyle.BG_TERTIARY,
                               fg=NothingPhoneStyle.TEXT_SECONDARY,
                               activebackground=NothingPhoneStyle.ACCENT_RED,
                               bd=0, width=btn_width,
                               cursor="hand2",
                               command=lambda: self._adjust(-5))
        btn_minus5.pack(side=tk.LEFT, padx=1)
        
        btn_reset = tk.Button(fine_controls, text="RESET",
                              font=self.fonts['small'],
                              bg=NothingPhoneStyle.BG_TERTIARY,
                              fg=NothingPhoneStyle.TEXT_SECONDARY,
                              activebackground=NothingPhoneStyle.ACCENT_RED,
                              bd=0, width=6,
                              cursor="hand2",
                              command=lambda: self._set_value(100))
        btn_reset.pack(side=tk.LEFT, padx=1, expand=True)
        
        btn_plus5 = tk.Button(fine_controls, text="+5",
                              font=self.fonts['small'],
                              bg=NothingPhoneStyle.BG_TERTIARY,
                              fg=NothingPhoneStyle.TEXT_SECONDARY,
                              activebackground=NothingPhoneStyle.ACCENT_RED,
                              bd=0, width=btn_width,
                              cursor="hand2",
                              command=lambda: self._adjust(5))
        btn_plus5.pack(side=tk.RIGHT, padx=1)
        
        btn_plus10 = tk.Button(fine_controls, text="+10",
                               font=self.fonts['small'],
                               bg=NothingPhoneStyle.BG_TERTIARY,
                               fg=NothingPhoneStyle.TEXT_SECONDARY,
                               activebackground=NothingPhoneStyle.ACCENT_RED,
                               bd=0, width=btn_width,
                               cursor="hand2",
                               command=lambda: self._adjust(10))
        btn_plus10.pack(side=tk.RIGHT, padx=1)
        
        # Test shock button
        self.btn_test = tk.Button(fine_controls, text="⚡ TEST",
                                  font=self.fonts['small'],
                                  bg=NothingPhoneStyle.ACCENT_RED,
                                  fg=NothingPhoneStyle.TEXT_PRIMARY,
                                  activebackground=NothingPhoneStyle.ACCENT_ORANGE,
                                  bd=0, width=7,
                                  cursor="hand2",
                                  command=self._test_shock)
        self.btn_test.pack(side=tk.RIGHT, padx=(0, 5))
    
    def _update_dot_color(self):
        """Update dot color based on value"""
        self.dot_canvas.delete("all")
        progress = (self.value.get() - self.min_val) / (self.max_val - self.min_val)
        color = NothingPhoneStyle.get_gradient_color(progress)
        self.dot_canvas.create_oval(2, 2, 8, 8, fill=color, outline="")
    
    def _draw_slider(self, event=None):
        self.slider_canvas.delete("all")
        width = self.slider_canvas.winfo_width()
        height = self.slider_canvas.winfo_height()
        
        if width <= 1:
            return
        
        track_y = height // 2
        track_height = 6
        margin = 10
        track_width = width - 2 * margin
        
        # Draw gradient track background
        self.slider_canvas.create_rectangle(
            margin, track_y - track_height//2,
            width - margin, track_y + track_height//2,
            fill=NothingPhoneStyle.BG_TERTIARY,
            outline=""
        )
        
        # Calculate progress
        progress = (self.value.get() - self.min_val) / (self.max_val - self.min_val)
        active_width = int(track_width * progress)
        
        # Draw gradient filled portion
        if active_width > 0:
            # Draw gradient segments
            num_segments = max(1, active_width // 2)
            for i in range(num_segments):
                seg_progress = i / max(1, num_segments - 1) * progress
                seg_color = NothingPhoneStyle.get_gradient_color(seg_progress)
                x1 = margin + (i * active_width // num_segments)
                x2 = margin + ((i + 1) * active_width // num_segments)
                self.slider_canvas.create_rectangle(
                    x1, track_y - track_height//2,
                    x2, track_y + track_height//2,
                    fill=seg_color,
                    outline=""
                )
        
        # Get current color for thumb
        current_color = NothingPhoneStyle.get_gradient_color(progress)
        
        # Update value label color
        self.value_label.configure(fg=current_color)
        
        # Draw thumb
        thumb_x = margin + active_width
        thumb_radius = 8
        self.slider_canvas.create_oval(
            thumb_x - thumb_radius, track_y - thumb_radius,
            thumb_x + thumb_radius, track_y + thumb_radius,
            fill=NothingPhoneStyle.TEXT_PRIMARY,
            outline=current_color,
            width=2
        )
        
        # Update dot color
        self._update_dot_color()
    
    def _on_click(self, event):
        self._update_from_pos(event.x)
    
    def _on_drag(self, event):
        self._update_from_pos(event.x)
    
    def _update_from_pos(self, x):
        width = self.slider_canvas.winfo_width()
        margin = 10
        progress = (x - margin) / (width - 2 * margin)
        progress = max(0, min(1, progress))
        value = int(self.min_val + progress * (self.max_val - self.min_val))
        self._set_value(value)
    
    def _increase(self):
        self._adjust(1)
    
    def _decrease(self):
        self._adjust(-1)
    
    def _adjust(self, delta):
        new_value = self.value.get() + delta
        self._set_value(new_value)
    
    def _set_value(self, value):
        value = max(self.min_val, min(self.max_val, value))
        self.value.set(value)
        self._draw_slider()
        if self.callback:
            self.callback(self.channel, value)
    
    def get_value(self):
        return self.value.get()
    
    def _test_shock(self):
        """Send test shock signal"""
        if self.test_shock_callback:
            self.test_shock_callback(self.channel)
    
    def set_test_callback(self, callback):
        """Set test shock callback after initialization"""
        self.test_shock_callback = callback
    
    def set_value(self, value):
        self._set_value(value)


class QRCodePanel(tk.Frame):
    """QR Code display panel"""
    
    def __init__(self, parent, fonts=None, size=200):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.size = size
        self.qr_image = None
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self._create_widgets()
    
    def _create_widgets(self):
        # Title
        title_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        dot_canvas = tk.Canvas(title_frame, width=10, height=10,
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               highlightthickness=0)
        dot_canvas.pack(side=tk.LEFT, padx=(0, 8))
        dot_canvas.create_oval(2, 2, 8, 8, fill=NothingPhoneStyle.ACCENT_RED, outline="")
        
        title = tk.Label(title_frame, text="CONNECTION QR",
                         font=self.fonts['heading'],
                         bg=NothingPhoneStyle.BG_SECONDARY,
                         fg=NothingPhoneStyle.TEXT_PRIMARY)
        title.pack(side=tk.LEFT)
        
        # Copy button
        self.btn_copy = tk.Button(title_frame, text="📋",
                                  font=self.fonts['small'],
                                  bg=NothingPhoneStyle.BG_TERTIARY,
                                  fg=NothingPhoneStyle.TEXT_SECONDARY,
                                  activebackground=NothingPhoneStyle.ACCENT_RED,
                                  bd=0, width=3,
                                  cursor="hand2")
        self.btn_copy.pack(side=tk.RIGHT)
        
        # QR Code container
        qr_container = tk.Frame(self, bg=NothingPhoneStyle.BG_PRIMARY, padx=2, pady=2)
        qr_container.pack(padx=10, pady=5)
        
        self.qr_label = tk.Label(qr_container, bg=NothingPhoneStyle.TEXT_PRIMARY)
        self.qr_label.pack()
        
        # Status text
        self.status_label = tk.Label(self, text="Scan to connect device",
                                     font=self.fonts['small'],
                                     bg=NothingPhoneStyle.BG_SECONDARY,
                                     fg=NothingPhoneStyle.TEXT_SECONDARY)
        self.status_label.pack(pady=(3, 10))
    
    def set_copy_command(self, command):
        self.btn_copy.configure(command=command)
    
    def update_qr(self, data):
        """Generate and display QR code from data"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=2,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((self.size, self.size), Image.Resampling.NEAREST)
            
            self.qr_image = ImageTk.PhotoImage(img)
            self.qr_label.configure(image=self.qr_image)
            self.status_label.configure(text="Scan to connect device",
                                        fg=NothingPhoneStyle.TEXT_SECONDARY)
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}",
                                        fg=NothingPhoneStyle.ACCENT_RED)
    
    def set_placeholder(self):
        """Show placeholder when no QR data available"""
        placeholder = Image.new('RGB', (self.size, self.size), color='#2A2A2A')
        self.qr_image = ImageTk.PhotoImage(placeholder)
        self.qr_label.configure(image=self.qr_image)
        self.status_label.configure(text="Waiting for configuration...",
                                    fg=NothingPhoneStyle.TEXT_MUTED)
    
    def resize(self, new_size):
        self.size = new_size


class SystemLogsPanel(tk.Frame):
    """System logs panel"""
    
    def __init__(self, parent, fonts=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.max_logs = 200
        self._create_widgets()
        
        gui_logger.add_callback(self._on_log)
    
    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        dot_canvas = tk.Canvas(header, width=10, height=10,
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               highlightthickness=0)
        dot_canvas.pack(side=tk.LEFT, padx=(0, 8))
        dot_canvas.create_oval(2, 2, 8, 8, fill=NothingPhoneStyle.ACCENT_RED, outline="")
        
        title = tk.Label(header, text="SYSTEM LOGS",
                         font=self.fonts['heading'],
                         bg=NothingPhoneStyle.BG_SECONDARY,
                         fg=NothingPhoneStyle.TEXT_PRIMARY)
        title.pack(side=tk.LEFT)
        
        btn_clear = tk.Button(header, text="CLEAR",
                              font=self.fonts['small'],
                              bg=NothingPhoneStyle.BG_TERTIARY,
                              fg=NothingPhoneStyle.TEXT_SECONDARY,
                              activebackground=NothingPhoneStyle.ACCENT_RED,
                              bd=0, width=6,
                              cursor="hand2",
                              command=self._clear_logs)
        btn_clear.pack(side=tk.RIGHT)
        
        # Log container
        log_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_TERTIARY)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.log_text = tk.Text(log_frame,
                                font=self.fonts['mono'],
                                bg=NothingPhoneStyle.BG_TERTIARY,
                                fg=NothingPhoneStyle.TEXT_PRIMARY,
                                insertbackground=NothingPhoneStyle.ACCENT_RED,
                                wrap=tk.WORD,
                                bd=0,
                                padx=8,
                                pady=8,
                                state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Custom Scrollbar
        scrollbar = ModernScrollbar(log_frame, orient=tk.VERTICAL,
                                   command=self.log_text.yview,
                                   bg=NothingPhoneStyle.BG_TERTIARY,
                                   trough_color=NothingPhoneStyle.BG_TERTIARY,
                                   thumb_color=NothingPhoneStyle.BORDER_COLOR,
                                   active_color=NothingPhoneStyle.ACCENT_RED,
                                   width=12)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.tag_configure("INFO", foreground=NothingPhoneStyle.LOG_INFO)
        self.log_text.tag_configure("SUCCESS", foreground=NothingPhoneStyle.LOG_SUCCESS)
        self.log_text.tag_configure("WARNING", foreground=NothingPhoneStyle.LOG_WARNING)
        self.log_text.tag_configure("ERROR", foreground=NothingPhoneStyle.LOG_ERROR)
        self.log_text.tag_configure("TIME", foreground=NothingPhoneStyle.TEXT_MUTED)
    
    def _on_log(self, log_entry):
        """Handle new log entry"""
        try:
            self.log_text.configure(state=tk.NORMAL)
            
            self.log_text.insert(tk.END, f"[{log_entry['timestamp']}] ", "TIME")
            self.log_text.insert(tk.END, f"[{log_entry['level']}] ", log_entry['level'])
            self.log_text.insert(tk.END, f"{log_entry['message']}\n")
            
            self.log_text.see(tk.END)
            
            lines = int(self.log_text.index('end-1c').split('.')[0])
            if lines > self.max_logs:
                self.log_text.delete('1.0', f'{lines - self.max_logs}.0')
            
            self.log_text.configure(state=tk.DISABLED)
        except:
            pass
    
    def _clear_logs(self):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state=tk.DISABLED)
        gui_logger.info("Logs cleared")



class TooltipIcon(tk.Canvas):
    """Modern question mark icon that shows tooltip on hover - Nothing Phone style"""
    
    def __init__(self, parent, tooltip_text, fonts=None, bg_color=None):
        self.bg_color = bg_color or NothingPhoneStyle.BG_SECONDARY
        super().__init__(parent, width=18, height=18, bg=self.bg_color, highlightthickness=0)
        self.tooltip_text = tooltip_text
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.tooltip_window = None
        
        # Draw circle with question mark
        self._draw_icon(False)
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._toggle_tooltip)
    
    def _draw_icon(self, hovered=False):
        self.delete("all")
        # Circle background
        fill_color = NothingPhoneStyle.ACCENT_RED if hovered else NothingPhoneStyle.BG_TERTIARY
        outline_color = NothingPhoneStyle.ACCENT_RED if hovered else NothingPhoneStyle.TEXT_MUTED
        text_color = NothingPhoneStyle.TEXT_PRIMARY if hovered else NothingPhoneStyle.TEXT_SECONDARY
        
        self.create_oval(2, 2, 16, 16, fill=fill_color, outline=outline_color, width=1)
        self.create_text(9, 9, text="?", font=("Segoe UI", 8, "bold"), fill=text_color)
        self.configure(cursor="hand2")
    
    def _on_enter(self, event=None):
        self._draw_icon(True)
        self._show_tooltip()
    
    def _on_leave(self, event=None):
        self._draw_icon(False)
        self._hide_tooltip()
    
    def _show_tooltip(self, event=None):
        if self.tooltip_window:
            return
            
        x = self.winfo_rootx() + 25
        y = self.winfo_rooty() - 10
        
        self.tooltip_window = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes('-topmost', True)
        
        # Tooltip frame with accent border
        frame = tk.Frame(tw, bg=NothingPhoneStyle.ACCENT_RED, padx=1, pady=1)
        frame.pack()
        
        inner = tk.Frame(frame, bg=NothingPhoneStyle.BG_PRIMARY, padx=12, pady=8)
        inner.pack()
        
        label = tk.Label(inner, text=self.tooltip_text,
                        font=self.fonts['small'],
                        bg=NothingPhoneStyle.BG_PRIMARY,
                        fg=NothingPhoneStyle.TEXT_PRIMARY,
                        justify=tk.LEFT,
                        wraplength=280)
        label.pack()
    
    def _hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def _toggle_tooltip(self, event=None):
        if self.tooltip_window:
            self._hide_tooltip()
        else:
            self._show_tooltip()


class ModernToggle(tk.Canvas):
    """Nothing Phone inspired toggle switch"""
    def __init__(self, parent, variable, command=None, fonts=None):
        super().__init__(parent, width=44, height=22, bg=NothingPhoneStyle.BG_SECONDARY, highlightthickness=0)
        self.variable = variable
        self.command = command
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        
        self.bind("<Button-1>", self._toggle)
        self._draw()
        
    def _draw(self):
        self.delete("all")
        is_on = self.variable.get()
        
        # Colors
        bg_color = NothingPhoneStyle.ACCENT_RED if is_on else NothingPhoneStyle.BG_TERTIARY
        toggle_color = NothingPhoneStyle.TEXT_PRIMARY
        
        # Background pill
        self.create_rounded_rect(2, 2, 42, 20, radius=9, fill=bg_color, outline="")
        
        # Circle handle
        x_pos = 32 if is_on else 12
        self.create_oval(x_pos-7, 5, x_pos+7, 17, fill=toggle_color, outline="")
        
        # Text state (ON/OFF)
        state_text = "ON" if is_on else "OFF"
        self.create_text(23, 32, text=state_text, font=self.fonts['small'], 
                         fill=NothingPhoneStyle.TEXT_SECONDARY)
        
        self.configure(cursor="hand2")

    def create_rounded_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _toggle(self, event=None):
        self.variable.set(not self.variable.get())
        self._draw()
        if self.command:
            self.command()


class ConfigSlider(tk.Frame):
    """Custom styled slider matching Nothing Phone aesthetic"""
    
    def __init__(self, parent, label, attr_name, min_val=0, max_val=100, 
                 initial=50, tooltip=None, fonts=None, on_change=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.min_val = min_val
        self.max_val = max_val
        self.attr_name = attr_name
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.on_change = on_change
        self.value = tk.DoubleVar(value=initial)
        
        self._create_widgets(label, tooltip)
    
    def _create_widgets(self, label, tooltip):
        # Main row
        row = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        row.pack(fill=tk.X, padx=10, pady=6)
        
        # Left side: label + tooltip
        left = tk.Frame(row, bg=NothingPhoneStyle.BG_SECONDARY)
        left.pack(side=tk.LEFT)
        
        lbl = tk.Label(left, text=label, font=self.fonts['body'],
                      bg=NothingPhoneStyle.BG_SECONDARY,
                      fg=NothingPhoneStyle.TEXT_SECONDARY,
                      width=14, anchor=tk.W)
        lbl.pack(side=tk.LEFT)
        
        if tooltip:
            tip = TooltipIcon(left, tooltip, self.fonts, NothingPhoneStyle.BG_SECONDARY)
            tip.pack(side=tk.LEFT, padx=(4, 0))
        
        # Right side: value display
        right = tk.Frame(row, bg=NothingPhoneStyle.BG_SECONDARY)
        right.pack(side=tk.RIGHT)
        
        self.value_label = tk.Label(right, text=str(int(self.value.get())),
                                    font=self.fonts['heading'],
                                    bg=NothingPhoneStyle.BG_SECONDARY,
                                    fg=NothingPhoneStyle.ACCENT_RED,
                                    width=4)
        self.value_label.pack(side=tk.LEFT)
        
        max_lbl = tk.Label(right, text=f"/{self.max_val}",
                          font=self.fonts['small'],
                          bg=NothingPhoneStyle.BG_SECONDARY,
                          fg=NothingPhoneStyle.TEXT_MUTED)
        max_lbl.pack(side=tk.LEFT)
        
        # Slider row
        slider_row = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        slider_row.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        # Custom canvas slider
        self.slider_canvas = tk.Canvas(slider_row, height=20,
                                       bg=NothingPhoneStyle.BG_SECONDARY,
                                       highlightthickness=0)
        self.slider_canvas.pack(fill=tk.X, expand=True)
        self.slider_canvas.bind("<Configure>", self._draw_slider)
        self.slider_canvas.bind("<Button-1>", self._on_click)
        self.slider_canvas.bind("<B1-Motion>", self._on_drag)
    
    def _draw_slider(self, event=None):
        self.slider_canvas.delete("all")
        width = self.slider_canvas.winfo_width()
        height = self.slider_canvas.winfo_height()
        
        if width <= 1:
            return
        
        track_y = height // 2
        track_height = 4
        margin = 8
        track_width = width - 2 * margin
        
        # Background track
        self.slider_canvas.create_rectangle(
            margin, track_y - track_height//2,
            width - margin, track_y + track_height//2,
            fill=NothingPhoneStyle.BG_TERTIARY,
            outline=""
        )
        
        # Progress calculation
        progress = (self.value.get() - self.min_val) / (self.max_val - self.min_val)
        active_width = int(track_width * progress)
        
        # Gradient fill
        if active_width > 0:
            color = NothingPhoneStyle.get_gradient_color(progress)
            self.slider_canvas.create_rectangle(
                margin, track_y - track_height//2,
                margin + active_width, track_y + track_height//2,
                fill=color,
                outline=""
            )
            self.value_label.configure(fg=color)
        
        # Thumb
        thumb_x = margin + active_width
        thumb_radius = 7
        current_color = NothingPhoneStyle.get_gradient_color(progress)
        
        self.slider_canvas.create_oval(
            thumb_x - thumb_radius, track_y - thumb_radius,
            thumb_x + thumb_radius, track_y + thumb_radius,
            fill=NothingPhoneStyle.TEXT_PRIMARY,
            outline=current_color,
            width=2
        )
    
    def _on_click(self, event):
        self._update_from_pos(event.x)
    
    def _on_drag(self, event):
        self._update_from_pos(event.x)
    
    def _update_from_pos(self, x):
        width = self.slider_canvas.winfo_width()
        margin = 8
        progress = (x - margin) / (width - 2 * margin)
        progress = max(0, min(1, progress))
        value = self.min_val + progress * (self.max_val - self.min_val)
        self.set_value(value)
    
    def set_value(self, value):
        value = max(self.min_val, min(self.max_val, value))
        self.value.set(value)
        self.value_label.configure(text=str(int(value)))
        self._draw_slider()
        if self.on_change:
            self.on_change(self.attr_name, value)
    
    def get_value(self):
        return self.value.get()


class ModeSelector(tk.Frame):
    """Modern mode selector buttons - Nothing Phone style"""
    
    def __init__(self, parent, modes, variable, tooltip=None, fonts=None, on_change=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.modes = modes
        self.variable = variable
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.on_change = on_change
        self.buttons = {}
        
        self._create_widgets(tooltip)
    
    def _create_widgets(self, tooltip):
        # Header row
        header = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=10, pady=(8, 5))
        
        lbl = tk.Label(header, text="MODE", font=self.fonts['small'],
                      bg=NothingPhoneStyle.BG_SECONDARY,
                      fg=NothingPhoneStyle.TEXT_MUTED)
        lbl.pack(side=tk.LEFT)
        
        if tooltip:
            tip = TooltipIcon(header, tooltip, self.fonts, NothingPhoneStyle.BG_SECONDARY)
            tip.pack(side=tk.LEFT, padx=(6, 0))
        
        # Buttons row
        btn_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        for text, val in self.modes:
            btn = tk.Button(btn_frame, text=text,
                           font=self.fonts['small'],
                           bg=NothingPhoneStyle.BG_TERTIARY,
                           fg=NothingPhoneStyle.TEXT_SECONDARY,
                           activebackground=NothingPhoneStyle.ACCENT_RED,
                           activeforeground=NothingPhoneStyle.TEXT_PRIMARY,
                           bd=0, padx=12, pady=6,
                           cursor="hand2",
                           command=lambda v=val: self._select(v))
            btn.pack(side=tk.LEFT, padx=(0, 4), expand=True, fill=tk.X)
            self.buttons[val] = btn
        
        # Initial selection
        self._update_buttons()
    
    def _select(self, value):
        self.variable.set(value)
        self._update_buttons()
        if self.on_change:
            self.on_change(value)
    
    def _update_buttons(self):
        current = self.variable.get()
        for val, btn in self.buttons.items():
            if val == current:
                btn.configure(bg=NothingPhoneStyle.ACCENT_RED,
                            fg=NothingPhoneStyle.TEXT_PRIMARY)
            else:
                btn.configure(bg=NothingPhoneStyle.BG_TERTIARY,
                            fg=NothingPhoneStyle.TEXT_SECONDARY)
    
    def refresh(self):
        self._update_buttons()


class PatternsPanel(tk.Frame):
    """Configuration panel for behavioral patterns - Nothing Phone style"""
    
    # Tooltip texts for each setting
    TOOLTIPS = {
        'device_power': "⚡ DEVICE POWER LIMIT\n\nHardware limit for DG-Lab device (0-200).\nLimits the maximum possible strength at the hardware level.\n\nRecommended: Start with 30-50 for safety.",
        'pattern_power': "📊 PATTERN MULTIPLIER\n\nSoftware pattern multiplier (0-100%).\nScales the intensity of the generated wave.\n\n100% means the pattern will use full available power defined by the device limit.",
        'mode': "🎮 OPERATION MODE\n\n• PROXIMITY — strength depends on distance to contact\n• IMPACT — strength depends on movement speed\n• RECOIL — strength depends on acceleration (jerk)",
        'sensitivity': "🎚️ SENSITIVITY\n\nDefines how strong the reaction is to input changes.\nHigher = stronger reaction to small changes.\n\nFor PROXIMITY: how fast the strength ramps up.\nFor IMPACT/RECOIL: speed/acceleration threshold.",
        'threshold': "🚫 ACTIVATION THRESHOLD\n\nMinimum value required to trigger a shock.\nFilters out accidental or weak signals.\n\nIncrease this if you experience false triggers.",
        'power_enabled': "🔌 POWER SETTINGS TOGGLE\n\nEnable or disable custom power management for this channel.\nIf disabled, default device behavior will be used.",
    }
    
    def __init__(self, parent, fonts=None, on_save_callback=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_PRIMARY)
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.on_save_callback = on_save_callback
        self.settings = None
        self.sliders = {}
        self.mode_selectors = {}
        self.power_vars = {}
        self._create_widgets()
    
    def _create_widgets(self):
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self, bg=NothingPhoneStyle.BG_PRIMARY, highlightthickness=0)
        self.scrollbar = ModernScrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview,
                                       bg=NothingPhoneStyle.BG_PRIMARY,
                                       trough_color=NothingPhoneStyle.BG_PRIMARY,
                                       thumb_color=NothingPhoneStyle.BORDER_COLOR,
                                       active_color=NothingPhoneStyle.ACCENT_RED,
                                       width=10)
        
        self.scroll_frame = tk.Frame(self.canvas, bg=NothingPhoneStyle.BG_PRIMARY)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mouse wheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scroll_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Configure>", self._on_frame_configure)

        # Content - Channel cards
        self._create_channel_card(self.scroll_frame, "CHANNEL A", "channel_a", NothingPhoneStyle.ACCENT_RED)
        self._create_channel_card(self.scroll_frame, "CHANNEL B", "channel_b", NothingPhoneStyle.ACCENT_ORANGE)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_frame_configure(self, event):
        # Update canvas window width
        self.canvas.itemconfig(self.canvas_window, width=event.width - 15)
        
    def _create_channel_card(self, parent, title, channel_key, accent_color):
        """Create a styled channel configuration card"""
        # Card container
        card = tk.Frame(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        card.pack(fill=tk.X, padx=8, pady=8)
        setattr(self, f"{channel_key}_card", card)
        
        # Card header with dot accent
        header = tk.Frame(card, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=12, pady=(12, 8))
        
        # Accent dot
        dot = tk.Canvas(header, width=12, height=12, bg=NothingPhoneStyle.BG_SECONDARY, highlightthickness=0)
        dot.pack(side=tk.LEFT, padx=(0, 10))
        dot.create_oval(2, 2, 10, 10, fill=accent_color, outline="")
        
        # Title
        lbl = tk.Label(header, text=title, font=self.fonts['heading'],
                      bg=NothingPhoneStyle.BG_SECONDARY,
                      fg=NothingPhoneStyle.TEXT_PRIMARY)
        lbl.pack(side=tk.LEFT)
        
        # Power settings toggle
        power_var = tk.BooleanVar(value=True)
        self.power_vars[channel_key] = power_var
        
        # Container for switch and label
        toggle_frame = tk.Frame(header, bg=NothingPhoneStyle.BG_SECONDARY)
        toggle_frame.pack(side=tk.RIGHT)
        
        status_lbl = tk.Label(toggle_frame, text="ENABLED", font=self.fonts['small'],
                             bg=NothingPhoneStyle.BG_SECONDARY,
                             fg=NothingPhoneStyle.ACCENT_RED)
        status_lbl.pack(side=tk.LEFT, padx=(0, 8))
        setattr(self, f"{channel_key}_status_lbl", status_lbl)
        
        def on_toggle():
            is_enabled = power_var.get()
            status_lbl.configure(
                text="ENABLED" if is_enabled else "DISABLED",
                fg=NothingPhoneStyle.ACCENT_RED if is_enabled else NothingPhoneStyle.TEXT_MUTED
            )
            # Update visual state of sliders
            self._update_card_visual_state(channel_key)
            # Auto-save if needed or let the user click save
            
        toggle_btn = ModernToggle(toggle_frame, variable=power_var, 
                                 command=on_toggle, fonts=self.fonts)
        toggle_btn.pack(side=tk.LEFT)
        setattr(self, f"{channel_key}_toggle", toggle_btn)
        
        tip = TooltipIcon(header, self.TOOLTIPS['power_enabled'], self.fonts, NothingPhoneStyle.BG_SECONDARY)
        tip.pack(side=tk.RIGHT, padx=15)
        
        # Body frame (contains everything below header)
        body = tk.Frame(card, bg=NothingPhoneStyle.BG_SECONDARY)
        body.pack(fill=tk.X)
        setattr(self, f"{channel_key}_body", body)
        
        # Separator
        sep = tk.Frame(body, height=1, bg=NothingPhoneStyle.BORDER_COLOR)
        sep.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        # Power section header
        power_header = tk.Frame(body, bg=NothingPhoneStyle.BG_SECONDARY)
        power_header.pack(fill=tk.X, padx=12)
        
        tk.Label(power_header, text="⚡ POWER SETTINGS", font=self.fonts['small'],
                bg=NothingPhoneStyle.BG_SECONDARY,
                fg=NothingPhoneStyle.TEXT_MUTED).pack(side=tk.LEFT)
        
        # Device Power slider (0-200)
        device_slider = ConfigSlider(body, "Device Limit", f"{channel_key}_device_power",
                                     min_val=0, max_val=200, initial=100,
                                     tooltip=self.TOOLTIPS['device_power'],
                                     fonts=self.fonts)
        device_slider.pack(fill=tk.X)
        self.sliders[f"{channel_key}_device_power"] = device_slider
        
        # Pattern Power slider (0-100)
        pattern_slider = ConfigSlider(body, "Pattern Multi", f"{channel_key}_pattern_power",
                                      min_val=0, max_val=100, initial=100,
                                      tooltip=self.TOOLTIPS['pattern_power'],
                                      fonts=self.fonts)
        pattern_slider.pack(fill=tk.X)
        self.sliders[f"{channel_key}_pattern_power"] = pattern_slider
        
        # Separator
        sep2 = tk.Frame(body, height=1, bg=NothingPhoneStyle.BORDER_COLOR)
        sep2.pack(fill=tk.X, padx=12, pady=8)
        
        # Mode selector
        mode_var = tk.StringVar(value="distance")
        setattr(self, f"{channel_key}_mode", mode_var)
        
        modes = [
            ("PROXIMITY", "distance"),
            ("IMPACT", "touch_1"),
            ("RECOIL", "touch_2"),
        ]
        
        mode_selector = ModeSelector(body, modes, mode_var,
                                     tooltip=self.TOOLTIPS['mode'],
                                     fonts=self.fonts)
        mode_selector.pack(fill=tk.X)
        self.mode_selectors[channel_key] = mode_selector
        
        # Behavior section header
        behavior_header = tk.Frame(body, bg=NothingPhoneStyle.BG_SECONDARY)
        behavior_header.pack(fill=tk.X, padx=12, pady=(5, 0))
        
        tk.Label(behavior_header, text="🎚️ BEHAVIOR TUNING", font=self.fonts['small'],
                bg=NothingPhoneStyle.BG_SECONDARY,
                fg=NothingPhoneStyle.TEXT_MUTED).pack(side=tk.LEFT)
        
        # Sensitivity slider
        sens_slider = ConfigSlider(body, "Sensitivity", f"{channel_key}_sens",
                                   min_val=0, max_val=100, initial=50,
                                   tooltip=self.TOOLTIPS['sensitivity'],
                                   fonts=self.fonts)
        sens_slider.pack(fill=tk.X)
        self.sliders[f"{channel_key}_sens"] = sens_slider
        
        # Threshold slider  
        thresh_slider = ConfigSlider(body, "Threshold", f"{channel_key}_thresh",
                                     min_val=0, max_val=100, initial=0,
                                     tooltip=self.TOOLTIPS['threshold'],
                                     fonts=self.fonts)
        thresh_slider.pack(fill=tk.X)
        self.sliders[f"{channel_key}_thresh"] = thresh_slider
        
        # Bottom padding
        tk.Frame(body, bg=NothingPhoneStyle.BG_SECONDARY, height=8).pack(fill=tk.X)

    def _update_card_visual_state(self, channel_key):
        """Update opacity/visual state of channel card based on toggle"""
        is_enabled = self.power_vars[channel_key].get()
        body = getattr(self, f"{channel_key}_body")
        
        # There's no real opacity in tkinter, so we simulate by changing colors
        # or just dimming the contents. For now, let's just update the status label.
        status_lbl = getattr(self, f"{channel_key}_status_lbl")
        status_lbl.configure(
            text="ENABLED" if is_enabled else "DISABLED",
            fg=NothingPhoneStyle.ACCENT_RED if is_enabled else NothingPhoneStyle.TEXT_MUTED
        )
        
        # We can disable all children of the body
        def set_state(parent, state):
            for child in parent.winfo_children():
                try:
                    if 'state' in child.config():
                        child.configure(state=state)
                except:
                    pass
                set_state(child, state)
        
        # set_state(body, tk.NORMAL if is_enabled else tk.DISABLED)


    def load_settings(self, settings):
        self.settings = settings
        # Parse settings into UI
        # We need to map from the complex json to simple sliders
        
        for ch in ['channel_a', 'channel_b']:
            try:
                ch_conf = settings['dglab3'][ch]
                mode = ch_conf.get('mode', 'distance')
                
                # Default UI state
                ui_mode = "distance"
                sens = 50.0
                thresh = 0.0
                
                # Load power enabled toggle
                power_enabled = ch_conf.get('power_settings_enabled', True)
                if ch in self.power_vars:
                    self.power_vars[ch].set(power_enabled)
                
                # Load device power (hardware limit, 0-200)
                device_power = ch_conf.get('device_power_limit', 100)
                if f"{ch}_device_power" in self.sliders:
                    self.sliders[f"{ch}_device_power"].set_value(device_power)
                
                # Load pattern power (software multiplier, 0-100)
                pattern_power = ch_conf.get('strength_limit', 100)
                if f"{ch}_pattern_power" in self.sliders:
                    self.sliders[f"{ch}_pattern_power"].set_value(pattern_power)
                
                if mode == 'distance':
                    ui_mode = "distance"
                elif mode == 'touch':
                    conf = ch_conf.get('mode_config', {}).get('touch', {})
                    deriv = conf.get('n_derivative', 1)
                    if deriv == 1:
                        ui_mode = "touch_1"
                    else:
                        ui_mode = "touch_2"
                        
                    # Calculate sensitivity from derivative params
                    d_params_list = conf.get('derivative_params', [])
                    if len(d_params_list) > deriv:
                        d_params = d_params_list[deriv]
                        top = d_params.get('top', 10)
                        bottom = d_params.get('bottom', 0)
                        
                        sens = max(0, min(100, 100 - top))
                        thresh = bottom * 100
                
                # Set mode
                getattr(self, f"{ch}_mode").set(ui_mode)
                if ch in self.mode_selectors:
                    self.mode_selectors[ch].refresh()
                
                # Update visual state based on loaded power toggle
                self._update_card_visual_state(ch)
                if hasattr(self, f"{ch}_toggle"):
                    getattr(self, f"{ch}_toggle")._draw()
                
                # Set sliders
                if f"{ch}_sens" in self.sliders:
                    self.sliders[f"{ch}_sens"].set_value(sens)
                if f"{ch}_thresh" in self.sliders:
                    self.sliders[f"{ch}_thresh"].set_value(thresh)
                
            except Exception:
                pass

    def apply_settings(self):
        """Write UI values back to settings dict"""
        if not self.settings: return None
        
        for ch in ['channel_a', 'channel_b']:
            ui_mode = getattr(self, f"{ch}_mode").get()
            
            # Get values from sliders
            sens = self.sliders[f"{ch}_sens"].get_value() if f"{ch}_sens" in self.sliders else 50
            thresh = self.sliders[f"{ch}_thresh"].get_value() if f"{ch}_thresh" in self.sliders else 0
            device_power = int(self.sliders[f"{ch}_device_power"].get_value()) if f"{ch}_device_power" in self.sliders else 100
            pattern_power = int(self.sliders[f"{ch}_pattern_power"].get_value()) if f"{ch}_pattern_power" in self.sliders else 100
            power_enabled = self.power_vars[ch].get() if ch in self.power_vars else True
            
            ch_conf = self.settings['dglab3'][ch]
            
            # Save power settings
            ch_conf['power_settings_enabled'] = power_enabled
            ch_conf['device_power_limit'] = device_power  # Hardware limit (0-200)
            ch_conf['strength_limit'] = pattern_power     # Pattern multiplier (0-100)
            
            if ui_mode == "distance":
                ch_conf['mode'] = 'distance'
            elif ui_mode.startswith("touch"):
                ch_conf['mode'] = 'touch'
                n_deriv = 1 if ui_mode == "touch_1" else 2
                
                # Update touch config
                if 'mode_config' not in ch_conf: ch_conf['mode_config'] = {}
                if 'touch' not in ch_conf['mode_config']:
                    ch_conf['mode_config']['touch'] = {
                        'freq_ms': 10,
                        'n_derivative': n_deriv,
                        'derivative_params': [
                            {"top": 1, "bottom": 0},
                            {"top": 5, "bottom": 0},
                            {"top": 50, "bottom": 0},
                            {"top": 500, "bottom": 0},
                        ]
                    }
                
                touch_conf = ch_conf['mode_config']['touch']
                touch_conf['n_derivative'] = n_deriv
                
                # Map sensitivity back to 'top'
                top = max(0.1, 100 - sens)
                if n_deriv == 1:
                     top = top / 2 
                
                bottom = thresh / 100.0
                
                # Update the specific param index
                touch_conf['derivative_params'][n_deriv]['top'] = top
                touch_conf['derivative_params'][n_deriv]['bottom'] = bottom

        return self.settings

    def _on_mode_change(self, channel):
        pass


class ConfigEditor(tk.Frame):
    """Configuration editor with save button"""
    
    def __init__(self, parent, on_save_callback=None, fonts=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.on_save_callback = on_save_callback
        self.current_file = "basic"
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self._create_widgets()
    
    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        dot_canvas = tk.Canvas(header, width=10, height=10,
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               highlightthickness=0)
        dot_canvas.pack(side=tk.LEFT, padx=(0, 8))
        dot_canvas.create_oval(2, 2, 8, 8, fill=NothingPhoneStyle.ACCENT_RED, outline="")
        
        title = tk.Label(header, text="CONFIGURATION",
                         font=self.fonts['heading'],
                         bg=NothingPhoneStyle.BG_SECONDARY,
                         fg=NothingPhoneStyle.TEXT_PRIMARY)
        title.pack(side=tk.LEFT)
        
        # File selector and action buttons in same row
        toolbar = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        toolbar.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Left side - file selector
        selector = tk.Frame(toolbar, bg=NothingPhoneStyle.BG_SECONDARY)
        selector.pack(side=tk.LEFT)
        
        self.btn_basic = tk.Button(selector, text="BASIC",
                                   font=self.fonts['small'],
                                   bg=NothingPhoneStyle.ACCENT_RED,
                                   fg=NothingPhoneStyle.TEXT_PRIMARY,
                                   activebackground=NothingPhoneStyle.ACCENT_ORANGE,
                                   bd=0, width=8,
                                   cursor="hand2",
                                   command=lambda: self._switch_file("basic"))
        self.btn_basic.pack(side=tk.LEFT, padx=(0, 3))
        
        self.btn_advanced = tk.Button(selector, text="ADVANCED",
                                      font=self.fonts['small'],
                                      bg=NothingPhoneStyle.BG_TERTIARY,
                                      fg=NothingPhoneStyle.TEXT_SECONDARY,
                                      activebackground=NothingPhoneStyle.ACCENT_RED,
                                      bd=0, width=10,
                                      cursor="hand2",
                                      command=lambda: self._switch_file("advanced"))
        self.btn_advanced.pack(side=tk.LEFT, padx=(0, 3))

        self.btn_patterns = tk.Button(selector, text="PATTERNS",
                                      font=self.fonts['small'],
                                      bg=NothingPhoneStyle.BG_TERTIARY,
                                      fg=NothingPhoneStyle.TEXT_SECONDARY,
                                      activebackground=NothingPhoneStyle.ACCENT_RED,
                                      bd=0, width=10,
                                      cursor="hand2",
                                      command=lambda: self._switch_file("patterns"))
        self.btn_patterns.pack(side=tk.LEFT)
        
        # Right side - action buttons
        actions = tk.Frame(toolbar, bg=NothingPhoneStyle.BG_SECONDARY)
        actions.pack(side=tk.RIGHT)
        
        self.btn_reload = tk.Button(actions, text="↻",
                                    font=self.fonts['body'],
                                    bg=NothingPhoneStyle.BG_TERTIARY,
                                    fg=NothingPhoneStyle.TEXT_SECONDARY,
                                    activebackground=NothingPhoneStyle.ACCENT_RED,
                                    bd=0, width=3,
                                    cursor="hand2",
                                    command=self._reload_config)
        self.btn_reload.pack(side=tk.LEFT, padx=2)
        
        self.btn_save = tk.Button(actions, text="💾 SAVE",
                                  font=self.fonts['small'],
                                  bg=NothingPhoneStyle.ACCENT_RED,
                                  fg=NothingPhoneStyle.TEXT_PRIMARY,
                                  activebackground=NothingPhoneStyle.ACCENT_ORANGE,
                                  bd=0, width=8,
                                  cursor="hand2",
                                  command=self._save_config)
        self.btn_save.pack(side=tk.LEFT, padx=2)
        
        # Text editor
        editor_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_TERTIARY)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)
        
        # Create text widget with both scrollbars
        self.text_editor = tk.Text(
            editor_frame,
            font=self.fonts['mono'],
            bg=NothingPhoneStyle.BG_TERTIARY,
            fg=NothingPhoneStyle.TEXT_PRIMARY,
            insertbackground=NothingPhoneStyle.ACCENT_RED,
            selectbackground=NothingPhoneStyle.ACCENT_RED,
            selectforeground=NothingPhoneStyle.TEXT_PRIMARY,
            wrap=tk.NONE,
            bd=0,
            padx=8,
            pady=8
        )
        
        # Vertical scrollbar
        v_scroll = ModernScrollbar(editor_frame, orient=tk.VERTICAL,
                                 command=self.text_editor.yview,
                                 bg=NothingPhoneStyle.BG_TERTIARY,
                                 trough_color=NothingPhoneStyle.BG_TERTIARY,
                                 thumb_color=NothingPhoneStyle.BORDER_COLOR,
                                 active_color=NothingPhoneStyle.ACCENT_RED,
                                 width=12)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        h_scroll = ModernScrollbar(editor_frame, orient=tk.HORIZONTAL,
                                 command=self.text_editor.xview,
                                 bg=NothingPhoneStyle.BG_TERTIARY,
                                 trough_color=NothingPhoneStyle.BG_TERTIARY,
                                 thumb_color=NothingPhoneStyle.BORDER_COLOR,
                                 active_color=NothingPhoneStyle.ACCENT_RED,
                                 height=12)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.text_editor.configure(yscrollcommand=v_scroll.set,
                                   xscrollcommand=h_scroll.set)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Patterns Panel (Hidden by default)
        self.patterns_panel = PatternsPanel(editor_frame, fonts=self.fonts)
        # We don't pack it yet, we switch visibility
        
        # Status bar
        self.status_bar = tk.Label(self, text="Ready",
                                   font=self.fonts['small'],
                                   bg=NothingPhoneStyle.BG_SECONDARY,
                                   fg=NothingPhoneStyle.TEXT_MUTED,
                                   anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=10, pady=(3, 8))
    
    def _switch_file(self, file_type):
        self.current_file = file_type
        if file_type == "basic":
            self.btn_basic.configure(bg=NothingPhoneStyle.ACCENT_RED, fg=NothingPhoneStyle.TEXT_PRIMARY)
            self.btn_advanced.configure(bg=NothingPhoneStyle.BG_TERTIARY, fg=NothingPhoneStyle.TEXT_SECONDARY)
            self.btn_patterns.configure(bg=NothingPhoneStyle.BG_TERTIARY, fg=NothingPhoneStyle.TEXT_SECONDARY)
            self._show_editor()
        elif file_type == "advanced":
            self.btn_advanced.configure(bg=NothingPhoneStyle.ACCENT_RED, fg=NothingPhoneStyle.TEXT_PRIMARY)
            self.btn_basic.configure(bg=NothingPhoneStyle.BG_TERTIARY, fg=NothingPhoneStyle.TEXT_SECONDARY)
            self.btn_patterns.configure(bg=NothingPhoneStyle.BG_TERTIARY, fg=NothingPhoneStyle.TEXT_SECONDARY)
            self._show_editor()
        else: # patterns
            self.btn_patterns.configure(bg=NothingPhoneStyle.ACCENT_RED, fg=NothingPhoneStyle.TEXT_PRIMARY)
            self.btn_basic.configure(bg=NothingPhoneStyle.BG_TERTIARY, fg=NothingPhoneStyle.TEXT_SECONDARY)
            self.btn_advanced.configure(bg=NothingPhoneStyle.BG_TERTIARY, fg=NothingPhoneStyle.TEXT_SECONDARY)
            self._show_patterns()
            
        self._reload_config()
    
    def _show_editor(self):
        self.patterns_panel.pack_forget()
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Re-pack scrollbars if needed or assume they stay
        
    def _show_patterns(self):
        self.text_editor.pack_forget()
        self.patterns_panel.pack(fill=tk.BOTH, expand=True)
        # Trigger load in panel
        # We need to parse current advanced config
        try:
            # We load the advanced config file from disk to ensure we have latest
            if os.path.exists(CONFIG_FILENAME):
                with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                    settings = yaml.safe_load(f)
                self.patterns_panel.load_settings(settings)
        except:
            pass

    def _get_current_filename(self):
        return CONFIG_FILENAME_BASIC if self.current_file == "basic" else CONFIG_FILENAME
    
    def _reload_config(self):
        if self.current_file == "patterns":
            self.status_bar.configure(text="Visual Pattern Editor", fg=NothingPhoneStyle.TEXT_SECONDARY)
            return

        filename = self._get_current_filename()
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                if self.current_file == "basic":
                    content = yaml.safe_dump(SETTINGS_BASIC_DEFAULT, allow_unicode=True, default_flow_style=False)
                else:
                    content = yaml.safe_dump(SETTINGS_DEFAULT, allow_unicode=True, default_flow_style=False)
            
            self.text_editor.delete('1.0', tk.END)
            self.text_editor.insert('1.0', content)
            self.status_bar.configure(text=f"Loaded: {filename}",
                                      fg=NothingPhoneStyle.TEXT_SECONDARY)
            gui_logger.info(f"Config loaded: {filename}")
        except Exception as e:
            self.status_bar.configure(text=f"Error: {str(e)}",
                                      fg=NothingPhoneStyle.ACCENT_RED)
            gui_logger.error(f"Config load error: {str(e)}")
    
    def _validate_config(self):
        try:
            content = self.text_editor.get('1.0', tk.END)
            yaml.safe_load(content)
            return True
        except yaml.YAMLError as e:
            self.status_bar.configure(text=f"Invalid YAML: {str(e)[:50]}",
                                      fg=NothingPhoneStyle.ACCENT_RED)
            gui_logger.error(f"Config validation failed")
            return False
    
    def _save_config(self):
        if not self._validate_config():
            return
        
        if self.current_file == "patterns":
            # Save from visual editor
            new_settings = self.patterns_panel.apply_settings()
            if new_settings:
                # Save to advanced file
                filename = CONFIG_FILENAME
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        yaml.safe_dump(new_settings, f, allow_unicode=True, default_flow_style=False)
                    
                    self.status_bar.configure(text=f"✓ Patterns Saved", fg=NothingPhoneStyle.LOG_SUCCESS)
                    gui_logger.success(f"Patterns saved to {filename}")
                    
                    if self.on_save_callback:
                        self.on_save_callback("advanced", new_settings)
                except Exception as e:
                    gui_logger.error(f"Save error: {e}")
            return

        filename = self._get_current_filename()
        try:
            content = self.text_editor.get('1.0', tk.END)
            config_data = yaml.safe_load(content)
            
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config_data, f, allow_unicode=True, default_flow_style=False)
            
            self.status_bar.configure(text=f"✓ Saved: {filename}",
                                      fg=NothingPhoneStyle.LOG_SUCCESS)
            gui_logger.success(f"Config saved: {filename}")
            
            if self.on_save_callback:
                self.on_save_callback(self.current_file, config_data)
        except Exception as e:
            self.status_bar.configure(text=f"Error: {str(e)}",
                                      fg=NothingPhoneStyle.ACCENT_RED)
            gui_logger.error(f"Config save error: {str(e)}")
    
    def load_initial(self):
        self._reload_config()


class ServerManager:
    """Manages the shocking server lifecycle"""
    
    def __init__(self, settings, settings_basic, on_log=None):
        self.settings = settings
        self.settings_basic = settings_basic
        self.on_log = on_log or gui_logger
        self.running = False
        self.server_thread = None
        self.loop = None
        self.dg_connection = None  # Store DGConnection class reference
    
    def start(self):
        """Start the server in a background thread"""
        if self.running:
            self.on_log.warning("Server already running")
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        self.on_log.success("Server starting...")
    
    def stop(self):
        """Stop the server"""
        if not self.running:
            return
        
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.on_log.info("Server stopped")
    
    def _run_server(self):
        """Internal server runner"""
        try:
            # Import server modules
            sys.path.insert(0, os.path.dirname(__file__))
            
            from flask import Flask
            from pythonosc.osc_server import AsyncIOOSCUDPServer
            from pythonosc.dispatcher import Dispatcher
            from websockets import serve as wsserve
            
            import srv
            from srv.connector.coyotev3ws import DGConnection
            from srv.handler.shock_handler import ShockHandler
            
            # Store DGConnection reference for test shock
            self.dg_connection = DGConnection
            
            self.on_log.success("Modules loaded successfully")
            
            # Setup dispatcher and handlers
            dispatcher = Dispatcher()
            handlers = []
            
            # Merge settings
            for chann in ['channel_a', 'channel_b']:
                self.settings['dglab3'][chann]['avatar_params'] = self.settings_basic['dglab3'][chann]['avatar_params']
                self.settings['dglab3'][chann]['mode'] = self.settings_basic['dglab3'][chann]['mode']
                self.settings['dglab3'][chann]['strength_limit'] = self.settings_basic['dglab3'][chann]['strength_limit']
                # Ensure device_power_limit is set (fallback to strength_limit for backwards compatibility)
                if 'device_power_limit' not in self.settings['dglab3'][chann]:
                    self.settings['dglab3'][chann]['device_power_limit'] = self.settings_basic['dglab3'][chann].get('device_power_limit', 100)
            
            for chann in ['A', 'B']:
                config_chann_name = f'channel_{chann.lower()}'
                chann_mode = self.settings['dglab3'][config_chann_name]['mode']
                shock_handler = ShockHandler(SETTINGS=self.settings, DG_CONN=DGConnection, channel_name=chann)
                handlers.append(shock_handler)
                for param in self.settings['dglab3'][config_chann_name]['avatar_params']:
                    self.on_log.success(f"Channel {chann} Mode: {chann_mode} Listening: {param}")
                    dispatcher.map(param, shock_handler.osc_handler)
            
            # Run async server
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            async def ws_handler(connection):
                client = DGConnection(connection, SETTINGS=self.settings)
                await client.serve()
            
            async def run():
                for handler in handlers:
                    handler.start_background_jobs()
                
                try:
                    server = AsyncIOOSCUDPServer(
                        (self.settings["osc"]["listen_host"], self.settings["osc"]["listen_port"]),
                        dispatcher, self.loop
                    )
                    self.on_log.success(f'OSC Listening: {self.settings["osc"]["listen_host"]}:{self.settings["osc"]["listen_port"]}')
                    transport, protocol = await server.create_serve_endpoint()
                except Exception as e:
                    self.on_log.error(f"OSC listen failed: {str(e)}")
                    return
                
                try:
                    async with wsserve(ws_handler, 
                                       self.settings['ws']["listen_host"], 
                                       self.settings['ws']["listen_port"]):
                        self.on_log.success(f'WebSocket Listening: {self.settings["ws"]["listen_host"]}:{self.settings["ws"]["listen_port"]}')
                        while self.running:
                            await asyncio.sleep(0.1)
                except Exception as e:
                    self.on_log.error(f"WebSocket listen failed: {str(e)}")
                    return
                
                transport.close()
            
            self.loop.run_until_complete(run())
            
        except Exception as e:
            self.on_log.error(f"Server error: {str(e)}")
            import traceback
            self.on_log.error(traceback.format_exc())
        finally:
            self.running = False
    
    def update_strength_limit(self, channel, value):
        """Update strength limit for a channel in real-time"""
        if not self.running:
            return
            
        # Update internal settings
        channel_key = f"channel_{channel.lower()}"
        if 'dglab3' in self.settings and channel_key in self.settings['dglab3']:
            self.settings['dglab3'][channel_key]['strength_limit'] = value
            
        # Update active connections
        async def _update_connections():
            try:
                import srv
                if not hasattr(srv, 'WS_CONNECTIONS'):
                    return
                    
                for conn in srv.WS_CONNECTIONS:
                    # Update limit on connection
                    conn.strength_limit[channel.upper()] = value
                    
                    # Force update strength to match the slider (Master Volume behavior)
                    target_strength = value
                        
                    self.on_log.info(f"Updating Channel {channel} strength to {target_strength}")
                    await conn.set_strength(channel.upper(), value=target_strength)
                        
            except Exception as e:
                self.on_log.error(f"Failed to update connections: {str(e)}")
                
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(_update_connections(), self.loop)
    
    def update_device_power_limit(self, channel, value, enabled=True):
        """Update device power limit for a channel (from PATTERNS config)"""
        if not self.running:
            return
            
        channel_key = f"channel_{channel.lower()}"
        if 'dglab3' in self.settings and channel_key in self.settings['dglab3']:
            self.settings['dglab3'][channel_key]['device_power_limit'] = value
            self.settings['dglab3'][channel_key]['power_settings_enabled'] = enabled
            
        async def _update_device_limits():
            try:
                import srv
                if not hasattr(srv, 'WS_CONNECTIONS'):
                    return
                
                # Update the strength_limit on all connections (this is the hardware limit)
                for conn in srv.WS_CONNECTIONS:
                    conn.strength_limit[channel.upper()] = value
                    self.on_log.info(f"Channel {channel} device power limit set to {value} (Enabled: {enabled})")
                        
            except Exception as e:
                self.on_log.error(f"Failed to update device limit: {str(e)}")
                
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(_update_device_limits(), self.loop)
    
    def send_test_shock(self, channel):
        """Send a short test shock to the specified channel"""
        if not self.running or not self.loop or not self.dg_connection:
            self.on_log.warning("Server not running, cannot send test shock")
            return
        
        async def do_shock():
            try:
                # Short test wave - 3 pulses (300ms)
                test_wave = '["0A0A0A0A64646464","0A0A0A0A64646464","0A0A0A0A64646464"]'
                await self.dg_connection.broadcast_wave(channel=channel.upper(), wavestr=test_wave)
                self.on_log.success(f"Test shock sent to Channel {channel}")
            except Exception as e:
                self.on_log.error(f"Test shock failed: {str(e)}")
        
        # Schedule the coroutine on the server's event loop
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(do_shock(), self.loop)


class ShockingVRChatGUI(tk.Tk):
    """Main application window - Full replacement for CMD app"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Shocking VRChat")
        self.configure(bg=NothingPhoneStyle.BG_PRIMARY)
        self.geometry("1000x700")
        self.minsize(800, 550)
        
        # Track window size
        self.current_scale = 1.0
        self.fonts = NothingPhoneStyle.get_scaled_fonts(1.0)
        
        # Load settings
        self.settings = {}
        self.settings_basic = {}
        self._load_settings()
        
        # Server info
        self.server_ip = self._get_local_ip()
        self.qr_url = ""
        
        # Server manager
        self.server_manager = None
        self.server_running = False
        
        # Bind resize event
        self.bind("<Configure>", self._on_resize)
        self._last_width = 0
        self._last_height = 0
        
        self._create_ui()
        self._update_qr()
        
        # Configure style for ttk widgets
        self._configure_ttk_style()
        
        # Initial logs
        gui_logger.success("Shocking VRChat GUI started")
        gui_logger.info(f"Server IP: {self.server_ip}")
        gui_logger.info(f"WS Port: {self.settings.get('ws', {}).get('listen_port', 28846)}")
        gui_logger.info(f"OSC Port: {self.settings.get('osc', {}).get('listen_port', 9001)}")
        
        # Auto-start server
        self.after(500, self._start_server)
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _configure_ttk_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TScrollbar",
                        background=NothingPhoneStyle.BG_TERTIARY,
                        troughcolor=NothingPhoneStyle.BG_SECONDARY,
                        arrowcolor=NothingPhoneStyle.TEXT_SECONDARY)
    
    def _on_resize(self, event):
        """Handle window resize for responsive layout"""
        if event.widget != self:
            return
        
        width = event.width
        height = event.height
        
        if abs(width - self._last_width) < 50 and abs(height - self._last_height) < 50:
            return
        
        self._last_width = width
        self._last_height = height
        
        # Calculate scale factor
        base_width = 1000
        new_scale = max(0.7, min(1.3, width / base_width))
        
        if abs(new_scale - self.current_scale) > 0.1:
            self.current_scale = new_scale
            if hasattr(self, 'qr_panel'):
                qr_size = int(180 * new_scale)
                self.qr_panel.resize(max(150, min(250, qr_size)))
                self._update_qr()
    
    def _load_settings(self):
        """Load settings from config files"""
        try:
            if os.path.exists(CONFIG_FILENAME):
                with open(CONFIG_FILENAME, 'r', encoding='utf-8') as f:
                    self.settings = yaml.safe_load(f)
            else:
                self.settings = SETTINGS_DEFAULT.copy()
                self.settings['ws']['master_uuid'] = str(uuid.uuid4())
                # Save initial config
                with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(self.settings, f, allow_unicode=True)
            
            if os.path.exists(CONFIG_FILENAME_BASIC):
                with open(CONFIG_FILENAME_BASIC, 'r', encoding='utf-8') as f:
                    self.settings_basic = yaml.safe_load(f)
            else:
                self.settings_basic = SETTINGS_BASIC_DEFAULT.copy()
                with open(CONFIG_FILENAME_BASIC, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(self.settings_basic, f, allow_unicode=True)
                    
        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load config: {str(e)}")
            self.settings = SETTINGS_DEFAULT.copy()
            self.settings_basic = SETTINGS_BASIC_DEFAULT.copy()
    
    def _get_local_ip(self):
        """Get local IP address"""
        try:
            host = self.settings.get('general', {}).get('local_ip_detect', {}).get('host', '223.5.5.5')
            port = self.settings.get('general', {}).get('local_ip_detect', {}).get('port', 80)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((host, port))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _create_ui(self):
        # Main container
        main_container = tk.Frame(self, bg=NothingPhoneStyle.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header
        header = tk.Frame(main_container, bg=NothingPhoneStyle.BG_PRIMARY)
        header.pack(fill=tk.X, pady=(0, 15))
        
        # Logo/Title area with dot pattern
        title_area = tk.Frame(header, bg=NothingPhoneStyle.BG_PRIMARY)
        title_area.pack(side=tk.LEFT)
        
        dot_frame = tk.Canvas(title_area, width=36, height=36,
                              bg=NothingPhoneStyle.BG_PRIMARY,
                              highlightthickness=0)
        dot_frame.pack(side=tk.LEFT, padx=(0, 12))
        
        for row in range(3):
            for col in range(3):
                x = 4 + col * 11
                y = 4 + row * 11
                color = NothingPhoneStyle.ACCENT_RED if (row + col) % 2 == 0 else NothingPhoneStyle.TEXT_MUTED
                dot_frame.create_oval(x, y, x+7, y+7, fill=color, outline="")
        
        title_text = tk.Frame(title_area, bg=NothingPhoneStyle.BG_PRIMARY)
        title_text.pack(side=tk.LEFT)
        
        title = tk.Label(title_text, text="SHOCKING VRCHAT",
                         font=self.fonts['title'],
                         bg=NothingPhoneStyle.BG_PRIMARY,
                         fg=NothingPhoneStyle.TEXT_PRIMARY)
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(title_text, text="DG-LAB CONTROLLER",
                            font=self.fonts['small'],
                            bg=NothingPhoneStyle.BG_PRIMARY,
                            fg=NothingPhoneStyle.TEXT_SECONDARY)
        subtitle.pack(anchor=tk.W)
        
        # Status indicator
        status_frame = tk.Frame(header, bg=NothingPhoneStyle.BG_PRIMARY)
        status_frame.pack(side=tk.RIGHT)
        
        self.status_dot = tk.Canvas(status_frame, width=12, height=12,
                                    bg=NothingPhoneStyle.BG_PRIMARY,
                                    highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))
        self.status_dot.create_oval(2, 2, 10, 10, fill=NothingPhoneStyle.LOG_WARNING, 
                                    outline="", tags="dot")
        
        self.status_text = tk.Label(status_frame, text="STARTING...",
                                    font=self.fonts['small'],
                                    bg=NothingPhoneStyle.BG_PRIMARY,
                                    fg=NothingPhoneStyle.TEXT_SECONDARY)
        self.status_text.pack(side=tk.LEFT)
        
        # Content area - two columns
        content = tk.Frame(main_container, bg=NothingPhoneStyle.BG_PRIMARY)
        content.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Controls & Config
        left_column = tk.Frame(content, bg=NothingPhoneStyle.BG_PRIMARY)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Power controls card
        power_card = tk.Frame(left_column, bg=NothingPhoneStyle.BG_SECONDARY)
        power_card.pack(fill=tk.X, pady=(0, 10))
        
        self.slider_a = PowerSlider(power_card, "CHANNEL A", "A",
                                    min_val=0, max_val=200,
                                    initial=min(200, self.settings_basic.get('dglab3', {}).get('channel_a', {}).get('strength_limit', 100)),
                                    callback=self._on_strength_change,
                                    test_shock_callback=self._on_test_shock,
                                    fonts=self.fonts,
                                    compact=True)
        self.slider_a.pack(fill=tk.X)
        
        sep = tk.Frame(power_card, height=1, bg=NothingPhoneStyle.BORDER_COLOR)
        sep.pack(fill=tk.X, padx=10)
        
        self.slider_b = PowerSlider(power_card, "CHANNEL B", "B",
                                    min_val=0, max_val=200,
                                    initial=min(200, self.settings_basic.get('dglab3', {}).get('channel_b', {}).get('strength_limit', 100)),
                                    callback=self._on_strength_change,
                                    test_shock_callback=self._on_test_shock,
                                    fonts=self.fonts,
                                    compact=True)
        self.slider_b.pack(fill=tk.X)
        
        # Config editor
        self.config_editor = ConfigEditor(left_column, 
                                          on_save_callback=self._on_config_save,
                                          fonts=self.fonts)
        self.config_editor.pack(fill=tk.BOTH, expand=True)
        self.config_editor.load_initial()
        
        # Right column - QR & Logs
        right_column = tk.Frame(content, bg=NothingPhoneStyle.BG_PRIMARY, width=280)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
        right_column.pack_propagate(False)
        
        # QR Code panel
        self.qr_panel = QRCodePanel(right_column, fonts=self.fonts, size=180)
        self.qr_panel.pack(fill=tk.X, pady=(0, 10))
        self.qr_panel.set_copy_command(self._copy_qr_url)
        
        # System Logs panel
        self.logs_panel = SystemLogsPanel(right_column, fonts=self.fonts)
        self.logs_panel.pack(fill=tk.BOTH, expand=True)
    
    def _update_qr(self):
        """Update QR code with current connection URL"""
        try:
            ws_port = self.settings.get('ws', {}).get('listen_port', 28846)
            master_uuid = self.settings.get('ws', {}).get('master_uuid', '')
            
            if not master_uuid:
                self.qr_panel.set_placeholder()
                return
            
            url = f"https://www.dungeon-lab.com/app-download.php#DGLAB-SOCKET#ws://{self.server_ip}:{ws_port}/{master_uuid}"
            self.qr_panel.update_qr(url)
            self.qr_url = url
        except Exception as e:
            self.qr_panel.set_placeholder()
            gui_logger.error(f"QR generation error: {str(e)}")
    
    def _on_test_shock(self, channel):
        """Handle test shock button press"""
        if self.server_manager:
            self.server_manager.send_test_shock(channel)
        else:
            gui_logger.warning("Server not started, cannot send test shock")
    
    def _on_strength_change(self, channel, value):
        """Handle strength slider change - auto save"""
        channel_key = f"channel_{channel.lower()}"
        try:
            self.settings_basic['dglab3'][channel_key]['strength_limit'] = value
            
            # Auto-save to file
            with open(CONFIG_FILENAME_BASIC, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.settings_basic, f, allow_unicode=True)
            
            # Update running server if available
            if self.server_manager:
                self.server_manager.settings_basic = self.settings_basic
                self.server_manager.update_strength_limit(channel, value)
                
            gui_logger.info(f"Channel {channel} strength: {value}")
        except Exception as e:
            gui_logger.error(f"Error updating strength: {e}")
    
    def _on_config_save(self, file_type, config_data):
        """Handle config save from editor"""
        if file_type == "basic":
            self.settings_basic = config_data
            try:
                self.slider_a.set_value(
                    config_data.get('dglab3', {}).get('channel_a', {}).get('strength_limit', 100)
                )
                self.slider_b.set_value(
                    config_data.get('dglab3', {}).get('channel_b', {}).get('strength_limit', 100)
                )
            except:
                pass
        else:
            # Advanced or Patterns config saved
            self.settings = config_data
            self._update_qr()
            
            # Sync power settings with running server
            if self.server_manager and self.server_manager.running:
                try:
                    # Update server's settings reference
                    self.server_manager.settings = config_data
                    
                    # Update device power limits on all connections
                    for ch in ['A', 'B']:
                        ch_key = f'channel_{ch.lower()}'
                        device_limit = config_data.get('dglab3', {}).get(ch_key, {}).get('device_power_limit', 100)
                        power_enabled = config_data.get('dglab3', {}).get(ch_key, {}).get('power_settings_enabled', True)
                        self.server_manager.update_device_power_limit(ch, device_limit, power_enabled)
                    
                    gui_logger.success("Power settings synced with server")
                except Exception as e:
                    gui_logger.error(f"Failed to sync settings: {e}")
    
    def _start_server(self):
        """Start the integrated server"""
        try:
            self.server_manager = ServerManager(
                self.settings.copy(), 
                self.settings_basic.copy(),
                gui_logger
            )
            self.server_manager.start()
            
            self.server_running = True
            self._update_status(True)
            
        except Exception as e:
            gui_logger.error(f"Failed to start server: {str(e)}")
            self._update_status(False)
    
    def _update_status(self, running):
        """Update status indicator"""
        self.status_dot.delete("dot")
        if running:
            self.status_dot.create_oval(2, 2, 10, 10, 
                                        fill=NothingPhoneStyle.LOG_SUCCESS, 
                                        outline="", tags="dot")
            self.status_text.configure(text="RUNNING")
        else:
            self.status_dot.create_oval(2, 2, 10, 10, 
                                        fill=NothingPhoneStyle.ACCENT_RED, 
                                        outline="", tags="dot")
            self.status_text.configure(text="STOPPED")
    
    def _copy_qr_url(self):
        """Copy QR URL to clipboard"""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.qr_url)
            gui_logger.success("QR URL copied to clipboard")
        except Exception as e:
            gui_logger.error(f"Failed to copy: {str(e)}")
    
    def _on_close(self):
        """Handle window close"""
        if self.server_manager:
            self.server_manager.stop()
        self.destroy()


def main():
    app = ShockingVRChatGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
