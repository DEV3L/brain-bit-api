from setuptools import setup, find_packages

requirements = []

with open('requirements.txt') as file:
    for line in file:
        if line:
            requirements.append(line)

setup(
    name='medasync-processing-enginer',
    packages=find_packages(),
    version='0.1',
    description='Python Eve App for managing the nlp data engine for Medasync Processing Engine',
    author='Dev3l Solutions',
    install_requires=[
        requirements
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
