from setuptools import setup, find_packages

name = 'ModelOptimisation2'
version = '0.1'
release = '0.1.0'
author = 'Magnus Hagdorn'

setup(
    name=name,
    packages=find_packages(),
    version=release,
    include_package_data=True,
    install_requires=[
        'f90nml',
        'ObjectiveFunction',
    ],
    extras_require={
        'lint': [
            'flake8>=3.5.0',
        ],
        'testing': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mo2-write = ModelOptimisation2.write_config:main',
            'mo2-configure = ModelOptimisation2.model_config:main',
            'mo2-transition = ModelOptimisation2.transition:main',
        ],
    },
    author=author,
    description="model optimisation framework for climate models",
)
