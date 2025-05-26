from setuptools import setup, find_packages

setup(
    name='logwatchdog',
    version='0.1.0',
    description='AI-powered Kubernetes log monitoring and auto-healing tool',
    author='Aviral Jain',
    author_email='your@email.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'kubernetes',
        'requests',
        'pyyaml',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'logwatchdog = watcher.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
