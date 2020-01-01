from setuptools import setup
from os import path


from vulkn.config import VERSION


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='vulkn',
    version=VERSION,
    description='The environmentally friendly petabyte scale Python eco-system built on Yandex ClickHouse',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='clickhouse',
    author='Jason Godden',
    author_email='jason@vulkndata.io',
    url='https://github.com/VulknData/vulkn',
    download_url=f'https://github.com/VulknData/vulkn/archive/v{VERSION}-alpha.tar.gz',
    license='gpl-3.0',
    include_package_data=True,
    packages=[
        'vulkn',
        'vulkn/apps',
        'vulkn/contrib',
        'vulkn/storages',
        'vulkn/storages/clickhouse',
        'vulkn/types',
        'vulkn/workspaces',
        'vulkn/workspaces/templates',
        'vulkn/funcs',
        'vulkn/funcs/agg',
        'vulkn/clickhouse',
        'vulkn/clickhouse/client',
        'vulkn/library',
        'vulkn/library/core',
        'vulkn/library/core/functions',
        'vulkn/library/core/aggfunctions',
        'vulkn/library/core/sqlext',
        'vulkn/library/core/sqlext/chunk_by',
        'vulkn/library/core/sqlext/vectorize_by',
        'vulkn/library/core/sqlext/vectorize_by/functions',
        'vulkn/formats',
        'vulkn/sql',
        'vulkn/sql/udfs',
        'vulkn/sql/vector',
        'vulkn/sql/extensions'
    ],
    install_requires=[
        'ciso8601',
        'numpy',
        'pandas',
        'python-dateutil',
        'pytz',
        'PyYAML',
        'six',
        'sqlparse',
        'tabulate'
    ],
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
