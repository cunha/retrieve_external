from setuptools import setup, find_packages

setup(
    name="retrieve_external",
    version='0.0.1',
    author='Alex Marder',
    # author_email='notlisted',
    description="Retrieve files for bdrmapIT.",
    url="https://github.com/alexmarder/retrieve_external",
    packages=find_packages(),
    install_requires=['python-dateutil', 'requests', 'humanfriendly', 'beautifulsoup4'],
    entry_points={
        'console_scripts': [
            'retrieve_external=retrieve_external.retrieve:main',
        ],
    },
    zip_safe=False,
    include_package_data=True,
    python_requires='>3.6'
)
