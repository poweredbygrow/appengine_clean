"""
Setup script
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.1.4'
setuptools.setup(
    name='appengine_clean',
    version=VERSION,
    author='David Grant',
    author_email='davidgrant@gmail.com',
    description='Clean old AppEngine versions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/poweredbygrow/appengine_clean',
    packages=['appengine_clean'],
    classifiers=[
      'Programming Language :: Python :: 3.7',
    ],
    entry_points = {
      'console_scripts': [
        'appengine-clean = appengine_clean.appengine_clean:main',                  
      ],              
    },
    download_url='https://github.com/poweredbygrow/appengine_clean/tarball/' + VERSION,
    keywords=['utility', 'miscellaneous', 'library'],
)
