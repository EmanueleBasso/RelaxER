from setuptools import setup

setup(
    name="relaxER",
    version="1.0",
    description="A rule-based Entity Resolution tool and with Active Learning",
    license="MIT",
    author="Emanuele Basso",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'py-stringmatching==0.4.1',
        'pandas==0.25.3',
        'tqdm==4.48.0',
        'PyQt5==5.15.0'
    ]
)