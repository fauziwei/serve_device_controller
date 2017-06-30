# coding: utf-8
# @2017
# Fauzi, fauziwei@yahoo.com
url_patterns = []

# index
from index import urls
url_patterns.extend(urls.url_patterns)

# oauth2
from oauth2 import urls
url_patterns.extend(urls.url_patterns)
