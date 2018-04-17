from setuptools import setup

setup(
    name='sparrow',
    version='0.1',
    py_modules=['sparrow'],
    include_package_data=True,
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        sparrow=sparrow:sparrow
    ''',
)
