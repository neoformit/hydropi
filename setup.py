"""Set up Python package."""

import setuptools

with open('requirements.txt') as f:
    requirements = [x for x in f.read().split('\n') if x]

setuptools.setup(
    name='hydropi',
    version='0.1',
    description='Interface and control a high pressure hydroponics system',
    url='https://github.com/neoformit/hydropi',
    author='neoformit',
    author_email='chyde@neoformit.com',
    license='MIT',
    install_requires=requirements,
    packages=[
        'hydropi',
        'hydropi.config',
        'hydropi.interfaces',
        'hydropi.interfaces.sensors',
        'hydropi.interfaces.controllers',
        'hydropi.notifications',
        'hydropi.process',
        'hydropi.process.check',
        'hydropi.server',
        'hydropi.server.handlers',
    ],
    zip_safe=True,
)
