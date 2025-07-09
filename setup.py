from setuptools import setup, find_packages

setup(
    name='hsoundworks_cli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'librosa',
        'matplotlib',
        'numpy',
        'soundfile'  # Add this if you're doing audio conversion
    ],
    entry_points={
        'console_scripts': [
            'hscheck = hsoundworks_cli.main:main',
            'hsconvert = hsoundworks_cli.convert:main',
            'hsbpm = hsoundworks_cli.bpm_analyser:main'
        ]
    },
)
