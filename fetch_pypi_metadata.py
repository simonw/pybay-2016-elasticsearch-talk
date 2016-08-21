"""
This script loops through all 85,000+ packages on PyPI and attempts to
download the JSON metadata for each package into a metadata/ folder

It uses the https://pypi.python.org/pypi/Django/json metadata URLs

Use this with caution since it sends a lot of traffic to PyPI!
"""

import requests
import json
import xmlrpclib
import os

PYPI_XMLRPC = 'https://pypi.python.org/pypi'
PYPI_METADATA_URL = 'http://pypi.python.org/pypi/%s/json'
METADATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'metadata')


def get_package_list():
    return xmlrpclib.ServerProxy(PYPI_XMLRPC).list_packages()


def get_fetched_packages():
    return [fn[:-5] for fn in os.listdir(METADATA_DIR) if fn.endswith('.json')]


def fetch_package(package_name):
    url = PYPI_METADATA_URL % package_name
    try:
        d = requests.get(url).json()
    except Exception, e:
        print "  Could not fetch %s - %s" % (url, e)
        return
    filepath = os.path.join(METADATA_DIR, '%s.json' % package_name)
    open(filepath, 'w').write(json.dumps(d, indent=2))


if __name__ == '__main__':
    if not os.path.isdir(METADATA_DIR):
        os.makedirs(METADATA_DIR)
    packages_to_fetch = set(get_package_list()) - set(get_fetched_packages())
    print "%d packages to fetch" % len(packages_to_fetch)
    for package in packages_to_fetch:
        print package
        fetch_package(package)
