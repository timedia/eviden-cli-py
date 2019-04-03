from setuptools import find_packages, setup


setup(
    name='eviden',
    version='1.0',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'eviden = eviden.__main__:main',
        ]
    },
    install_requires=[
        'bs4',
        'requests',
    ],
    extras_require={
        'test': [
            'flake8',
            'pytest',
        ],
    },
    python_requires=">= 3.7",
)
