from setuptools import setup

setup(
    name='arithvlexer',
    version='1.0',
    py_modules=['arithvlexer'],
    install_requires=['Pygments>=2.0'],
    entry_points={
        'pygments.lexers': [
            'arithv = arithvlexer:ArithVLexer',
        ],
    },
)
