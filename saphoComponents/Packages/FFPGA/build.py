#!/usr/bin/env python3
"""
Enhanced Build Script for Fractal Visualizer
Supports PyInstaller, cx_Freeze, and Nuitka build systems
"""

import os
import sys
import shutil
import subprocess
import logging
import argparse
import platform
from pathlib import Path
from datetime import datetime


class BuildLogger:
    """Enhanced logging system for build process"""
    
    def __init__(self, log_level=logging.INFO):
        self.setup_logger(log_level)
    
    def setup_logger(self, log_level):
        """Setup comprehensive logging"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create timestamp for log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"build_{timestamp}.log"
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Build process started - Log file: {log_file}")
        self.logger.info(f"Platform: {platform.system()} {platform.release()}")
        self.logger.info(f"Python: {sys.version}")


class EnhancedBuilder:
    """Enhanced build system for Fractal Visualizer"""
    
    def __init__(self, build_type="pyinstaller", debug=False):
        self.build_type = build_type.lower()
        self.debug = debug
        self.logger = BuildLogger().logger
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.main_script = "fractal_visualizer.py"
        
        # Build configuration
        self.app_name = "Enhanced Fractal Visualizer"
        self.app_version = "1.0.0"
        self.app_description = "Advanced fractal visualization tool with real-time rendering"
        self.app_author = "Fractal Systems"
        
        self.logger.info(f"Initializing {self.build_type} build system")
        self.logger.info(f"Debug mode: {self.debug}")
    
    def check_dependencies(self):
        """Check and install required dependencies"""
        self.logger.info("Checking build dependencies...")
        
        required_packages = {
            'pyinstaller': ['pyinstaller>=5.0'],
            'cx_freeze': ['cx_freeze>=6.0'],
            'nuitka': ['nuitka>=1.0', 'ordered-set']
        }
        
        runtime_packages = [
            'customtkinter>=5.0.0',
            'pillow>=9.0.0',
            'numpy>=1.20.0',
            'scipy>=1.7.0'
        ]
        
        try:
            # Check build tool
            build_deps = required_packages.get(self.build_type, [])
            for package in build_deps:
                self._install_package(package)
            
            # Check runtime dependencies
            for package in runtime_packages:
                self._install_package(package)
                
            self.logger.info("All dependencies checked successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
            return False
    
    def _install_package(self, package):
        """Install package if not available"""
        try:
            pkg_name = package.split('>=')[0].split('==')[0]
            __import__(pkg_name.replace('-', '_'))
            self.logger.debug(f"Package {pkg_name} already installed")
        except ImportError:
            self.logger.info(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to install {package}: {result.stderr}")
            
            self.logger.info(f"Successfully installed {package}")
    
    def clean_build(self):
        """Clean previous build artifacts"""
        self.logger.info("Cleaning previous build artifacts...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        files_to_clean = [

            "*.egg-info",
            "__pycache__"
        ]
        
        # Clean directories
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.logger.info(f"Removed directory: {dir_path}")
        
        # Clean files
        for pattern in files_to_clean:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    file_path.unlink()
                    self.logger.info(f"Removed file: {file_path}")
                elif file_path.is_dir():
                    shutil.rmtree(file_path)
                    self.logger.info(f"Removed directory: {file_path}")
    
    def validate_source(self):
        """Validate source code and requirements"""
        self.logger.info("Validating source code...")
        
        main_script_path = self.project_root / self.main_script
        if not main_script_path.exists():
            self.logger.error(f"Main script not found: {self.main_script}")
            return False
        
        # Check for required imports
        try:
            with open(main_script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            required_imports = [
                'customtkinter', 'PIL', 'numpy', 'scipy'
            ]
            
            for imp in required_imports:
                if imp not in content:
                    self.logger.warning(f"Import '{imp}' not found in main script")
            
            self.logger.info("Source validation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Source validation failed: {e}")
            return False
    
    def build_pyinstaller(self):
        """Build using PyInstaller"""
        self.logger.info("Starting PyInstaller build...")
        
        # PyInstaller command
        cmd = [
            'pyinstaller',
            '--name', self.app_name.replace(' ', '_'),
            '--onefile' if not self.debug else '--onedir',
            '--windowed',
            '--icon', 'icon.ico' if Path('icon.ico').exists() else None,
            '--add-data', 'assets;assets' if Path('assets').exists() else None,
            '--hidden-import', 'customtkinter',
            '--hidden-import', 'PIL._tkinter_finder',
            '--collect-submodules', 'customtkinter',
            '--collect-data', 'customtkinter',
            '--noconsole' if not self.debug else '--console',
            self.main_script
        ]
        
        # Remove None values
        cmd = [arg for arg in cmd if arg is not None]
        
        # Add debug options
        if self.debug:
            cmd.extend(['--debug', 'all'])
        
        # Create spec file for advanced configuration
        spec_file = self.project_root / f"{self.app_name.replace(' ', '_')}.spec"
        
      
        self.logger.info(f"Generated spec file: {spec_file}")
        self.logger.info(f"PyInstaller command: {' '.join(cmd)}")
        
        try:
            # Run PyInstaller
            result = subprocess.run(
                ['pyinstaller', str(spec_file)],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.logger.info("PyInstaller build completed successfully")
                self._log_build_output(result.stdout)
                return True
            else:
                self.logger.error("PyInstaller build failed")
                self._log_build_output(result.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"PyInstaller build error: {e}")
            return False
    
    def build_cx_freeze(self):
        """Build using cx_Freeze"""
        self.logger.info("Starting cx_Freeze build...")
        
        # Create setup.py for cx_Freeze
        setup_content = self._generate_cx_freeze_setup()
        setup_file = self.project_root / "setup_cx.py"
        
        with open(setup_file, 'w', encoding='utf-8') as f:
            f.write(setup_content)
        
        self.logger.info(f"Generated setup file: {setup_file}")
        
        try:
            # Run cx_Freeze
            result = subprocess.run([
                sys.executable, str(setup_file), 'build'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                self.logger.info("cx_Freeze build completed successfully")
                self._log_build_output(result.stdout)
                return True
            else:
                self.logger.error("cx_Freeze build failed")
                self._log_build_output(result.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"cx_Freeze build error: {e}")
            return False
    
    def build_nuitka(self):
        """Build using Nuitka"""
        self.logger.info("Starting Nuitka build...")
        
        cmd = [
            'nuitka',
            '--standalone' if not self.debug else '--onefile',
            '--enable-plugin=tk-inter',
            '--enable-plugin=numpy',
            '--include-package=customtkinter',
            '--include-package=PIL',
            '--include-package=scipy',
            '--windows-disable-console' if platform.system() == 'Windows' and not self.debug else None,
            '--output-dir=dist',
            f'--output-filename={self.app_name.replace(" ", "_")}',
            self.main_script
        ]
        
        # Remove None values
        cmd = [arg for arg in cmd if arg is not None]
        
        self.logger.info(f"Nuitka command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.logger.info("Nuitka build completed successfully")
                self._log_build_output(result.stdout)
                return True
            else:
                self.logger.error("Nuitka build failed")
                self._log_build_output(result.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"Nuitka build error: {e}")
            return False
    
    def _generate_pyinstaller_spec(self):
        """Generate PyInstaller spec file"""
        return f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets') if os.path.exists('assets') else None,
    ],
    hiddenimports=[
        'customtkinter',
        'PIL._tkinter_finder',
        'scipy.special',
        'scipy.linalg',
        'scipy.sparse',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out None values from datas
a.datas = [item for item in a.datas if item is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name.replace(" ", "_")}',
    debug={'True' if self.debug else 'False'},
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console={'True' if self.debug else 'False'},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    def _generate_cx_freeze_setup(self):
        """Generate cx_Freeze setup file"""
        return f'''import sys
from cx_Freeze import setup, Executable
import os

# Dependencies
build_options = {{
    'packages': [
        'customtkinter',
        'PIL',
        'numpy',
        'scipy',
        'tkinter',
    ],
    'excludes': [
        'unittest',
        'email',
        'http',
        'urllib',
        'xml',
    ],
    'include_files': [
        ('assets', 'assets') if os.path.exists('assets') else None,
    ],
    'optimize': 0 if {self.debug} else 2,
}}

# Filter out None values
build_options['include_files'] = [
    item for item in build_options['include_files'] 
    if item is not None
]

# Base for GUI applications
base = None
if sys.platform == 'win32':
    base = 'Win32GUI' if not {self.debug} else 'Console'

# Executable configuration
executables = [
    Executable(
        '{self.main_script}',
        base=base,
        target_name='{self.app_name.replace(" ", "_")}',
        icon='icon.ico' if os.path.exists('icon.ico') else None,
    )
]

setup(
    name='{self.app_name}',
    version='{self.app_version}',
    description='{self.app_description}',
    author='{self.app_author}',
    options={{'build_exe': build_options}},
    executables=executables,
)
'''
    
    def _log_build_output(self, output):
        """Log build output with proper formatting"""
        if output:
            self.logger.info("Build output:")
            for line in output.split('\n'):
                if line.strip():
                    self.logger.info(f"  {line}")
    
    def post_build_tasks(self):
        """Perform post-build tasks"""
        self.logger.info("Performing post-build tasks...")
        
        # Copy additional files
        additional_files = [
            'README.md',
            'LICENSE',
            'requirements.txt',
        ]
        
        for file_name in additional_files:
            src_file = self.project_root / file_name
            if src_file.exists():
                # Find the dist directory
                for dist_subdir in self.dist_dir.iterdir():
                    if dist_subdir.is_dir():
                        dst_file = dist_subdir / file_name
                        shutil.copy2(src_file, dst_file)
                        self.logger.info(f"Copied {file_name} to distribution")
        
        # Create installer script
        self._create_installer_script()
        
        # Generate build report
        self._generate_build_report()
    
    def _create_installer_script(self):
        """Create installer script for the application"""
        installer_content = f'''#!/bin/bash
# Enhanced Fractal Visualizer Installer

echo "Installing {self.app_name}..."

# Create application directory
APP_DIR="$HOME/Applications/{self.app_name.replace(' ', '_')}"
mkdir -p "$APP_DIR"

# Copy files
cp -r dist/* "$APP_DIR/"

# Create desktop entry (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    DESKTOP_FILE="$HOME/.local/share/applications/{self.app_name.replace(' ', '_').lower()}.desktop"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment={self.app_description}
Exec=$APP_DIR/{self.app_name.replace(' ', '_')}
Icon=$APP_DIR/icon.ico
Terminal=false
Categories=Graphics;Science;
EOF
    chmod +x "$DESKTOP_FILE"
    echo "Desktop entry created"
fi

echo "Installation completed!"
echo "Application installed to: $APP_DIR"
'''
        
        installer_file = self.dist_dir / "install.sh"
        with open(installer_file, 'w', encoding='utf-8') as f:
            f.write(installer_content)
        
        # Make executable
        installer_file.chmod(0o755)
        self.logger.info(f"Created installer script: {installer_file}")
    
    def _generate_build_report(self):
        """Generate comprehensive build report"""
        report_content = f'''# Build Report - {self.app_name}

## Build Information
- **Build Type**: {self.build_type}
- **Build Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Platform**: {platform.system()} {platform.release()}
- **Python Version**: {sys.version}
- **Debug Mode**: {self.debug}

## Application Details
- **Name**: {self.app_name}
- **Version**: {self.app_version}
- **Description**: {self.app_description}
- **Author**: {self.app_author}

## Build Artifacts
'''
        
        # List build artifacts
        if self.dist_dir.exists():
            report_content += "### Distribution Files\n"
            for item in self.dist_dir.rglob('*'):
                if item.is_file():
                    size = item.stat().st_size
                    report_content += f"- {item.relative_to(self.dist_dir)} ({size:,} bytes)\n"
        
        report_content += f'''
## Usage Instructions
1. Navigate to the `dist` directory
2. Run the executable: `{self.app_name.replace(' ', '_')}`
3. For installation, run: `./install.sh` (Linux/macOS)

## Build Logs
- Check the `logs` directory for detailed build logs
- Debug mode: {self.debug}

## Troubleshooting
- Ensure all dependencies are installed
- Check build logs for specific error messages
- Verify source code integrity
'''
        
        report_file = self.dist_dir / "BUILD_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"Build report generated: {report_file}")
    
    def run_build(self):
        """Run the complete build process"""
        self.logger.info(f"Starting {self.build_type} build process...")
        
        # Pre-build checks
        if not self.check_dependencies():
            self.logger.error("Dependency check failed")
            return False
        
        if not self.validate_source():
            self.logger.error("Source validation failed")
            return False
        
        # Clean previous builds
        self.clean_build()
        
        # Build based on type
        build_methods = {
            'pyinstaller': self.build_pyinstaller,
            'cx_freeze': self.build_cx_freeze,
            'nuitka': self.build_nuitka,
        }
        
        build_method = build_methods.get(self.build_type)
        if not build_method:
            self.logger.error(f"Unknown build type: {self.build_type}")
            return False
        
        # Execute build
        success = build_method()
        
        if success:
            self.post_build_tasks()
            self.logger.info("Build process completed successfully!")
            self.logger.info(f"Executable available in: {self.dist_dir}")
        else:
            self.logger.error("Build process failed!")
        
        return success


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Enhanced Build Script for Fractal Visualizer'
    )
    parser.add_argument(
        '--build-type', '-t',
        choices=['pyinstaller', 'cx_freeze', 'nuitka'],
        default='pyinstaller',
        help='Build system to use (default: pyinstaller)'
    )
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug mode'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set log level
    log_level = logging.DEBUG if args.verbose else logging.INFO
    
    try:
        # Create builder
        builder = EnhancedBuilder(
            build_type=args.build_type,
            debug=args.debug
        )
        
        # Run build
        success = builder.run_build()
        
        if success:
            print(f"\n✅ Build completed successfully!")
            print(f"📁 Executable location: {builder.dist_dir}")
            print(f"📋 Check BUILD_REPORT.md for details")
        else:
            print(f"\n❌ Build failed!")
            print(f"📋 Check logs directory for details")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()