
from setuptools import setup, find_packages

setup(
    name='ecu_audit_cli',
    version='0.2.1',
    description='CLI tool for secure ECU audit logging via ELM327',
    author='Sumit Chouhan',
    packages=find_packages(),
    install_requires=[
        'python-can',
        'flask',
        'pyserial',
    ],
    entry_points={
        'console_scripts': [
            'ecu-audit=ecu_audit.main:main',
        ],
    },
)
