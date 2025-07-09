import os
import sys
import time
import argparse
import threading
import numpy as np
from datetime import datetime
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import customtkinter as ctk
import tkinter as tk
from scipy import ndimage
import subprocess


class EnhancedFractalVisualizer:
    def __init__(self, output_file_path, palette="viridis", width=256, height=256):
        self.output_file_path = output_file_path
        self.palette_name = palette
        self.width = width
        self.height = height
        self.pixels_read = 0
        self.total_pixels = self.width * self.height
        self.image_data = np.zeros((self.height, self.width), dtype=np.float32)
        self.running = True
        self.file_position = 0
        self.photo_image = None
        self.last_update_time = 0
        
        # Enhanced color scheme
        self.colors = {
            'bg': '#0a0a0a', 'surface': '#1a1a1a', 'primary': '#8b5cf6',
            'secondary': '#06b6d4', 'text_primary': '#ffffff', 'text_secondary': '#a3a3a3',
            'success': '#10b981', 'warning': '#f59e0b', 'error': '#ef4444'
        }
        
        self._setup_palettes()
        self._setup_ui()
        
        self.monitor_thread = threading.Thread(target=self._monitor_file, daemon=True)
        self.monitor_thread.start()

    def _setup_palettes(self):
        """Setup enhanced artistic color palettes"""
        def create_palette(colors, name):
            if name == "plasma":
                t = np.linspace(0, 1, 256)
                r = np.clip(255 * (0.05 + 0.5 * np.sin(2 * np.pi * t + 0.5)), 0, 255)
                g = np.clip(255 * (0.3 + 0.7 * np.sin(2 * np.pi * t + 1.5)), 0, 255)
                b = np.clip(255 * (0.8 + 0.2 * np.sin(2 * np.pi * t + 2.5)), 0, 255)
            elif name == "cosmic":
                t = np.linspace(0, 1, 256)
                r = np.clip(255 * (0.1 + 0.9 * t**2), 0, 255)
                g = np.clip(255 * (0.2 + 0.8 * np.sin(np.pi * t)), 0, 255)
                b = np.clip(255 * (0.9 - 0.5 * t), 0, 255)
            elif name == "fire":
                t = np.linspace(0, 1, 256)
                r = np.clip(255 * np.minimum(1, 4 * t), 0, 255)
                g = np.clip(255 * np.maximum(0, 4 * t - 1), 0, 255)
                b = np.clip(255 * np.maximum(0, 4 * t - 3), 0, 255)
            else:  # viridis
                t = np.linspace(0, 1, 256)
                r = np.clip(255 * (0.267 + 0.973 * t - 0.686 * t**2), 0, 255)
                g = np.clip(255 * (0.005 + 1.420 * t - 0.680 * t**2), 0, 255)
                b = np.clip(255 * (0.329 + 0.725 * t - 0.520 * t**2), 0, 255)
            
            return np.column_stack([r, g, b]).astype(np.uint8)
        
        self.palettes = {
            "viridis": create_palette(None, "viridis"),
            "plasma": create_palette(None, "plasma"),
            "cosmic": create_palette(None, "cosmic"),
            "fire": create_palette(None, "fire")
        }
        
        self.current_palette = self.palettes.get(self.palette_name, self.palettes["viridis"])

    def _setup_ui(self):
        """Setup enhanced UI"""
        ctk.set_appearance_mode("dark")
        
        self.root = ctk.CTk()
        self.root.title("Enhanced Fractal Visualizer")
        self.root.configure(fg_color=self.colors['bg'])
        self.root.geometry("1400x900")
        
        # Main layout
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel
        left_panel = ctk.CTkFrame(main_frame, width=350, fg_color=self.colors['surface'])
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(left_panel, text="Fractal Visualizer", 
                           font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Dimensions control
        dims_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        dims_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(dims_frame, text="Dimensions", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        dim_controls = ctk.CTkFrame(dims_frame, fg_color="transparent")
        dim_controls.pack(fill="x", pady=5)
        
        ctk.CTkLabel(dim_controls, text="Width:").pack(side="left")
        self.width_entry = ctk.CTkEntry(dim_controls, width=60, placeholder_text=str(self.width))
        self.width_entry.pack(side="left", padx=5)
        self.width_entry.insert(0, str(self.width))
        
        ctk.CTkLabel(dim_controls, text="Height:").pack(side="left", padx=(10, 0))
        self.height_entry = ctk.CTkEntry(dim_controls, width=60, placeholder_text=str(self.height))
        self.height_entry.pack(side="left", padx=5)
        self.height_entry.insert(0, str(self.height))
        
        apply_btn = ctk.CTkButton(dims_frame, text="Apply Dimensions", 
                                command=self._apply_dimensions, height=32)
        apply_btn.pack(pady=10)
        
        # Palette selection
        palette_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        palette_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(palette_frame, text="Color Palette", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.palette_var = ctk.StringVar(value=self.palette_name)
        palette_menu = ctk.CTkOptionMenu(palette_frame, variable=self.palette_var,
                                       values=list(self.palettes.keys()),
                                       command=self._change_palette)
        palette_menu.pack(pady=10, fill="x", padx=10)
        
        # Enhancement controls
        enhance_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        enhance_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(enhance_frame, text="Enhancement", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.sharpness_var = ctk.DoubleVar(value=2.0)
        ctk.CTkLabel(enhance_frame, text="Sharpness:").pack()
        sharpness_slider = ctk.CTkSlider(enhance_frame, from_=0.5, to=5.0, 
                                       variable=self.sharpness_var, command=self._update_display)
        sharpness_slider.pack(fill="x", padx=10, pady=5)
        
        self.contrast_var = ctk.DoubleVar(value=1.5)
        ctk.CTkLabel(enhance_frame, text="Contrast:").pack()
        contrast_slider = ctk.CTkSlider(enhance_frame, from_=0.5, to=3.0,
                                      variable=self.contrast_var, command=self._update_display)
        contrast_slider.pack(fill="x", padx=10, pady=5)
        
        # Progress
        progress_frame = ctk.CTkFrame(left_panel, fg_color=self.colors['bg'])
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(progress_frame, text="Progress", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="0%")
        self.progress_label.pack(pady=5)
        
        # Status
        self.status_label = ctk.CTkLabel(left_panel, text="Waiting for data...", 
                                       font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        refresh_btn = ctk.CTkButton(btn_frame, text="Refresh", command=self._refresh)
        refresh_btn.pack(fill="x", pady=5)
        
        save_btn = ctk.CTkButton(btn_frame, text="Save Image", command=self._save_image,
                               fg_color=self.colors['success'])
        save_btn.pack(fill="x", pady=5)
        
        # Right panel - Canvas
        canvas_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['surface'])
        canvas_frame.pack(side="right", fill="both", expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg=self.colors['bg'], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas.bind('<Configure>', self._on_canvas_resize)

    def _apply_dimensions(self):
        """Apply new dimensions and restart processing"""
        try:
            new_width = int(self.width_entry.get())
            new_height = int(self.height_entry.get())
            
            if new_width > 0 and new_height > 0 and new_width <= 2048 and new_height <= 2048:
                self.width = new_width
                self.height = new_height
                self.total_pixels = self.width * self.height
                self.image_data = np.zeros((self.height, self.width), dtype=np.float32)
                self.pixels_read = 0
                self.file_position = 0
                self.canvas.delete("all")
                self.status_label.configure(text=f"Dimensions updated: {self.width}x{self.height}")
            else:
                self.status_label.configure(text="Invalid dimensions (1-2048)")
        except ValueError:
            self.status_label.configure(text="Invalid dimension values")

    def _change_palette(self, palette_name):
        """Change color palette"""
        self.palette_name = palette_name
        self.current_palette = self.palettes[palette_name]
        self._update_display()

    def _monitor_file(self):
        """Monitor file for changes"""
        while self.running:
            try:
                if os.path.exists(self.output_file_path):
                    self._read_file_data()
                time.sleep(0.05)
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(0.1)

    def _read_file_data(self):
        """Read and process file data"""
        try:
            with open(self.output_file_path, 'r') as f:
                f.seek(self.file_position)
                chunk = f.read(4096)
                
                if chunk:
                    lines = chunk.strip().split('\n')
                    new_pixels = []
                    
                    for line in lines:
                        if line.strip() and line.strip().isdigit():
                            new_pixels.append(int(line.strip()))
                    
                    if new_pixels:
                        self._process_pixels(new_pixels)
                    
                    self.file_position = f.tell()
        except Exception as e:
            print(f"Read error: {e}")

    def _process_pixels(self, pixels):
        """Process new pixel data"""
        for pixel in pixels:
            if self.pixels_read >= self.total_pixels:
                break
            
            y, x = divmod(self.pixels_read, self.width)
            if y < self.height:
                # Normalize to 0-1 range for better processing
                self.image_data[y, x] = pixel / 255.0
                self.pixels_read += 1
        
        # Update UI periodically
        current_time = time.time()
        if current_time - self.last_update_time > 0.1:
            self.root.after_idle(self._update_progress)
            self.last_update_time = current_time

    def _update_progress(self):
        """Update progress and display"""
        progress = self.pixels_read / self.total_pixels
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{int(progress * 100)}%")
        
        if self.pixels_read == 0:
            self.status_label.configure(text="Waiting for data...")
        elif self.pixels_read >= self.total_pixels:
            self.status_label.configure(text="Complete")
        else:
            row = self.pixels_read // self.width
            self.status_label.configure(text=f"Processing row {row + 1}/{self.height}")
        
        self._update_display()

    def _update_display(self, *args):
        """Update fractal display with enhancements"""
        if self.pixels_read == 0:
            return
        
        # Get visible portion
        visible_rows = min(self.height, (self.pixels_read + self.width - 1) // self.width)
        if visible_rows == 0:
            return
        
        # Get data and apply enhancements
        data = self.image_data[:visible_rows, :].copy()
        
        # Apply artistic enhancements
        data = self._enhance_data(data)
        
        # Convert to color image
        indices = np.clip(data * 255, 0, 255).astype(np.uint8)
        rgb_image = self.current_palette[indices]
        
        # Create PIL image
        pil_image = Image.fromarray(rgb_image, 'RGB')
        
        # Apply final enhancements
        pil_image = self._apply_image_enhancements(pil_image)
        
        self.photo_image = pil_image
        self._update_canvas()

    def _enhance_data(self, data):
        """Apply artistic enhancements to data"""
        if data.size == 0:
            return data
        
        # Apply edge enhancement
        try:
            # Gaussian blur for smoothing
            smoothed = ndimage.gaussian_filter(data, sigma=0.5)
            
            # Edge detection
            edges = ndimage.sobel(smoothed)
            
            # Combine original with edges
            enhanced = data + 0.3 * edges
            
            # Normalize
            enhanced = np.clip(enhanced, 0, 1)
            
            # Apply gamma correction for better contrast
            enhanced = np.power(enhanced, 0.8)
            
            return enhanced
        except:
            return data

    def _apply_image_enhancements(self, image):
        """Apply PIL-based enhancements"""
        try:
            # Sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(self.sharpness_var.get())
            
            # Contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.contrast_var.get())
            
            # Slight brightness boost
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            return image
        except:
            return image

    def _update_canvas(self):
        """Update canvas display"""
        if not self.photo_image:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        # Scale to fit canvas
        img_width, img_height = self.photo_image.size
        scale = min(canvas_width / img_width, canvas_height / img_height) * 0.95
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # High-quality resize
        scaled_image = self.photo_image.resize((new_width, new_height), Image.LANCZOS)
        
        self.tk_image = ImageTk.PhotoImage(scaled_image)
        
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.tk_image)

    def _on_canvas_resize(self, event):
        """Handle canvas resize"""
        if hasattr(self, 'photo_image') and self.photo_image:
            self._update_canvas()

    def _refresh(self):
        """Refresh visualization"""
        self.pixels_read = 0
        self.file_position = 0
        self.image_data.fill(0)
        self.canvas.delete("all")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.status_label.configure(text="Refreshed - waiting for data...")

    def _save_image(self):
        """Save enhanced fractal image"""
        if self.pixels_read == 0:
            return
        
        try:
            # Create final enhanced image
            enhanced_data = self._enhance_data(self.image_data)
            indices = np.clip(enhanced_data * 255, 0, 255).astype(np.uint8)
            rgb_image = self.current_palette[indices]
            
            final_image = Image.fromarray(rgb_image, 'RGB')
            final_image = self._apply_image_enhancements(final_image)
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fractal_{self.palette_name}_{timestamp}.png"
            
            output_dir = os.path.dirname(self.output_file_path) or "."
            save_path = os.path.join(output_dir, filename)
            
            final_image.save(save_path, "PNG", optimize=True)
            self.status_label.configure(text=f"Saved: {filename}")
            
        except Exception as e:
            self.status_label.configure(text=f"Save error: {str(e)}")

    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()

    def _on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.quit()


def main():
    parser = argparse.ArgumentParser(description='Enhanced Fractal Visualizer')
    parser.add_argument('output_file', help='Path to pixel data file')
    parser.add_argument('--palette', '-p', default='viridis',
                        choices=['viridis', 'plasma', 'cosmic', 'fire'],
                        help='Color palette')
    parser.add_argument('--width', type=int, default=256, help='Width in pixels')
    parser.add_argument('--height', type=int, default=256, help='Height in pixels')
    
    args = parser.parse_args()
    
    try:
        visualizer = EnhancedFractalVisualizer(
            args.output_file, args.palette, args.width, args.height
        )
        visualizer.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()