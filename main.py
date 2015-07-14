#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import logging
import re
import os
import webapp2
import jinja2
import config

from webapp2 import uri_for

from google.appengine.api import urlfetch


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)
MAIN_HTML = """<html>
    <body>
        <h1>Cocos2d-x File Watcher!</h1>
        <p>Coming soon...</p>
    </body>
</html>
"""


def _filename_to_diff_regex(filename):

    filename = re.escape(filename)
    return r"(?:---|\+\+\+) (?:a|b).*?{}.*".format(filename)


def _find_matches_for_files_in_diff(files, diff_file):

    regexes = map(_filename_to_diff_regex, files)
    regexes = map(re.compile, regexes)

    return map(lambda r: r.findall(diff_file), regexes)


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_HTML)


class GithubHookHandler(webapp2.RequestHandler):

    def get(self):

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({'files': config.FILES}))

    def post(self):

        payload = json.loads(self.request.body.decode())
        pull_request = payload.get('pull_request')

        if not pull_request:
            return

        diff_url = pull_request['diff_url']
        diff_response = urlfetch.fetch(diff_url)
        diff_file = diff_response.content

        if diff_response.status_code != 200:
            logging.error("Couldn't fetch diff file!")
            return

        files = config.FILES
        matches = _find_matches_for_files_in_diff(files, diff_file)

        if any(matches):
            urlfetch.fetch(
                config.SLACK_WEBHOOK,
                payload='payload={"text": "Changes to {}"}'.format(matches),
                method=urlfetch.POST
            )


class PHSBSubscriber(webapp2.RequestHandler):
    def get(self):

        hook_url = uri_for('github-webhook', _full=True)
        template = JINJA_ENVIRONMENT.get_template('index.html')

        self.response.write(template.render({'webhook_url': hook_url}))


app = webapp2.WSGIApplication([
    webapp2.Route('/',                  MainHandler,        'main'),
    webapp2.Route('/github-webhook',    GithubHookHandler,  'github-webhook'),
    webapp2.Route('/subscribe',         PHSBSubscriber,     'subscriber')
], debug=True)
