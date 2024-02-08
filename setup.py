from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='five9',
    version='1.1.0',
    packages=find_packages(),
    description='A Five9 Configuration Webserivce API wrapper',
    long_description=open('README.md').read(),
    install_requires=requirements,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
    ],
)
