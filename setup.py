_classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]

if __name__ == '__main__':
    from setuptools import setup
    import dtyper

    desc = '⌨️dtyper: Call typer commands or make dataclasses from them ⌨️'

    setup(
        name='dtyper',
        version=dtyper.__version__,
        author='Tom Ritchford',
        author_email='tom@swirly.com',
        url='https://github.com/rec/dtyper',
        py_modules=['dtyper'],
        description=desc,
        long_description=open('README.rst').read(),
        license='MIT',
        classifiers=_classifiers,
        keywords=['dataclass'],
    )
