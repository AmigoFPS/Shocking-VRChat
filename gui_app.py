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
            'strength_limit': 100,
            'n_derivative': 0,
            # New dynamic power settings
            'device_limit': 100,      # Max device power (0-200)
            'sensitivity': 100,       # Response multiplier (0-200%)
            'threshold': 10,          # Min activation level (0-100)
            # Random boost on impact
            'impact_boost_min': 0,    # Min random boost (0-100)
            'impact_boost_max': 30,   # Max random boost (0-100)
        },
        'channel_b': {
            'avatar_params': [
                '/avatar/parameters/pcs/contact/enterPass',
                '/avatar/parameters/lms-penis-proximityA*',
                '/avatar/parameters/TouchAreaC',
                '/avatar/parameters/TouchAreaD',
            ],
            'mode': 'distance',
            'strength_limit': 100,
            'n_derivative': 0,
            # New dynamic power settings
            'device_limit': 100,      # Max device power (0-200)
            'sensitivity': 100,       # Response multiplier (0-200%)
            'threshold': 10,          # Min activation level (0-100)
            # Random boost on impact
            'impact_boost_min': 0,    # Min random boost (0-100)
            'impact_boost_max': 30,   # Max random boost (0-100)
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
    """Custom log handler that outputs to GUI and intercepts loguru backend logs"""
    
    # Log level mapping from loguru to our levels
    LOGURU_LEVEL_MAP = {
        'TRACE': 'INFO',
        'DEBUG': 'INFO',
        'INFO': 'INFO',
        'SUCCESS': 'SUCCESS',
        'WARNING': 'WARNING',
        'ERROR': 'ERROR',
        'CRITICAL': 'ERROR',
    }
    
    def __init__(self):
        self.log_queue = queue.Queue()
        self.callbacks = []
        self._loguru_connected = False
    
    def add_callback(self, callback):
        self.callbacks.append(callback)
    
    def connect_loguru(self):
        """Connect loguru logger to this handler so backend logs appear in GUI"""
        if self._loguru_connected:
            return
        try:
            from loguru import logger as loguru_logger
            
            def _loguru_sink(message):
                record = message.record
                level = self.LOGURU_LEVEL_MAP.get(record['level'].name, 'INFO')
                # Skip overly verbose debug messages
                if record['level'].name in ('TRACE', 'DEBUG'):
                    return
                # Format with source module info
                module = record['module']
                func = record['function']
                msg = str(record['message'])
                source = f"[{module}] " if module not in ('gui_app',) else ""
                self.log(level, f"{source}{msg}")
            
            # Remove default stderr handler to avoid duplicate output
            loguru_logger.add(_loguru_sink, level="INFO", format="{message}")
            self._loguru_connected = True
        except ImportError:
            pass
    
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
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
        
        # Test shock button - separated from main controls with warning style
        test_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        test_frame.pack(fill=tk.X, padx=pad_x, pady=(0, 8 if self.compact else 12))
        
        # Warning label
        test_warn = tk.Label(test_frame, text="⚠",
                             font=self.fonts['small'],
                             bg=NothingPhoneStyle.BG_SECONDARY,
                             fg=NothingPhoneStyle.TEXT_MUTED)
        test_warn.pack(side=tk.LEFT, padx=(0, 4))
        
        self.btn_test = tk.Button(test_frame, text="⚡ TEST SHOCK",
                                  font=self.fonts['small'],
                                  bg=NothingPhoneStyle.BG_TERTIARY,
                                  fg=NothingPhoneStyle.LOG_WARNING,
                                  activebackground=NothingPhoneStyle.ACCENT_RED,
                                  activeforeground=NothingPhoneStyle.TEXT_PRIMARY,
                                  bd=1,
                                  relief=tk.SOLID,
                                  width=14,
                                  cursor="hand2",
                                  command=self._test_shock)
        self.btn_test.pack(side=tk.RIGHT)
    
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


class PatternSelector(tk.Frame):
    """Pattern mode selector panel for each channel with dynamic power settings"""
    
    PATTERNS = {
        'PROXIMITY': {
            'mode': 'distance',
            'description': 'Power depends on distance to contact',
            'n_derivative': 0
        },
        'IMPACT': {
            'mode': 'touch',
            'description': 'Power depends on movement speed',
            'n_derivative': 1
        },
        'RECOIL': {
            'mode': 'touch', 
            'description': 'Power depends on acceleration',
            'n_derivative': 2
        }
    }
    
    def __init__(self, parent, channel, initial_mode='PROXIMITY', 
                 initial_device_limit=100, initial_sensitivity=100, initial_threshold=10,
                 initial_boost_min=0, initial_boost_max=30,
                 callback=None, settings_callback=None, fonts=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.channel = channel
        self.callback = callback
        self.settings_callback = settings_callback
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.selected_pattern = tk.StringVar(value=initial_mode)
        self.device_limit = tk.IntVar(value=initial_device_limit)
        self.sensitivity = tk.IntVar(value=initial_sensitivity)
        self.threshold = tk.IntVar(value=initial_threshold)
        self.impact_boost_min = tk.IntVar(value=initial_boost_min)
        self.impact_boost_max = tk.IntVar(value=initial_boost_max)
        self._create_widgets()
    
    def _create_widgets(self):
        # Channel header
        header = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        dot_canvas = tk.Canvas(header, width=10, height=10,
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               highlightthickness=0)
        dot_canvas.pack(side=tk.LEFT, padx=(0, 8))
        dot_canvas.create_oval(2, 2, 8, 8, fill=NothingPhoneStyle.ACCENT_RED, outline="")
        
        title = tk.Label(header, text=f"CHANNEL {self.channel}",
                         font=self.fonts['heading'],
                         bg=NothingPhoneStyle.BG_SECONDARY,
                         fg=NothingPhoneStyle.TEXT_PRIMARY)
        title.pack(side=tk.LEFT)
        
        # Pattern buttons container
        buttons_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
        
        self.pattern_buttons = {}
        for pattern_name in self.PATTERNS.keys():
            btn = tk.Radiobutton(
                buttons_frame,
                text=pattern_name,
                variable=self.selected_pattern,
                value=pattern_name,
                font=self.fonts['small'],
                bg=NothingPhoneStyle.BG_SECONDARY,
                fg=NothingPhoneStyle.TEXT_PRIMARY,
                selectcolor=NothingPhoneStyle.BG_TERTIARY,
                activebackground=NothingPhoneStyle.BG_SECONDARY,
                activeforeground=NothingPhoneStyle.ACCENT_RED,
                indicatoron=0,
                width=10,
                height=1,
                bd=0,
                highlightthickness=1,
                highlightbackground=NothingPhoneStyle.BORDER_COLOR,
                highlightcolor=NothingPhoneStyle.ACCENT_RED,
                cursor="hand2",
                command=self._on_pattern_change
            )
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
            self.pattern_buttons[pattern_name] = btn
        
        # Update button styles
        self._update_button_styles()
        
        # Description label
        self.desc_label = tk.Label(
            self,
            text=self.PATTERNS[self.selected_pattern.get()]['description'],
            font=self.fonts['small'],
            bg=NothingPhoneStyle.BG_SECONDARY,
            fg=NothingPhoneStyle.TEXT_MUTED,
            wraplength=300
        )
        self.desc_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Dynamic power settings frame (always visible)
        self.settings_frame = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        self.settings_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Device Limit slider (max power)
        self.limit_frame = tk.Frame(self.settings_frame, bg=NothingPhoneStyle.BG_SECONDARY)
        self.limit_frame.pack(fill=tk.X, pady=2)
        
        limit_label = tk.Label(self.limit_frame, text="Device Limit:",
                               font=self.fonts['small'],
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               fg=NothingPhoneStyle.TEXT_SECONDARY,
                               width=12, anchor=tk.W)
        limit_label.pack(side=tk.LEFT)
        
        self.limit_slider = tk.Scale(
            self.limit_frame,
            from_=0, to=200,
            orient=tk.HORIZONTAL,
            variable=self.device_limit,
            font=self.fonts['small'],
            bg=NothingPhoneStyle.BG_SECONDARY,
            fg=NothingPhoneStyle.TEXT_PRIMARY,
            troughcolor=NothingPhoneStyle.BG_TERTIARY,
            activebackground=NothingPhoneStyle.ACCENT_RED,
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            length=120,
            command=lambda v: self._on_setting_change('device_limit', int(v))
        )
        self.limit_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.limit_value_label = tk.Label(self.limit_frame, 
                                          text=f"{self.device_limit.get()}",
                                          font=self.fonts['small'],
                                          bg=NothingPhoneStyle.BG_SECONDARY,
                                          fg=NothingPhoneStyle.ACCENT_RED,
                                          width=5)
        self.limit_value_label.pack(side=tk.RIGHT)
        
        # Sensitivity slider (response multiplier)
        self.sens_frame = tk.Frame(self.settings_frame, bg=NothingPhoneStyle.BG_SECONDARY)
        self.sens_frame.pack(fill=tk.X, pady=2)
        
        sens_label = tk.Label(self.sens_frame, text="Sensitivity:",
                              font=self.fonts['small'],
                              bg=NothingPhoneStyle.BG_SECONDARY,
                              fg=NothingPhoneStyle.TEXT_SECONDARY,
                              width=12, anchor=tk.W)
        sens_label.pack(side=tk.LEFT)
        
        self.sens_slider = tk.Scale(
            self.sens_frame,
            from_=0, to=200,
            orient=tk.HORIZONTAL,
            variable=self.sensitivity,
            font=self.fonts['small'],
            bg=NothingPhoneStyle.BG_SECONDARY,
            fg=NothingPhoneStyle.TEXT_PRIMARY,
            troughcolor=NothingPhoneStyle.BG_TERTIARY,
            activebackground=NothingPhoneStyle.ACCENT_ORANGE,
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            length=120,
            command=lambda v: self._on_setting_change('sensitivity', int(v))
        )
        self.sens_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.sens_value_label = tk.Label(self.sens_frame,
                                         text=f"{self.sensitivity.get()}%",
                                         font=self.fonts['small'],
                                         bg=NothingPhoneStyle.BG_SECONDARY,
                                         fg=NothingPhoneStyle.ACCENT_ORANGE,
                                         width=5)
        self.sens_value_label.pack(side=tk.RIGHT)
        
        # Threshold slider (min activation)
        self.thresh_frame = tk.Frame(self.settings_frame, bg=NothingPhoneStyle.BG_SECONDARY)
        self.thresh_frame.pack(fill=tk.X, pady=2)
        
        thresh_label = tk.Label(self.thresh_frame, text="Threshold:",
                                font=self.fonts['small'],
                                bg=NothingPhoneStyle.BG_SECONDARY,
                                fg=NothingPhoneStyle.TEXT_SECONDARY,
                                width=12, anchor=tk.W)
        thresh_label.pack(side=tk.LEFT)
        
        self.thresh_slider = tk.Scale(
            self.thresh_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self.threshold,
            font=self.fonts['small'],
            bg=NothingPhoneStyle.BG_SECONDARY,
            fg=NothingPhoneStyle.TEXT_PRIMARY,
            troughcolor=NothingPhoneStyle.BG_TERTIARY,
            activebackground=NothingPhoneStyle.LOG_INFO,
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            length=120,
            command=lambda v: self._on_setting_change('threshold', int(v))
        )
        self.thresh_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.thresh_value_label = tk.Label(self.thresh_frame,
                                           text=f"{self.threshold.get()}%",
                                           font=self.fonts['small'],
                                           bg=NothingPhoneStyle.BG_SECONDARY,
                                           fg=NothingPhoneStyle.LOG_INFO,
                                           width=5)
        self.thresh_value_label.pack(side=tk.RIGHT)
        
        # Impact Boost Range frame (random boost on impact detection)
        self.boost_frame = tk.Frame(self.settings_frame, bg=NothingPhoneStyle.BG_SECONDARY)
        self.boost_frame.pack(fill=tk.X, pady=(5, 2))
        
        boost_title = tk.Label(self.boost_frame, text="⚡ Random Boost:",
                               font=self.fonts['small'],
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               fg=NothingPhoneStyle.ACCENT_ORANGE,
                               anchor=tk.W)
        boost_title.pack(fill=tk.X)
        
        # Min boost slider
        self.boost_min_frame = tk.Frame(self.settings_frame, bg=NothingPhoneStyle.BG_SECONDARY)
        self.boost_min_frame.pack(fill=tk.X, pady=1)
        
        boost_min_label = tk.Label(self.boost_min_frame, text="  Min:",
                                   font=self.fonts['small'],
                                   bg=NothingPhoneStyle.BG_SECONDARY,
                                   fg=NothingPhoneStyle.TEXT_SECONDARY,
                                   width=12, anchor=tk.W)
        boost_min_label.pack(side=tk.LEFT)
        
        self.boost_min_slider = tk.Scale(
            self.boost_min_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self.impact_boost_min,
            font=self.fonts['small'],
            bg=NothingPhoneStyle.BG_SECONDARY,
            fg=NothingPhoneStyle.TEXT_PRIMARY,
            troughcolor=NothingPhoneStyle.BG_TERTIARY,
            activebackground=NothingPhoneStyle.ACCENT_ORANGE,
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            length=120,
            command=lambda v: self._on_setting_change('impact_boost_min', int(v))
        )
        self.boost_min_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.boost_min_value_label = tk.Label(self.boost_min_frame,
                                              text=f"+{self.impact_boost_min.get()}",
                                              font=self.fonts['small'],
                                              bg=NothingPhoneStyle.BG_SECONDARY,
                                              fg=NothingPhoneStyle.ACCENT_ORANGE,
                                              width=5)
        self.boost_min_value_label.pack(side=tk.RIGHT)
        
        # Max boost slider
        self.boost_max_frame = tk.Frame(self.settings_frame, bg=NothingPhoneStyle.BG_SECONDARY)
        self.boost_max_frame.pack(fill=tk.X, pady=1)
        
        boost_max_label = tk.Label(self.boost_max_frame, text="  Max:",
                                   font=self.fonts['small'],
                                   bg=NothingPhoneStyle.BG_SECONDARY,
                                   fg=NothingPhoneStyle.TEXT_SECONDARY,
                                   width=12, anchor=tk.W)
        boost_max_label.pack(side=tk.LEFT)
        
        self.boost_max_slider = tk.Scale(
            self.boost_max_frame,
            from_=0, to=100,
            orient=tk.HORIZONTAL,
            variable=self.impact_boost_max,
            font=self.fonts['small'],
            bg=NothingPhoneStyle.BG_SECONDARY,
            fg=NothingPhoneStyle.TEXT_PRIMARY,
            troughcolor=NothingPhoneStyle.BG_TERTIARY,
            activebackground=NothingPhoneStyle.ACCENT_RED,
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            length=120,
            command=lambda v: self._on_setting_change('impact_boost_max', int(v))
        )
        self.boost_max_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        self.boost_max_value_label = tk.Label(self.boost_max_frame,
                                              text=f"+{self.impact_boost_max.get()}",
                                              font=self.fonts['small'],
                                              bg=NothingPhoneStyle.BG_SECONDARY,
                                              fg=NothingPhoneStyle.ACCENT_RED,
                                              width=5)
        self.boost_max_value_label.pack(side=tk.RIGHT)
    
    def _update_button_styles(self):
        """Update button styles based on selection"""
        selected = self.selected_pattern.get()
        for name, btn in self.pattern_buttons.items():
            if name == selected:
                btn.configure(
                    bg=NothingPhoneStyle.ACCENT_RED,
                    fg=NothingPhoneStyle.TEXT_PRIMARY,
                    highlightbackground=NothingPhoneStyle.ACCENT_RED
                )
            else:
                btn.configure(
                    bg=NothingPhoneStyle.BG_TERTIARY,
                    fg=NothingPhoneStyle.TEXT_SECONDARY,
                    highlightbackground=NothingPhoneStyle.BORDER_COLOR
                )
    
    def _on_pattern_change(self):
        """Handle pattern selection change"""
        selected = self.selected_pattern.get()
        self._update_button_styles()
        
        # Update description
        self.desc_label.configure(text=self.PATTERNS[selected]['description'])
        
        # Notify callback
        if self.callback:
            pattern_config = self.PATTERNS[selected]
            self.callback(self.channel, selected, pattern_config, self.get_settings())
    
    def _on_setting_change(self, setting_name, value):
        """Handle settings slider change"""
        if setting_name == 'device_limit':
            self.limit_value_label.configure(text=f"{value}")
        elif setting_name == 'sensitivity':
            self.sens_value_label.configure(text=f"{value}%")
        elif setting_name == 'threshold':
            self.thresh_value_label.configure(text=f"{value}%")
        elif setting_name == 'impact_boost_min':
            self.boost_min_value_label.configure(text=f"+{value}")
            # Ensure min <= max
            if value > self.impact_boost_max.get():
                self.impact_boost_max.set(value)
                self.boost_max_value_label.configure(text=f"+{value}")
                if self.settings_callback:
                    self.settings_callback(self.channel, 'impact_boost_max', value)
        elif setting_name == 'impact_boost_max':
            self.boost_max_value_label.configure(text=f"+{value}")
            # Ensure max >= min
            if value < self.impact_boost_min.get():
                self.impact_boost_min.set(value)
                self.boost_min_value_label.configure(text=f"+{value}")
                if self.settings_callback:
                    self.settings_callback(self.channel, 'impact_boost_min', value)
        
        if self.settings_callback:
            self.settings_callback(self.channel, setting_name, value)
    
    def get_pattern(self):
        """Get current pattern name"""
        return self.selected_pattern.get()
    
    def get_pattern_config(self):
        """Get current pattern configuration"""
        return self.PATTERNS[self.selected_pattern.get()]
    
    def get_settings(self):
        """Get current dynamic power settings"""
        return {
            'device_limit': self.device_limit.get(),
            'sensitivity': self.sensitivity.get(),
            'threshold': self.threshold.get(),
            'impact_boost_min': self.impact_boost_min.get(),
            'impact_boost_max': self.impact_boost_max.get()
        }
    
    def set_pattern(self, pattern_name):
        """Set pattern by name"""
        if pattern_name in self.PATTERNS:
            self.selected_pattern.set(pattern_name)
            self._update_button_styles()
            self.desc_label.configure(text=self.PATTERNS[pattern_name]['description'])
    
    def set_settings(self, device_limit=None, sensitivity=None, threshold=None, 
                     impact_boost_min=None, impact_boost_max=None):
        """Set dynamic power settings"""
        if device_limit is not None:
            self.device_limit.set(device_limit)
            self.limit_value_label.configure(text=f"{device_limit}")
        if sensitivity is not None:
            self.sensitivity.set(sensitivity)
            self.sens_value_label.configure(text=f"{sensitivity}%")
        if threshold is not None:
            self.threshold.set(threshold)
            self.thresh_value_label.configure(text=f"{threshold}%")
        if impact_boost_min is not None:
            self.impact_boost_min.set(impact_boost_min)
            self.boost_min_value_label.configure(text=f"+{impact_boost_min}")
        if impact_boost_max is not None:
            self.impact_boost_max.set(impact_boost_max)
            self.boost_max_value_label.configure(text=f"+{impact_boost_max}")


class PatternPanel(tk.Frame):
    """Pattern configuration panel with channel selectors"""
    
    def __init__(self, parent, settings_basic, callback=None, settings_callback=None, fonts=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.settings_basic = settings_basic
        self.callback = callback
        self.settings_callback = settings_callback
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self._create_widgets()
    
    def _get_initial_pattern(self, channel):
        """Determine initial pattern from settings"""
        channel_key = f'channel_{channel.lower()}'
        mode = self.settings_basic.get('dglab3', {}).get(channel_key, {}).get('mode', 'distance')
        n_derivative = self.settings_basic.get('dglab3', {}).get(channel_key, {}).get('n_derivative', 0)
        
        if mode == 'distance':
            return 'PROXIMITY'
        elif mode == 'touch':
            if n_derivative == 1:
                return 'IMPACT'
            elif n_derivative >= 2:
                return 'RECOIL'
        return 'PROXIMITY'
    
    def _get_initial_setting(self, channel, setting_name):
        """Get initial setting value from settings"""
        channel_key = f'channel_{channel.lower()}'
        defaults = {
            'device_limit': 100, 
            'sensitivity': 100, 
            'threshold': 10,
            'impact_boost_min': 0,
            'impact_boost_max': 30
        }
        return self.settings_basic.get('dglab3', {}).get(channel_key, {}).get(setting_name, defaults.get(setting_name, 100))
    
    def _create_widgets(self):
        # Header
        header = tk.Frame(self, bg=NothingPhoneStyle.BG_SECONDARY)
        header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        dot_canvas = tk.Canvas(header, width=10, height=10,
                               bg=NothingPhoneStyle.BG_SECONDARY,
                               highlightthickness=0)
        dot_canvas.pack(side=tk.LEFT, padx=(0, 8))
        dot_canvas.create_oval(2, 2, 8, 8, fill=NothingPhoneStyle.ACCENT_RED, outline="")
        
        title = tk.Label(header, text="PATTERN MODE",
                         font=self.fonts['heading'],
                         bg=NothingPhoneStyle.BG_SECONDARY,
                         fg=NothingPhoneStyle.TEXT_PRIMARY)
        title.pack(side=tk.LEFT)
        
        # Separator
        sep1 = tk.Frame(self, height=1, bg=NothingPhoneStyle.BORDER_COLOR)
        sep1.pack(fill=tk.X, padx=10, pady=5)
        
        # Channel A selector
        self.pattern_a = PatternSelector(
            self, 
            channel='A',
            initial_mode=self._get_initial_pattern('A'),
            initial_device_limit=self._get_initial_setting('A', 'device_limit'),
            initial_sensitivity=self._get_initial_setting('A', 'sensitivity'),
            initial_threshold=self._get_initial_setting('A', 'threshold'),
            initial_boost_min=self._get_initial_setting('A', 'impact_boost_min'),
            initial_boost_max=self._get_initial_setting('A', 'impact_boost_max'),
            callback=self._on_pattern_change,
            settings_callback=self._on_setting_change,
            fonts=self.fonts
        )
        self.pattern_a.pack(fill=tk.X)
        
        # Separator
        sep2 = tk.Frame(self, height=1, bg=NothingPhoneStyle.BORDER_COLOR)
        sep2.pack(fill=tk.X, padx=10, pady=5)
        
        # Channel B selector
        self.pattern_b = PatternSelector(
            self,
            channel='B',
            initial_mode=self._get_initial_pattern('B'),
            initial_device_limit=self._get_initial_setting('B', 'device_limit'),
            initial_sensitivity=self._get_initial_setting('B', 'sensitivity'),
            initial_threshold=self._get_initial_setting('B', 'threshold'),
            initial_boost_min=self._get_initial_setting('B', 'impact_boost_min'),
            initial_boost_max=self._get_initial_setting('B', 'impact_boost_max'),
            callback=self._on_pattern_change,
            settings_callback=self._on_setting_change,
            fonts=self.fonts
        )
        self.pattern_b.pack(fill=tk.X)
    
    def _on_pattern_change(self, channel, pattern_name, pattern_config, settings):
        """Handle pattern change for a channel"""
        if self.callback:
            self.callback(channel, pattern_name, pattern_config, settings)
    
    def _on_setting_change(self, channel, setting_name, value):
        """Handle settings slider change"""
        if self.settings_callback:
            self.settings_callback(channel, setting_name, value)
    
    def get_patterns(self):
        """Get current patterns for both channels"""
        return {
            'A': {
                **self.pattern_a.get_pattern_config(),
                **self.pattern_a.get_settings()
            },
            'B': {
                **self.pattern_b.get_pattern_config(),
                **self.pattern_b.get_settings()
            }
        }


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
    """System logs panel with category filters"""
    
    def __init__(self, parent, fonts=None):
        super().__init__(parent, bg=NothingPhoneStyle.BG_SECONDARY)
        self.fonts = fonts or NothingPhoneStyle.get_scaled_fonts()
        self.max_logs = 50
        self.auto_scroll = True
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
        
        # Auto-scroll toggle
        self.auto_scroll_var = tk.BooleanVar(value=True)
        btn_scroll = tk.Checkbutton(header, text="AUTO↓",
                                     font=self.fonts['small'],
                                     variable=self.auto_scroll_var,
                                     bg=NothingPhoneStyle.BG_SECONDARY,
                                     fg=NothingPhoneStyle.TEXT_SECONDARY,
                                     selectcolor=NothingPhoneStyle.BG_TERTIARY,
                                     activebackground=NothingPhoneStyle.BG_SECONDARY,
                                     bd=0,
                                     command=self._toggle_auto_scroll)
        btn_scroll.pack(side=tk.RIGHT, padx=(0, 5))
        
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
        # Category tags for backend source modules
        self.log_text.tag_configure("SRC_OSC", foreground="#6EC6FF")       # OSC data
        self.log_text.tag_configure("SRC_WS", foreground="#A78BFA")        # WebSocket
        self.log_text.tag_configure("SRC_POWER", foreground="#F59E0B")     # Power/strength
        self.log_text.tag_configure("SRC_WAVE", foreground="#34D399")      # Wave patterns
        self.log_text.tag_configure("SRC_BOOST", foreground="#FB923C")     # Boost events
        self.log_text.tag_configure("SRC_DEVICE", foreground="#C084FC")    # Device connection
    
    def _toggle_auto_scroll(self):
        self.auto_scroll = self.auto_scroll_var.get()
    
    def _get_source_tag(self, message):
        """Determine source tag based on message content"""
        msg_lower = message.lower()
        if any(k in msg_lower for k in ('osc ', 'vrcosc', 'avatar_param', 'osc listen')):
            return "SRC_OSC"
        if any(k in msg_lower for k in ('websocket', 'ws conn', 'ws id', 'wsid', 'heartbeat', 'hb')):
            return "SRC_WS"
        if any(k in msg_lower for k in ('strength', 'power', 'device_limit', 'set strength', 'device limit')):
            return "SRC_POWER"
        if any(k in msg_lower for k in ('wave', 'pulse', 'sending [', 'sending "')):
            return "SRC_WAVE"
        if any(k in msg_lower for k in ('boost', 'impact!', 'impact detect', 'decay')):
            return "SRC_BOOST"
        if any(k in msg_lower for k in ('connect', 'disconnect', 'closed', 'bind', 'device', 'keep-alive')):
            return "SRC_DEVICE"
        return None
    
    def _on_log(self, log_entry):
        """Handle new log entry with rich formatting"""
        try:
            self.log_text.configure(state=tk.NORMAL)
            
            # Timestamp
            self.log_text.insert(tk.END, f"{log_entry['timestamp']} ", "TIME")
            
            # Level badge
            level = log_entry['level']
            self.log_text.insert(tk.END, f"{level:<7} ", level)
            
            # Message with source color
            message = log_entry['message']
            source_tag = self._get_source_tag(message)
            if source_tag:
                self.log_text.insert(tk.END, f"{message}\n", source_tag)
            else:
                self.log_text.insert(tk.END, f"{message}\n")
            
            # Auto-scroll
            if self.auto_scroll:
                self.log_text.see(tk.END)
            
            # Trim old logs
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
        self.btn_advanced.pack(side=tk.LEFT)
        
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
            self.btn_basic.configure(bg=NothingPhoneStyle.ACCENT_RED,
                                     fg=NothingPhoneStyle.TEXT_PRIMARY)
            self.btn_advanced.configure(bg=NothingPhoneStyle.BG_TERTIARY,
                                        fg=NothingPhoneStyle.TEXT_SECONDARY)
        else:
            self.btn_advanced.configure(bg=NothingPhoneStyle.ACCENT_RED,
                                        fg=NothingPhoneStyle.TEXT_PRIMARY)
            self.btn_basic.configure(bg=NothingPhoneStyle.BG_TERTIARY,
                                     fg=NothingPhoneStyle.TEXT_SECONDARY)
        self._reload_config()
    
    def _get_current_filename(self):
        return CONFIG_FILENAME_BASIC if self.current_file == "basic" else CONFIG_FILENAME
    
    def _reload_config(self):
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
                # Set n_derivative for touch mode (IMPACT/RECOIL patterns)
                n_derivative = self.settings_basic['dglab3'][chann].get('n_derivative', 0)
                self.settings['dglab3'][chann]['mode_config']['touch']['n_derivative'] = n_derivative
            
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
                    
                    # If current strength exceeds new limit, clamp it
                    current = conn.strength.get(channel.upper(), 0)
                    limit = conn.get_upper_strength(channel.upper())
                    
                    if current > limit:
                        self.on_log.info(f"Clamping Channel {channel} strength from {current} to {limit}")
                        await conn.set_strength(channel.upper(), value=limit)
                        
            except Exception as e:
                self.on_log.error(f"Failed to update connections: {str(e)}")
                
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(_update_connections(), self.loop)
    
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
    
    def send_wakeup_pulse(self, channel):
        """Send a small wake-up pulse when power level changes"""
        if not self.running or not self.loop or not self.dg_connection:
            return
        
        async def do_wakeup():
            try:
                await self.dg_connection.broadcast_wakeup_pulse(channel=channel.upper())
                self.on_log.info(f"Wake-up pulse sent to Channel {channel}")
            except Exception as e:
                self.on_log.error(f"Wake-up pulse failed: {str(e)}")
        
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(do_wakeup(), self.loop)


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
        
        # Flag to prevent recursive slider updates
        self._updating_sliders = False
        
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
        
        # Left column - Controls & Config (with scroll)
        left_column_outer = tk.Frame(content, bg=NothingPhoneStyle.BG_PRIMARY)
        left_column_outer.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        # Create scrollable container
        self.left_canvas = tk.Canvas(left_column_outer, bg=NothingPhoneStyle.BG_PRIMARY, 
                                     highlightthickness=0)
        left_scrollbar = ModernScrollbar(left_column_outer, orient=tk.VERTICAL,
                                        command=self.left_canvas.yview,
                                        bg=NothingPhoneStyle.BG_PRIMARY,
                                        trough_color=NothingPhoneStyle.BG_PRIMARY,
                                        thumb_color=NothingPhoneStyle.BG_TERTIARY,
                                        active_color=NothingPhoneStyle.ACCENT_RED,
                                        width=10)
        
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Inner frame for content
        left_column = tk.Frame(self.left_canvas, bg=NothingPhoneStyle.BG_PRIMARY)
        self.left_canvas_window = self.left_canvas.create_window((0, 0), window=left_column, anchor='nw')
        
        # Bind scroll events
        def _on_left_canvas_configure(event):
            self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
            # Match inner frame width to canvas width
            self.left_canvas.itemconfig(self.left_canvas_window, width=event.width)
        
        self.left_canvas.bind('<Configure>', _on_left_canvas_configure)
        
        # Bind mouse wheel for scrolling
        def _on_mousewheel(event):
            self.left_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            self.left_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            self.left_canvas.unbind_all("<MouseWheel>")
        
        left_column.bind('<Enter>', _bind_mousewheel)
        left_column.bind('<Leave>', _unbind_mousewheel)
        
        # Power controls card
        power_card = tk.Frame(left_column, bg=NothingPhoneStyle.BG_SECONDARY)
        power_card.pack(fill=tk.X, pady=(0, 10))
        
        self.slider_a = PowerSlider(power_card, "CHANNEL A LIMIT", "A",
                                    min_val=0, max_val=200,
                                    initial=min(200, self.settings_basic.get('dglab3', {}).get('channel_a', {}).get('device_limit', 
                                                self.settings_basic.get('dglab3', {}).get('channel_a', {}).get('strength_limit', 100))),
                                    callback=self._on_strength_change,
                                    test_shock_callback=self._on_test_shock,
                                    fonts=self.fonts,
                                    compact=True)
        self.slider_a.pack(fill=tk.X)
        
        sep = tk.Frame(power_card, height=1, bg=NothingPhoneStyle.BORDER_COLOR)
        sep.pack(fill=tk.X, padx=10)
        
        self.slider_b = PowerSlider(power_card, "CHANNEL B LIMIT", "B",
                                    min_val=0, max_val=200,
                                    initial=min(200, self.settings_basic.get('dglab3', {}).get('channel_b', {}).get('device_limit',
                                                self.settings_basic.get('dglab3', {}).get('channel_b', {}).get('strength_limit', 100))),
                                    callback=self._on_strength_change,
                                    test_shock_callback=self._on_test_shock,
                                    fonts=self.fonts,
                                    compact=True)
        self.slider_b.pack(fill=tk.X)
        
        # Pattern selector panel
        self.pattern_panel = PatternPanel(
            left_column,
            settings_basic=self.settings_basic,
            callback=self._on_pattern_change,
            settings_callback=self._on_setting_change,
            fonts=self.fonts
        )
        self.pattern_panel.pack(fill=tk.X, pady=(10, 0))
        
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
        """Handle strength slider change - updates device_limit and syncs with pattern panel"""
        if self._updating_sliders:
            return
        
        channel_key = f"channel_{channel.lower()}"
        try:
            self._updating_sliders = True
            
            # Update both strength_limit (for compatibility) and device_limit
            self.settings_basic['dglab3'][channel_key]['strength_limit'] = value
            self.settings_basic['dglab3'][channel_key]['device_limit'] = value
            
            # Sync with pattern panel (without triggering callback)
            if channel == 'A':
                self.pattern_panel.pattern_a.device_limit.set(value)
                self.pattern_panel.pattern_a.limit_value_label.configure(text=f"{value}")
            else:
                self.pattern_panel.pattern_b.device_limit.set(value)
                self.pattern_panel.pattern_b.limit_value_label.configure(text=f"{value}")
            
            # Update runtime settings
            self._update_runtime_setting(channel, 'device_limit', value)
            
            # Auto-save to file
            with open(CONFIG_FILENAME_BASIC, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.settings_basic, f, allow_unicode=True)
            
            # Update running server if available
            if self.server_manager:
                self.server_manager.settings_basic = self.settings_basic
                self.server_manager.update_strength_limit(channel, value)
                # Send wake-up pulse to keep device active
                self.server_manager.send_wakeup_pulse(channel)
                
            gui_logger.info(f"Channel {channel} device limit: {value}")
        except Exception as e:
            gui_logger.error(f"Error updating strength: {e}")
        finally:
            self._updating_sliders = False
    
    def _on_pattern_change(self, channel, pattern_name, pattern_config, settings):
        """Handle pattern mode change for a channel - real-time update"""
        channel_key = f"channel_{channel.lower()}"
        try:
            # Update settings
            self.settings_basic['dglab3'][channel_key]['mode'] = pattern_config['mode']
            self.settings_basic['dglab3'][channel_key]['n_derivative'] = pattern_config['n_derivative']
            self.settings_basic['dglab3'][channel_key]['device_limit'] = settings['device_limit']
            self.settings_basic['dglab3'][channel_key]['sensitivity'] = settings['sensitivity']
            self.settings_basic['dglab3'][channel_key]['threshold'] = settings['threshold']
            self.settings_basic['dglab3'][channel_key]['impact_boost_min'] = settings['impact_boost_min']
            self.settings_basic['dglab3'][channel_key]['impact_boost_max'] = settings['impact_boost_max']
            
            # Update runtime settings for real-time effect
            self._update_runtime_pattern_settings(channel, pattern_name, settings)
            
            # Auto-save to file
            with open(CONFIG_FILENAME_BASIC, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.settings_basic, f, allow_unicode=True)
            
            # Refresh config editor if on basic view
            if self.config_editor.current_file == "basic":
                self.config_editor._reload_config()
            
            gui_logger.success(f"Channel {channel} pattern: {pattern_name}")
            
        except Exception as e:
            gui_logger.error(f"Error updating pattern: {e}")
    
    def _on_setting_change(self, channel, setting_name, value):
        """Handle settings slider change - real-time update"""
        if self._updating_sliders:
            return
            
        channel_key = f"channel_{channel.lower()}"
        try:
            self._updating_sliders = True
            
            # Update settings
            self.settings_basic['dglab3'][channel_key][setting_name] = value
            
            # If device_limit changed, also sync with main slider and strength_limit
            if setting_name == 'device_limit':
                self.settings_basic['dglab3'][channel_key]['strength_limit'] = value
                # Sync with main power slider (without triggering callback)
                if channel == 'A':
                    self.slider_a.value.set(value)
                    self.slider_a._draw_slider()
                else:
                    self.slider_b.value.set(value)
                    self.slider_b._draw_slider()
                # Send wake-up pulse
                if self.server_manager:
                    self.server_manager.send_wakeup_pulse(channel)
            
            # Update runtime settings for real-time effect
            self._update_runtime_setting(channel, setting_name, value)
            
            # Auto-save to file
            with open(CONFIG_FILENAME_BASIC, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.settings_basic, f, allow_unicode=True)
            
            if setting_name == 'device_limit':
                gui_logger.info(f"Channel {channel} device limit: {value}")
            elif setting_name == 'sensitivity':
                gui_logger.info(f"Channel {channel} sensitivity: {value}%")
            elif setting_name == 'threshold':
                gui_logger.info(f"Channel {channel} threshold: {value}%")
            elif setting_name == 'impact_boost_min':
                gui_logger.info(f"Channel {channel} random boost min: +{value}")
            elif setting_name == 'impact_boost_max':
                gui_logger.info(f"Channel {channel} random boost max: +{value}")
            
        except Exception as e:
            gui_logger.error(f"Error updating setting: {e}")
        finally:
            self._updating_sliders = False
    
    def _update_runtime_pattern_settings(self, channel, pattern_name, settings):
        """Update runtime pattern settings in shock handler"""
        try:
            from srv.handler.shock_handler import RUNTIME_PATTERN_SETTINGS
            RUNTIME_PATTERN_SETTINGS[channel.upper()] = {
                'pattern': pattern_name,
                'device_limit': settings['device_limit'],
                'sensitivity': settings['sensitivity'],
                'threshold': settings['threshold'],
                'impact_boost_min': settings.get('impact_boost_min', 0),
                'impact_boost_max': settings.get('impact_boost_max', 30),
            }
        except ImportError:
            pass  # Server not started yet
    
    def _update_runtime_setting(self, channel, setting_name, value):
        """Update runtime setting value in shock handler"""
        try:
            from srv.handler.shock_handler import RUNTIME_PATTERN_SETTINGS
            RUNTIME_PATTERN_SETTINGS[channel.upper()][setting_name] = value
        except (ImportError, KeyError):
            pass  # Server not started yet
    
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
                # Update pattern panel based on saved config
                self._update_pattern_from_config('A', config_data)
                self._update_pattern_from_config('B', config_data)
            except:
                pass
        else:
            self.settings = config_data
            self._update_qr()
    
    def _update_pattern_from_config(self, channel, config_data):
        """Update pattern panel based on config data"""
        channel_key = f'channel_{channel.lower()}'
        channel_config = config_data.get('dglab3', {}).get(channel_key, {})
        mode = channel_config.get('mode', 'distance')
        n_derivative = channel_config.get('n_derivative', 0)
        device_limit = channel_config.get('device_limit', 100)
        sensitivity = channel_config.get('sensitivity', 100)
        threshold = channel_config.get('threshold', 10)
        impact_boost_min = channel_config.get('impact_boost_min', 0)
        impact_boost_max = channel_config.get('impact_boost_max', 30)
        
        # Determine pattern from mode and n_derivative
        if mode == 'distance':
            pattern = 'PROXIMITY'
        elif mode == 'touch':
            if n_derivative == 1:
                pattern = 'IMPACT'
            elif n_derivative >= 2:
                pattern = 'RECOIL'
            else:
                pattern = 'PROXIMITY'
        else:
            pattern = 'PROXIMITY'
        
        settings = {
            'device_limit': device_limit,
            'sensitivity': sensitivity,
            'threshold': threshold,
            'impact_boost_min': impact_boost_min,
            'impact_boost_max': impact_boost_max
        }
        
        # Update the pattern panel
        if channel == 'A':
            self.pattern_panel.pattern_a.set_pattern(pattern)
            self.pattern_panel.pattern_a.set_settings(device_limit, sensitivity, threshold, 
                                                       impact_boost_min, impact_boost_max)
        else:
            self.pattern_panel.pattern_b.set_pattern(pattern)
            self.pattern_panel.pattern_b.set_settings(device_limit, sensitivity, threshold,
                                                       impact_boost_min, impact_boost_max)
        
        # Update runtime settings
        self._update_runtime_pattern_settings(channel, pattern, settings)
    
    def _start_server(self):
        """Start the integrated server"""
        try:
            # Connect loguru to GUI so backend logs appear in log panel
            gui_logger.connect_loguru()
            
            # Initialize runtime pattern settings before starting server
            self._init_runtime_pattern_settings()
            
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
    
    def _init_runtime_pattern_settings(self):
        """Initialize runtime pattern settings from current config"""
        for channel in ['A', 'B']:
            channel_key = f'channel_{channel.lower()}'
            channel_config = self.settings_basic.get('dglab3', {}).get(channel_key, {})
            
            mode = channel_config.get('mode', 'distance')
            n_derivative = channel_config.get('n_derivative', 0)
            device_limit = channel_config.get('device_limit', 100)
            sensitivity = channel_config.get('sensitivity', 100)
            threshold = channel_config.get('threshold', 10)
            impact_boost_min = channel_config.get('impact_boost_min', 0)
            impact_boost_max = channel_config.get('impact_boost_max', 30)
            
            # Determine pattern
            if mode == 'distance':
                pattern = 'PROXIMITY'
            elif mode == 'touch':
                if n_derivative == 1:
                    pattern = 'IMPACT'
                elif n_derivative >= 2:
                    pattern = 'RECOIL'
                else:
                    pattern = 'PROXIMITY'
            else:
                pattern = 'PROXIMITY'
            
            settings = {
                'device_limit': device_limit,
                'sensitivity': sensitivity,
                'threshold': threshold,
                'impact_boost_min': impact_boost_min,
                'impact_boost_max': impact_boost_max
            }
            self._update_runtime_pattern_settings(channel, pattern, settings)
    
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
