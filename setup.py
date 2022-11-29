from setuptools import setup, find_packages


setup(
    name='detadantic',
    version='0.0.1',
    author='Jay',
    author_email='0jaybae0@gmail.com',
    description='Provides Active-Record style wrappers to Deta Base using Pydantic.',
    url='https://github.com/Jay184/detadantic',
    project_urls={
        'Bug Tracker': 'https://github.com/Jay184/detadantic/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    py_modules=['detadantic'],
    include_package_data=True,
    install_requires=[
        'deta==1.1.0',
        'pydantic==1.10.2',
    ],
    extras_require={
        'dev': [
            'pkginfo==1.8.3',
            'build',
            'twine',
            'pytest',
        ]
    },
    python_requires='>=3.9'
)
