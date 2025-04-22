
from setuptools import setup, find_packages

setup(
    name='ecu_audit_cli',
    version='0.1.0',
    description='CLI tool for secure ECU audit logging via ELM327',
    author='DestroSolutions',
    packages=find_packages(),
    install_requires=[
        'python-can',
        'flask'
    ],
    entry_points={
        'console_scripts': [
            'ecu-audit=ecu_audit.main:main',
        ],
    },
)
