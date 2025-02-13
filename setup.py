# SPDX-FileCopyrightText: 2025 Helmholtz-Zentrum für Umweltforschung GmbH - UFZ
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from setuptools import setup, find_packages

long_description = open('README.md').read() if os.path.exists('README.md') else ''

setup(
    name='PyExpress',
    version='1.0',
    description='Python library for automating 3D image analysis pipelines',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Helmholtz-UFZ/PyExpress.git',
    author='Martin Kobe, Claudius Wehner, Rikard Graß',
    author_email='martin.kobe@ufz.de',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    keywords='3D image analysis, photogrammetry, research, automation, pipeline',
    packages=find_packages(
        include=['PyExpress', 'PyExpress.*'],
        exclude=['LICENSES', 'DOCS']
    ),
    install_requires=[
        'python-abc',
        'influxdb-client',
        'pysftp',
        'opencv-python',
        'tifffile',
        'pandas',
        'seaborn',
        'scikit-learn',
        'scikit-image',
        'minio',
        'numpy',
        'astral',
    ],
    python_requires='>=3.9',
    license_files=("LICENSE.md", "LICENSES/GPL-3.0-or-later.txt"),
    include_package_data=True,
    zip_safe=False,
)
