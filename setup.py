from setuptools import setup
from vulkn import __version__

setup(
    name='vulkn',
    version=__version__,
    description='Python DataOps environment for Yandex ClickHouse',
    long_description='',
    keywords='clickhouse',
    url='https://github.com/vulkndata/vulkn',
    author='Jason Godden',
    author_email='jason@vulkndata.io',
    license='GPL v3',
    package_data={'vulkn': ['vulkn.rc.sample']},
    packages=[
        'vulkn',
        'vulkn.clickhouse',
        'vulkn.clickhouse.client',
        'vulkn.funcs',
        'vulkn.sql',
        'vulkn.sql.extensions',
        'vulkn.sql.vector',
        'vulkn.types'
    ],
    install_requires=[
        'sqlparse>=0.2.2',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'vulkn = vulkn.cli:run_cli'
        ]
    }
)