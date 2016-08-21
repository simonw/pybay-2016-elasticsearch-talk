import re
import os
import urlparse
import hashlib
import json
import sys

title_re = re.compile(r'([=*]{3,})\n([^\n]+)\n\1\n')


def find_title(rst):
    matches = title_re.findall(rst)
    # eg: [('===========================', 'FAQ: Installation')]
    if not matches:
        return ''
    else:
        return matches[0][1]


def walk_documentation(path='.', base_url=''):
    path = os.path.realpath(path)
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.txt'):
                filepath = os.path.join(dirpath, filename)
                content = open(filepath).read()
                title = find_title(content)
                # Figure out path relative to original
                relpath = os.path.relpath(filepath, path)
                url = urlparse.urljoin(base_url, relpath[:-4] + '/')
                yield {
                    'title': title,
                    'path': relpath,
                    'top_folder': relpath.split('/')[0],
                    'url': url,
                    'content': content,
                    'id': hashlib.sha1(url).hexdigest(),
                }


def usage(extra_error=''):
    print "Outputs sphinx docs in a format that can be bulk loaded into elasticsearch"
    print "Usage: %s <path-to-folder> <base-url-of-hosted-docs>" % sys.argv[0]
    print
    print "e.g."
    print "  %s ~/django/docs/ https://docs.djangoproject.com/en/1.10/ | curl -s XPOST localhost:9200/docsearch/doc/_bulk --data-binary @-" % sys.argv[0]
    if extra_error:
        print
        print extra_error
    sys.exit(1)


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 2:
        usage()
    path, base_url = args
    if not (base_url.startswith('http://') or base_url.startswith('https://')):
        usage('Docs URL must start with http or https')

    for document in walk_documentation(path, base_url):
        print json.dumps({'index': {'_id': document['id']}})
        print json.dumps(document)
