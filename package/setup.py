try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='PythonChromiumHTML2PDF',
    description='PythonChromiumHTML2PDF : '
                'Minimal Python HTML->PDF converter with Chromium.',
    license='Apache License 2.0',
    version='0.1.0',
    author='Valentin François',
    maintainer='Valentin François',
    url='https://github.com/ValentinFrancois/PythonChromiumHTML2PDF',
    packages=['PythonChromiumHTML2PDF'],
    install_requires=['git+git://github.com/ValentinFrancois/PyChromeDevTools']
)
