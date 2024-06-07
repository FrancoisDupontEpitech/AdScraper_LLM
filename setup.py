from setuptools import setup, find_packages

def load_requirements(filename):
    with open(filename, 'r') as f:
        return f.read().splitlines()

setup(
    name='AdScraper_LLM',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=load_requirements('requirements.txt'),
    entry_points={
        'console_scripts': [
            'adscraper=package.adscraper_llm:main',
        ],
    },
)
