import os
import sys
import time
import argparse
import threading
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk, ImageFilter
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk


class ModernFractalVisualizer:
    def __init__(self, output_file_path, palette="grayscale", width=128, height=128):
        self.output_file_path = output_file_path
        self.palette_name = palette
        self.width = width
        self.height = height
        self.pixels_read = 0
        self.total_pixels = self.width * self.height
        self.image_data = np.zeros((self.height, self.width), dtype=np.uint8)
        self.running = True
        self.file_position = 0
        self.photo_image = None
        self.is_processing = False
        self.last_update_time = 0
        
        # Color scheme - AMOLED with purple accent
        self.colors = {
            'bg': '#000000',           # Pure black for AMOLED
            'surface': '#0a0a0a',      # Very dark surface
            'surface_variant': '#1a1a1a',  # Slightly lighter surface
            'primary': '#8b5cf6',      # Purple accent
            'primary_variant': '#7c3aed',  # Darker purple
            'secondary': '#a855f7',    # Light purple
            'text_primary': '#ffffff',  # Pure white text
            'text_secondary': '#b3b3b3', # Dimmed white
            'text_tertiary': '#666666', # More dimmed
            'success': '#10b981',      # Green for success
            'warning': '#f59e0b',      # Orange for warning
            'error': '#ef4444',        # Red for error
        }
        
        self._prepare_palettes()
        self._setup_ui()
        
        # Start monitoring in a separate thread for better performance
        self.monitor_thread = threading.Thread(target=self._monitor_file_thread, daemon=True)
        self.monitor_thread.start()

    def _prepare_palettes(self):
        """Prepare optimized color palettes using numpy for fast indexing"""
        
        def create_grayscale():
            return np.array([(i, i, i) for i in range(256)], dtype=np.uint8)
        
        def create_fire():
            palette = []
            for i in range(256):
                if i < 64:
                    # Black to red
                    r, g, b = i * 4, 0, 0
                elif i < 128:
                    # Red to yellow
                    r, g, b = 255, (i - 64) * 4, 0
                elif i < 192:
                    # Yellow to white
                    r, g, b = 255, 255, (i - 128) * 4
                else:
                    # White variations
                    r, g, b = 255, 255, 255 - (i - 192)
                palette.append((min(255, r), min(255, g), min(255, b)))
            return np.array(palette, dtype=np.uint8)
        
        def create_ocean():
            palette = []
            for i in range(256):
                if i < 85:
                    # Deep blue
                    r, g, b = 0, 0, i * 3
                elif i < 170:
                    # Blue to cyan
                    r, g, b = 0, (i - 85) * 3, 255
                else:
                    # Cyan to white
                    r, g, b = (i - 170) * 3, 255, 255
                palette.append((min(255, r), min(255, g), min(255, b)))
            return np.array(palette, dtype=np.uint8)
        
        def create_rainbow():
            palette = []
            for i in range(256):
                # HSV to RGB conversion for smooth rainbow
                h = i / 255.0 * 360
                s = 1.0
                v = 1.0
                
                c = v * s
                x = c * (1 - abs((h / 60) % 2 - 1))
                m = v - c
                
                if 0 <= h < 60:
                    r, g, b = c, x, 0
                elif 60 <= h < 120:
                    r, g, b = x, c, 0
                elif 120 <= h < 180:
                    r, g, b = 0, c, x
                elif 180 <= h < 240:
                    r, g, b = 0, x, c
                elif 240 <= h < 300:
                    r, g, b = x, 0, c
                else:
                    r, g, b = c, 0, x
                
                r, g, b = int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)
                palette.append((r, g, b))
            return np.array(palette, dtype=np.uint8)
        
        def create_plasma():
            palette = []
            for i in range(256):
                # Plasma-like colors
                t = i / 255.0
                r = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * t)))
                g = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * t + 2 * np.pi / 3)))
                b = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * t + 4 * np.pi / 3)))
                palette.append((r, g, b))
            return np.array(palette, dtype=np.uint8)
        
        def create_viridis():
            # Viridis colormap approximation
            palette = []
            for i in range(256):
                t = i / 255.0
                r = int(255 * (0.267 + 0.973 * t - 0.686 * t**2))
                g = int(255 * (0.005 + 1.420 * t - 0.680 * t**2))
                b = int(255 * (0.329 + 0.725 * t - 0.520 * t**2))
                r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
                palette.append((r, g, b))
            return np.array(palette, dtype=np.uint8)
        
        self.color_palettes = {
            "grayscale": create_grayscale(),
            "fire": create_fire(),
            "ocean": create_ocean(),
            "rainbow": create_rainbow(),
            "plasma": create_plasma(),
            "viridis": create_viridis(),
        }
        
        if self.palette_name not in self.color_palettes:
            self.palette_name = "grayscale"
        
        self.current_palette = self.color_palettes[self.palette_name]

    def _setup_ui(self):
        """Setup the modern UI with AMOLED theme"""
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Fractal Visualizer")
        self.root.configure(fg_color=self.colors['bg'])
        
        # Make window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors['bg'], corner_radius=0)
        main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Header
        self._create_header(main_container)
        
        # Content area
        content_frame = ctk.CTkFrame(main_container, fg_color=self.colors['bg'], corner_radius=0)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Left panel (controls)
        self._create_control_panel(content_frame)
        
        # Right panel (visualization)
        self._create_visualization_panel(content_frame)
        
        # Setup window
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600)
        y = (self.root.winfo_screenheight() // 2) - (400)
        self.root.geometry(f"1200x800+{x}+{y}")

    def _create_header(self, parent):
        """Create modern header with title and status"""
        header_frame = ctk.CTkFrame(parent, fg_color=self.colors['surface'], height=80, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Fractal Visualizer",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.grid(row=0, column=0, padx=30, pady=20, sticky="w")
        
        # Status indicator
        self.status_indicator = ctk.CTkFrame(header_frame, fg_color=self.colors['warning'], width=12, height=12, corner_radius=6)
        self.status_indicator.grid(row=0, column=2, padx=(10, 30), pady=20, sticky="e")
        
        # Status text
        self.header_status = ctk.CTkLabel(
            header_frame,
            text="Waiting for data...",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['text_secondary']
        )
        self.header_status.grid(row=0, column=1, padx=10, pady=20, sticky="e")

    def _create_control_panel(self, parent):
        """Create control panel with palette selection and stats"""
        control_frame = ctk.CTkFrame(parent, fg_color=self.colors['surface'], width=300, corner_radius=12)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        control_frame.grid_propagate(False)
        
        # Palette selection
        palette_section = ctk.CTkFrame(control_frame, fg_color=self.colors['surface_variant'], corner_radius=8)
        palette_section.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            palette_section,
            text="Color Palette",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(pady=(15, 10))
        
        self.palette_var = ctk.StringVar(value=self.palette_name)
        self.palette_menu = ctk.CTkOptionMenu(
            palette_section,
            variable=self.palette_var,
            values=list(self.color_palettes.keys()),
            command=self._on_palette_change,
            fg_color=self.colors['primary'],
            button_color=self.colors['primary_variant'],
            button_hover_color=self.colors['secondary'],
            text_color=self.colors['text_primary'],
            font=ctk.CTkFont(size=12)
        )
        self.palette_menu.pack(pady=(0, 15), padx=15, fill="x")
        
        # Progress section
        progress_section = ctk.CTkFrame(control_frame, fg_color=self.colors['surface_variant'], corner_radius=8)
        progress_section.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            progress_section,
            text="Progress",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(pady=(15, 10))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_section,
            progress_color=self.colors['primary'],
            fg_color=self.colors['bg'],
            height=8
        )
        self.progress_bar.pack(pady=(0, 10), padx=15, fill="x")
        self.progress_bar.set(0)
        
        # Progress text
        self.progress_text = ctk.CTkLabel(
            progress_section,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['primary']
        )
        self.progress_text.pack(pady=(0, 15))
        
        # Stats section
        stats_section = ctk.CTkFrame(control_frame, fg_color=self.colors['surface_variant'], corner_radius=8)
        stats_section.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            stats_section,
            text="Statistics",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(pady=(15, 10))
        
        # Stats labels
        self.pixels_label = ctk.CTkLabel(
            stats_section,
            text=f"Pixels: 0 / {self.total_pixels:,}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.pixels_label.pack(pady=(0, 5))
        
        self.dimensions_label = ctk.CTkLabel(
            stats_section,
            text=f"Dimensions: {self.width} × {self.height}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.dimensions_label.pack(pady=(0, 5))
        
        self.file_label = ctk.CTkLabel(
            stats_section,
            text=f"File: {os.path.basename(self.output_file_path)}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_secondary']
        )
        self.file_label.pack(pady=(0, 15))
        
        # Control buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="Refresh",
            command=self._on_refresh,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_variant'],
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.refresh_btn.pack(fill="x", pady=(0, 10))
        
        self.save_btn = ctk.CTkButton(
            button_frame,
            text="Save Image",
            command=self._save_image,
            fg_color=self.colors['success'],
            hover_color=self._adjust_color(self.colors['success'], 0.8),
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.save_btn.pack(fill="x")

    def _create_visualization_panel(self, parent):
        """Create visualization panel with canvas"""
        viz_frame = ctk.CTkFrame(parent, fg_color=self.colors['surface'], corner_radius=12)
        viz_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas container
        canvas_container = ctk.CTkFrame(viz_frame, fg_color=self.colors['bg'], corner_radius=8)
        canvas_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)
        
        # Canvas
        self.canvas = tk.Canvas(
            canvas_container,
            bg=self.colors['bg'],
            highlightthickness=0,
            bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        if hasattr(self, 'photo_image') and self.photo_image:
            self._update_canvas_display()

    def _on_palette_change(self, palette_name):
        """Handle palette change"""
        self.palette_name = palette_name
        self.current_palette = self.color_palettes[palette_name]
        self._update_display()

    def _on_refresh(self):
        """Handle refresh button click"""
        self.pixels_read = 0
        self.file_position = 0
        self.image_data.fill(0)
        self._update_ui_state()
        self.canvas.delete("all")

    def _monitor_file_thread(self):
        """Monitor file in separate thread"""
        while self.running:
            try:
                if os.path.exists(self.output_file_path):
                    self._read_file_data()
                time.sleep(0.05)  # 50ms polling interval
            except Exception as e:
                print(f"Error monitoring file: {e}", file=sys.stderr)
                time.sleep(0.1)

    def _read_file_data(self):
        """Read new data from file with optimized buffering"""
        try:
            with open(self.output_file_path, 'r') as f:
                f.seek(self.file_position)
                # Read in chunks for better performance
                chunk = f.read(8192)
                if chunk:
                    lines = chunk.splitlines()
                    # Handle partial lines
                    if not chunk.endswith('\n') and len(lines) > 1:
                        # Put back the last incomplete line
                        incomplete_line = lines[-1]
                        lines = lines[:-1]
                        f.seek(f.tell() - len(incomplete_line))
                    
                    new_pixels = []
                    for line in lines:
                        line = line.strip()
                        if line and line.isdigit():
                            pixel_value = max(0, min(255, int(line)))
                            new_pixels.append(pixel_value)
                    
                    if new_pixels:
                        self._process_new_pixels(new_pixels)
                    
                    self.file_position = f.tell()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)

    def _process_new_pixels(self, new_pixels):
        """Process new pixels with batch updates"""
        for pixel_value in new_pixels:
            if self.pixels_read >= self.total_pixels:
                break
            
            y = self.pixels_read // self.width
            x = self.pixels_read % self.width
            
            if y < self.height and x < self.width:
                self.image_data[y, x] = pixel_value
                self.pixels_read += 1
        
        # Update UI periodically (not for every pixel)
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:  # Update every 100ms
            self.root.after_idle(self._update_ui_state)
            self.last_update_time = current_time
        
        if self.pixels_read >= self.total_pixels:
            self.root.after_idle(self._on_completion)

    def _update_ui_state(self):
        """Update UI state and display"""
        # Update progress
        progress = self.pixels_read / self.total_pixels
        self.progress_bar.set(progress)
        self.progress_text.configure(text=f"{int(progress * 100)}%")
        
        # Update stats
        self.pixels_label.configure(text=f"Pixels: {self.pixels_read:,} / {self.total_pixels:,}")
        
        # Update status
        if self.pixels_read == 0:
            self.header_status.configure(text="Waiting for data...")
            self.status_indicator.configure(fg_color=self.colors['warning'])
        elif self.pixels_read >= self.total_pixels:
            self.header_status.configure(text="Complete")
            self.status_indicator.configure(fg_color=self.colors['success'])
        else:
            current_row = self.pixels_read // self.width
            self.header_status.configure(text=f"Processing row {current_row + 1}/{self.height}")
            self.status_indicator.configure(fg_color=self.colors['primary'])
        
        # Update display
        self._update_display()

    def _update_display(self):
        """Update the fractal display with current data"""
        if self.pixels_read == 0:
            return
        
        # Calculate visible rows
        visible_rows = min(self.height, (self.pixels_read + self.width - 1) // self.width)
        if visible_rows == 0:
            return
        
        # Create RGB image from current data
        visible_data = self.image_data[:visible_rows, :]
        rgb_image = self.current_palette[visible_data]
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image, mode='RGB')
        
        # Apply smoothing for better visual quality
        if visible_rows > 1:
            pil_image = pil_image.filter(ImageFilter.SMOOTH_MORE)
        
        self.photo_image = pil_image
        self._update_canvas_display()

    def _update_canvas_display(self):
        """Update canvas with current image"""
        if not self.photo_image:
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Calculate scaling to fit canvas while maintaining aspect ratio
        img_width, img_height = self.photo_image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y) * 0.9  # Leave some margin
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize image
        scaled_image = self.photo_image.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage and display
        self.tk_image = ImageTk.PhotoImage(scaled_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2, canvas_height // 2,
            image=self.tk_image
        )

    def _on_completion(self):
        """Handle completion of fractal generation"""
        self.header_status.configure(text="Complete")
        self.status_indicator.configure(fg_color=self.colors['success'])
        self.progress_bar.set(1.0)
        self.progress_text.configure(text="100%")
        
        # Auto-save if not already saved
        self._save_image()

    def _save_image(self):
        """Save the current fractal image"""
        if self.pixels_read == 0:
            return
        
        try:
            # Create full RGB image
            rgb_image = self.current_palette[self.image_data]
            final_image = Image.fromarray(rgb_image, mode='RGB')
            
            # Create output directory
            output_dir = os.path.dirname(self.output_file_path) or os.getcwd()
            images_dir = os.path.join(output_dir, "fractals")
            os.makedirs(images_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fractal_{self.palette_name}_{timestamp}.png"
            filepath = os.path.join(images_dir, filename)
            
            # Save with high quality
            final_image.save(filepath, "PNG", optimize=True)
            
            print(f"Fractal saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving image: {e}", file=sys.stderr)

    def _adjust_color(self, color, factor):
        """Adjust color brightness"""
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
        return f"#{r:02x}{g:02x}{b:02x}"

    def run(self):
        """Run the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}", file=sys.stderr)

    def _on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.quit()
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description='Modern Real-time Fractal Visualizer')
    parser.add_argument('output_file', help='Path to the output file with pixel values')
    parser.add_argument('--palette', '-p', default='grayscale',
                        choices=['grayscale', 'fire', 'ocean', 'rainbow', 'plasma', 'viridis'],
                        help='Initial color palette')
    parser.add_argument('--width', type=int, default=128, help='Fractal width in pixels')
    parser.add_argument('--height', type=int, default=128, help='Fractal height in pixels')
    
    args = parser.parse_args()
    
    try:
        visualizer = ModernFractalVisualizer(
            args.output_file,
            palette=args.palette,
            width=args.width,
            height=args.height
        )
        visualizer.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()