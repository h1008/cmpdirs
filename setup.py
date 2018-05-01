from setuptools import setup, find_packages

# See https://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
from cmpdirs._version import VERSION

setup(
    name='cmpdirs',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click'
    ],
    entry_points={
        "console_scripts": [
            "cmpdirs = cmpdirs.cmpdirs:cli",
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose', 'parameterized']
)

