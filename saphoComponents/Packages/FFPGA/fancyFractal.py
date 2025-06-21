#!/usr/bin/env python3
"""
fancyFractal.py - Gerador de Imagem Fractal em Tempo Real
Lê dados do arquivo output e gera imagem PNG progressivamente
"""

import sys
import os
import numpy as np
from PIL import Image, ImageDraw
import argparse
import time

class FancyFractal:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.image = Image.new('RGB', (width, height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.pixel_data = {}
        self.max_iterations = 100
        
    def load_fractal_data(self, filepath):
        """Carrega dados do arquivo de saída do CMM"""
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse da linha: valor_iteracao px py
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        iterations = int(float(parts[0]))
                        px = int(float(parts[1]))
                        py = int(float(parts[2]))
                        
                        # Armazena os dados do pixel
                        self.pixel_data[(px, py)] = iterations
                        
                    except (ValueError, IndexError):
                        continue
                        
        except FileNotFoundError:
            print(f"Arquivo não encontrado: {filepath}")
            return False
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return False
            
        return True
    
    def iterations_to_color(self, iterations):
        """Converte número de iterações em cor RGB"""
        if iterations == 0:
            return (0, 0, 0)  # Preto para pontos no conjunto
            
        # Normaliza as iterações
        normalized = iterations / self.max_iterations
        
        # Esquema de cores suave e bonito
        if normalized < 0.16:
            # Azul escuro para roxo
            r = int(25 + normalized * 6.25 * 50)
            g = int(25 + normalized * 6.25 * 7)
            b = int(112 + normalized * 6.25 * 100)
        elif normalized < 0.42:
            # Roxo para magenta
            factor = (normalized - 0.16) / 0.26
            r = int(75 + factor * 100)
            g = int(32 + factor * 68)
            b = int(212 - factor * 80)
        elif normalized < 0.6425:
            # Magenta para laranja
            factor = (normalized - 0.42) / 0.2225
            r = int(175 + factor * 80)
            g = int(100 + factor * 55)
            b = int(132 - factor * 132)
        elif normalized < 0.8575:
            # Laranja para amarelo
            factor = (normalized - 0.6425) / 0.215
            r = int(255)
            g = int(155 + factor * 100)
            b = int(factor * 50)
        else:
            # Amarelo para branco
            factor = (normalized - 0.8575) / 0.1425
            r = int(255)
            g = int(255)
            b = int(50 + factor * 205)
            
        return (min(255, r), min(255, g), min(255, b))
    
    def generate_progressive_image(self, output_path, current_iteration):
        """Gera imagem progressivamente com base nos dados disponíveis"""
        pixels_drawn = 0
        
        # Desenha apenas os pixels que foram calculados até agora
        for (px_orig, py_orig), iterations in self.pixel_data.items():
            # Escala os pixels originais (128x128) para a resolução da imagem
            scale_x = self.width / 128.0
            scale_y = self.height / 128.0
            
            px_scaled = int(px_orig * scale_x)
            py_scaled = int(py_orig * scale_y)
            
            # Desenha um bloco de pixels para melhor visualização
            block_size_x = max(1, int(scale_x))
            block_size_y = max(1, int(scale_y))
            
            color = self.iterations_to_color(iterations)
            
            # Desenha o bloco de pixels
            for dx in range(block_size_x):
                for dy in range(block_size_y):
                    final_x = px_scaled + dx
                    final_y = py_scaled + dy
                    
                    if 0 <= final_x < self.width and 0 <= final_y < self.height:
                        self.image.putpixel((final_x, final_y), color)
            
            pixels_drawn += 1
        
        # Adiciona efeito de brilho nos pixels mais recentes
        if current_iteration > 0 and len(self.pixel_data) > 0:
            self.add_glow_effect()
        
        # Salva a imagem
        self.image.save(output_path, 'PNG', optimize=True)
        return pixels_drawn
    
    def add_glow_effect(self):
        """Adiciona um sutil efeito de brilho"""
        # Cria uma versão com brilho sutil
        enhanced = self.image.copy()
        
        # Aplica um filtro de realce muito sutil
        pixels = np.array(enhanced)
        
        # Realce de contraste muito sutil
        pixels = pixels.astype(np.float32)
        pixels = pixels * 1.05  # Aumenta levemente o brilho
        pixels = np.clip(pixels, 0, 255).astype(np.uint8)
        
        self.image = Image.fromarray(pixels)

def main():
    parser = argparse.ArgumentParser(description='Fancy Fractal Generator')
    parser.add_argument('input_file', help='Arquivo de entrada com dados do fractal')
    parser.add_argument('iteration', type=int, help='Iteração atual')
    parser.add_argument('--width', type=int, default=800, help='Largura da imagem')
    parser.add_argument('--height', type=int, default=600, help='Altura da imagem')
    parser.add_argument('--output', default='fractal_realtime.png', help='Arquivo de saída')
    
    args = parser.parse_args()
    
    print(f"fancyFractal v1.0 - Iteração {args.iteration}")
    print(f"Input: {args.input_file}")
    print(f"Output: {args.output}")
    print(f"Resolução: {args.width}x{args.height}")
    
    # Cria o gerador de fractal
    fractal = FancyFractal(args.width, args.height)
    
    # Carrega os dados do arquivo
    if not fractal.load_fractal_data(args.input_file):
        print("Erro ao carregar dados do fractal")
        sys.exit(1)
    
    # Gera a imagem progressiva
    pixels_drawn = fractal.generate_progressive_image(args.output, args.iteration)
    
    print(f"Pixels processados: {pixels_drawn}")
    print(f"Imagem salva: {args.output}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())