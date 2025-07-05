from setuptools import setup, find_packages

setup(
    name='logwatchdog',
    version='0.1.0',
    description='AI-powered Kubernetes log monitoring and auto-healing tool',
    author='Sejal Jain',
    author_email='your@email.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'slack_sdk',        # ✅ correct
        'python-dotenv',    # ✅ correct
        'openai',
        'pyyaml',
        'kubernetes',
        'fastapi',
        'uvicorn',
        'prometheus_client'

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
