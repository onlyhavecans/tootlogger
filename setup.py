#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Setup script """

import setuptools
import versioneer

with open('README.md') as readme_file:
    README = readme_file.read()


setuptools.setup(
    name='tootlogger',
    install_requires=['html2text', 'jinja2', 'mastodon.py', 'toml'],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['tootlogger = tootlogger.cli:main']
    },
    url='https://onlyhavecans.works/amy/tootlogger',
    license='BSD',
    author='Amy Aronsohn',
    author_email='WagThatTail@Me.com',
    description='Log your Matodon toots to DayOne',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    include_package_data=True,
    license_file="LICENSE.txt",
    long_description=README,
    long_description_content_type='text/markdown',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
