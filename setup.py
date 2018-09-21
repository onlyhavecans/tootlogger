import setuptools
import versioneer


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
    zip_safe=False,
)
