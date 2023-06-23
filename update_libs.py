#!/usr/bin/env python
# update_libs.py
#
# Retrieve the versions of packages from Arch Linux's repositories and update
# Dockerfile as needed.
#
# The code in documentation comments can also be used to test the functions by
# running "python -m doctest update_libs.py -v".

from __future__ import print_function

try:
    # Python 3
    import urllib.request as urllib
except ImportError:
    # Python 2
    import urllib

import json
import toml
import os
import re


def convert_openssl_version(version):
    """Convert OpenSSL package versions to match upstream's format

    >>> convert_openssl_version('1.0.2.o')
    '1.0.2o'
    """

    return re.sub(r'(.+)\.([a-z])', r'\1\2', version)


def convert_sqlite_version(version):
    """Convert SQLite package versions to match upstream's format

    >>> convert_sqlite_version('3.24.0')
    '3240000'
    """

    matches = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    return '{:d}{:02d}{:02d}00'.format(
        int(matches[1]), int(matches[2]), int(matches[3])
    )


def pkgver(package):
    """Retrieve the current version of the package in Arch Linux repos

    API documentation: https://wiki.archlinux.org/index.php/Official_repositories_web_interface

    The "str" call is only needed to make the test pass on Python 2 and 3, you
    do not need to include it when using this function.

    >>> str(pkgver('reiserfsprogs'))
    '3.6.27'
    """

    # Though the URL contains "/search/", this only returns exact matches (see API documentation)
    url = f'https://www.archlinux.org/packages/search/json/?name={package}'
    req = urllib.urlopen(url)
    metadata = json.loads(req.read())
    req.close()
    try:
        return metadata['results'][0]['pkgver']
    except IndexError:
        raise NameError(f'Package not found: {package}')


def rustup_version():
    """
    Retrieve the current version of Rustup from https://static.rust-lang.org/rustup/release-stable.toml

    :return: The current Rustup version
    """

    req = urllib.urlopen('https://static.rust-lang.org/rustup/release-stable.toml')
    metadata = toml.loads(req.read().decode("utf-8"))
    req.close()

    return metadata['version']


if __name__ == '__main__':
    PACKAGES = {
        'CURL': pkgver('curl'),
        #'PQ': pkgver('postgresql-old-upgrade'), # see https://github.com/clux/muslrust/issues/81
        'SQLITE': convert_sqlite_version(pkgver('sqlite')),
        'SSL': convert_openssl_version(pkgver('openssl')),
        'ZLIB': pkgver('zlib'),
        'RUSTUP': rustup_version()
    }

    # Show a list of packages with current versions
    for prefix, value in PACKAGES.items():
        print(f'{prefix}_VER="{value}"')

    # Update Dockerfile
    fname = 'Dockerfile'
    with open(fname, 'r') as src:
        dst = open(f'{fname}.new', 'w')

            # Iterate over each line in Dockerfile, replacing any *_VER variables with the most recent version
        for line in src:
            for prefix, version in PACKAGES.items():
                line = re.sub(f'({prefix}_VER=)\S+', f'\1"{version}"', line)
            dst.write(line)

    dst.close()
    os.rename(f'{fname}.new', fname)
