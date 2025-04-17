# import setuptools
from setuptools import setup, find_packages


with open('README-pypi.md', 'r', encoding='utf-8') as read_me_file:
    read_me = read_me_file.read()


setup(
    name='forgy',
    version='0.1.3',
    author='Lamide I. Ogundeji',
    author_email='midetobi@gmail.com',
    description="A powerful file organizer and ebook manager for e-book metadata retrieval and renaming with ease",
    long_description=read_me,
    long_description_content_type='text/markdown',
    url="https://github.com/misterola/forgy",
    license="AGPL-3.0",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=[
        'pypdf==5.0.1',
        'requests==2.32.3',
        'reportlab==4.2.2',
        'python-dotenv==1.1.0',
        'flake8==7.1.1'
    ],
    entry_points={
        "console_scripts": [
            "forgy=cli.main:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>3.10',
)
