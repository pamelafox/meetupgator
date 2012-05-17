#!/usr/bin/python2.5
#
# Copyright 2009 Google Inc.
# Licensed under the Apache License, Version 2.0:
# http://www.apache.org/licenses/LICENSE-2.0

import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.api import memcache

from django.utils import simplejson

class ProxyHandler(webapp.RequestHandler):

  def get(self):
    url = self.request.get('url')
    logging.info(url)

    # Check if the result is cached, fetch if not
    json_str = memcache.get(url)
    if not json_str:
      logging.info('Fetching URL')
      try:
        result = urlfetch.fetch(url, deadline=10)
        if result.status_code == 200:
          json_str = result.content
          logging.info('Caching')
          memcache.set(url, json_str, 60)
        else:
          logging.info(result.status_code)
          logging.info(result.content)
      except:
          logging.info('Error fetching URL')

    # Output JSON result, and wrap in callback if provided
    if json_str:
      callback = self.request.get('callback')
      self.response.headers['Content-Type'] = 'application/json'
      if callback:
        self.response.out.write(callback + '(' + json_str + ')')
      else:
        self.response.out.write(json_str)


def main():
  application = webapp.WSGIApplication([(r'/proxy', ProxyHandler)],
                                     debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()