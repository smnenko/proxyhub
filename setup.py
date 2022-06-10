from setuptools import setup


setup(
    name='proxyhub',
    version='0.0.1',
    description='Parse proxies from github repos',
    url='https://github.com/smnenko/proxy',
    author='Stanislav Semenenko',
    author_email='stanichgame@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='proxy http https socks4 socks5 parsing',
    project_urls={
        'Source': 'https://github.com/smnenko/proxy',
        'Issues': 'https://github.com/smnenko/proxy/issues'
    },
    py_modules=['proxyhub'],
    install_requires=['requests'],
    python_requires='>=3.8'
)
