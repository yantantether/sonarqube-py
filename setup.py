import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sonarqube-py",
    version="0.1.0",
    author="Pat Turner",
    description="A python wrapper for the SonarQube web API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yantantether/sonarqube-py",
    packages=setuptools.find_packages(),
    install_requires=[
          'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
    ],
    python_requires='>=3.6',
)