from setuptools import setup, find_namespace_packages
from os import path


from vulkn.config import VERSION


BASE_URL = 'https://github.com/VulknData/vulkn'

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read().strip()

with open(path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.read().strip().split('\n')

setup(
    name='vulkn',
    version=VERSION,
    description='The environmentally friendly petabyte scale Python eco-system built on Yandex ClickHouse',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='clickhouse',
    author='Jason Godden',
    author_email='jason@vulkndata.io',
    url=BASE_URL,
    download_url=f'{BASE_URL}/archive/v{VERSION}-alpha.tar.gz',
    license='gpl-3.0',
    include_package_data=True,
    packages=find_namespace_packages(include=['vulkn','vulkn.*']),
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False,
    scripts=['scripts/vulkn'],
    python_requires='>=3.7'
)
