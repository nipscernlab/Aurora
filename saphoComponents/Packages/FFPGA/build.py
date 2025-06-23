#!/usr/bin/env python3
"""
Script para gerar o executável fancyFractal.exe
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Executa comando e exibe output"""
    print(f"Executando: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            cwd=cwd,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def clean_build():
    """Limpa arquivos de build anteriores"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removendo {dir_name}...")
            shutil.rmtree(dir_name)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    required_packages = [
        'pyinstaller',
        'customtkinter',
        'numpy',
        'pillow'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Pacotes faltando: {', '.join(missing_packages)}")
        print("Instale com: pip install " + " ".join(missing_packages))
        return False
    
    return True

def build_executable():
    """Gera o executável"""
    print("🚀 Iniciando build do fancyFractal.exe")
    
    # Verificar dependências
    if not check_dependencies():
        return False
    
    # Limpar build anterior
    clean_build()
    
    # Verificar se os arquivos necessários existem
    required_files = ['fractal_visualizer.py', 'build_fractal.spec']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Arquivo necessário não encontrado: {file}")
            return False
    
    # Executar PyInstaller
    print("📦 Gerando executável...")
    if not run_command("pyinstaller build_fractal.spec --clean"):
        print("❌ Erro ao gerar executável")
        return False
    
    # Verificar se executável foi criado
    exe_path = os.path.join("dist", "fancyFractal.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ Executável criado com sucesso!")
        print(f"📍 Localização: {os.path.abspath(exe_path)}")
        print(f"📊 Tamanho: {size_mb:.1f} MB")
        
        # Testar executável básico (apenas verificar se inicia)
        print("🧪 Testando executável...")
        test_cmd = f'"{exe_path}" --help'
        if run_command(test_cmd):
            print("✅ Teste básico passou!")
        else:
            print("⚠️  Executável criado mas teste falhou")
        
        return True
    else:
        print("❌ Executável não foi criado")
        return False

def create_portable_package():
    """Cria pacote portável com exemplo"""
    print("📦 Criando pacote portável...")
    
    package_dir = "fancyFractal_portable"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    os.makedirs(package_dir)
    
    # Copiar executável
    exe_src = os.path.join("dist", "fancyFractal.exe")
    exe_dst = os.path.join(package_dir, "fancyFractal.exe")
    shutil.copy2(exe_src, exe_dst)
    
    # Criar arquivo de exemplo
    example_data = "\n".join([str(i % 256) for i in range(128 * 128)])
    with open(os.path.join(package_dir, "example_fractal.txt"), "w") as f:
        f.write(example_data)
    
    # Criar arquivo de instruções
    instructions = """# Fractal Visualizer - Instruções de Uso

## Uso Básico:
fancyFractal.exe example_fractal.txt

## Opções Avançadas:
fancyFractal.exe dados.txt --width 256 --height 256 --palette rainbow

## Paletas Disponíveis:
- grayscale (padrão)
- fire
- ocean  
- rainbow
- plasma
- viridis

## Exemplo com JavaScript/Electron:
const command = `"${fancyFractalPath}" "${outputFilePath}" --width 128 --height 128 --palette rainbow`;
"""
    
    with open(os.path.join(package_dir, "README.txt"), "w", encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"✅ Pacote portável criado em: {os.path.abspath(package_dir)}")

def main():
    """Função principal"""
    print("🎨 Fractal Visualizer Builder")
    print("=" * 40)
    
    if build_executable():
        create_portable_package()
        print("\n🎉 Build concluído com sucesso!")
        print("\nPara usar no seu projeto Electron:")
        print("1. Copie fancyFractal.exe para saphoComponents/Packages/FFPGA/")
        print("2. Use o código JavaScript que você já tem")
        print("3. O executável aceita os parâmetros: arquivo --width N --height N --palette NOME")
        
        return True
    else:
        print("\n❌ Build falhou")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)