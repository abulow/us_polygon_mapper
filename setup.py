from setuptools import setup
import io

setup(
    name='us_polygon_mapper',
    version='1.0.0',
    author='Adam Bulow',
    author_email='adamjbulow@gmail.com',
    packages=['us_polygon_mapper'],
    package_data={'us_polygon_mapper': ['*']},
    url='https://github.com/abulow/us_polygon_mapper',
    license='LICENSE.txt',
    description=("Create Google Maps US polygon maps from csv's, python "
            "dictionaries and pandas dataframes"),
    long_description=io.open('README.rst', encoding="utf8").read(),
    install_requires=[
        "pandas", "gmplot", "selenium",
        "Pillow", "BeautifulSoup4"
        ]
)