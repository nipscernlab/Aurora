#!/usr/bin/env python3
"""
Setup script for Modern Fractal Visualizer
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Modern Real-time Fractal Visualizer with AMOLED theme"

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'numpy>=1.21.0',
        'Pillow>=9.0.0',
        'customtkinter>=5.0.0',
        'scipy>=1.7.0'
    ]

setup(
    name="fractal-visualizer",
    version="2.0.0",
    description="Modern Real-time Fractal Visualizer with AMOLED theme",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/fractal-visualizer",
    
    # Package configuration
    packages=find_packages(),
    py_modules=['fractal_visualizer'],
    
    # Dependencies
    install_requires=read_requirements(),
    
    # Python version requirement
    python_requires=">=3.7",
    
    # Entry points for command line usage
    entry_points={
        'console_scripts': [
            'fractal-visualizer=fractal_visualizer:main',
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.png', '*.ico'],
    },
    
    # Classifiers for PyPI
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for search
    keywords="fractal visualization graphics numpy pillow customtkinter amoled",
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/yourusername/fractal-visualizer/issues",
        "Source": "https://github.com/yourusername/fractal-visualizer",
        "Documentation": "https://github.com/yourusername/fractal-visualizer/wiki",
    },
    
    # License
    license="MIT",
    
    # Additional metadata
    zip_safe=False,
    platforms=["any"],
)