#!/usr/bin/env python
# check_stable.py
#
# Retrieve latest stable version from static.rust-lang.org
# Compare the stable version to ensure we have a corresponding docker tag
#
# If we have not built it, print the version we need to build and exit 0
# If we have built it, exit 1

import urllib.request as urllib
import json
import toml
import sys

# Dockerhub repo to compare rust-lang release with
DOCKERHUB_REPO="clux/muslrust"

def rust_stable_version():
    """Retrieve the latest rust stable version from static.rust-lang.org"""
    url = 'https://static.rust-lang.org/dist/channel-rust-stable.toml'
    req = urllib.urlopen(url)
    data = toml.loads(req.read().decode("utf-8"))
    req.close()
    return data['pkg']['rust']['version'].split()[0]

def tag_exists(tag):
    """Retrieve our built tags and check we have built a given one"""
    (namespace, repo) = DOCKERHUB_REPO.split("/")
    url = f'https://registry.hub.docker.com/v2/namespaces/{namespace}/repositories/{repo}/tags'
    req = urllib.urlopen(url)
    data = json.loads(req.read())
    req.close()
    return any(x['name'] == tag for x in data['results'])


if __name__ == '__main__':
    latest_stable = rust_stable_version()
    stable_tag = f'{latest_stable}-stable'
    if tag_exists(stable_tag):
        print(f'tag {stable_tag} already built')
        sys.exit(1)
    else:
        print(f'need to build {latest_stable}')
        sys.exit(0)
