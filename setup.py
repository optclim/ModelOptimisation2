from setuptools import setup, find_packages
from sphinx.setup_command import BuildDoc

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
        'ObjectiveFunction_client',
    ],
    cmdclass={'build_sphinx': BuildDoc},
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'copyright': ('setup.py', author),
            'source_dir': ('setup.py', 'docs')}},
    setup_requires=['sphinx'],
    extras_require={
        'lint': [
            'flake8>=3.5.0',
        ],
        'docs': [
            'sphinx<4.0',
            'sphinx_rtd_theme',
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
            'mo2-simobs_dummy = ModelOptimisation2.simobs_dummy:main',
            'mo2-optimise = ModelOptimisation2.optimise:main',
        ],
    },
    author=author,
    description="model optimisation framework for climate models",
)
