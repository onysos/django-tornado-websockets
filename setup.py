import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tornado-websockets',
    version='0.0.1',
    description="Simple way to use WebSockets for Django with Tornado",
    long_description=README,
    author='Hugo ALLIAUME',
    author_email='kocal@live.fr',
    packages=['tornado_websockets'],
    install_requires=[
        'Django>=1.8',
        'tornado>=4.3',
        'tox>=2.3',
    ],
    include_package_data=True,
    license='GPLv3 License',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP'
    ]
)
