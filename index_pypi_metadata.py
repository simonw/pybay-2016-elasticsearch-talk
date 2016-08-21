"""
This script reads the JSON files in the metadata/ folder that have been
fetched with fetch_pypi_metadata.py, creates appropriate mappings in
Elasticsearch and then indexes all of the packages and releases into
Elasticsearch.
"""

from elasticsearch_dsl import DocType, String, Date, Integer, Boolean
from elasticsearch_dsl.connections import connections
import os
import json
from dateutil import parser

# Define a default Elasticsearch client
connections.create_connection(hosts=['localhost'])


class Package(DocType):
    name = String(index='not_analyzed')
    summary = String(analyzer='snowball')
    description = String(analyzer='snowball')
    keywords = String(analyzer='snowball')
    classifiers = String(index='not_analyzed', multi=True)

    class Meta:
        index = 'package'

    @classmethod
    def from_json(cls, d):
        return cls(
            meta={'id': d['info']['name']},
            name=d['info']['name'],
            summary=d['info']['summary'],
            description=d['info']['description'],
            keywords=d['info']['description'],
            classifiers=d['info']['classifiers'],
        )


class Release(DocType):
    package_name = String(index='not_analyzed')
    package_version = String(index='not_analyzed')
    python_version = String(index='not_analyzed')
    packagetype = String(index='not_analyzed')
    url = String(index='not_analyzed')
    filename = String(index='not_analyzed')
    has_sig = Boolean()
    downloads = Integer()
    size = Integer()
    upload_time = Date()

    class Meta:
        index = 'release'

    @classmethod
    def releases_from_json(cls, package_json):
        package_name = package_json['info']['name']
        release_docs = []
        releases = package_json.get('releases') or {}
        for version_number, list_of_relases in releases.items():
            for release in list_of_relases:
                release_docs.append(cls(
                    meta={'id': release['md5_digest']},
                    package_name=package_name,
                    package_version=version_number,
                    python_version=release['python_version'],
                    packagetype=release['packagetype'],
                    url=release['url'],
                    filename=release['filename'],
                    has_sig=release['has_sig'],
                    downloads=release['downloads'],
                    size=release['size'],
                    upload_time=parser.parse(release['upload_time']),
                ))
        return release_docs


# create the mappings in elasticsearch
Package.init()
Release.init()

filenames = os.listdir('metadata')
total = len(filenames)
count = 0
for filename in filenames:
    s = open('metadata/%s' % filename).read().strip()
    if s.startswith('{'):
        d = json.loads(s)
        p = Package.from_json(d)
        p.save()
        print p.name
        for r in Release.releases_from_json(d):
            r.save()
            print '  ', r.url
        count += 1
        if count % 100 == 0:
            print "%s / %s" % (count, total)
