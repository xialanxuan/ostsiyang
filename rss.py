import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images

import jinja2
import webapp2

from model import *
from main import *


class RSSHandler(webapp2.RequestHandler):
    def get(self, view):
		url = 'http://ostsiyang.appspot.com/view='+view
		bound_answer=Answer()
		bound_question=Question()
		question=bound_question.get_by_id(int(view))
		answer=bound_answer.get_question(int(view))
		temp_vars = { 
			'question' : question,
			'url' : url,
			'answer' : answer,
			}
		self.response.headers['Content-Type'] = 'text/xml'
		display = JINJA_ENVIRONMENT.get_template('rss.xml')
		self.response.write(display.render(temp_vars))


application = webapp2.WSGIApplication([
    (r'/rss/view=(.*)/rss.xml', RSSHandler),
], debug=True)