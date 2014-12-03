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
import os,os.path

from google.appengine.ext import ndb
from google.appengine.api import users


import jinja2
import webapp2

#from models import *







JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()

        if user:
        	url = users.create_logout_url(self.request.uri)
        	url_linktext = 'Logout'
        	url_response = 'Welcome, ' + user.nickname()
        	user_control = 1
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            url_response = 'Welcome'
            user_control = 0

        template_values = {
        	'url': url,
            'url_linktext': url_linktext,
            'url_response': url_response,
            'user_control': user_control,
        }

        template = JINJA_ENVIRONMENT.get_template('header.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)