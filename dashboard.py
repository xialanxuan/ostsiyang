import os
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from main import *
from model import *


def strip_tags(temptags2):
  temptags2 = temptags2.split(',')
  for x in range(len(temptags2)):
	temptags2[x] = temptags2[x].strip()
	if temptags2[x] == '':
		temptags2[x] = None
  temptags2 = filter(None, temptags2)
  temptags2 = list(set(temptags2))
  return temptags2


class Dashboard(webapp2.RequestHandler):
	def show(self):
		c_title = self.request.get('c_title', DEFAULT_QUESTION_NAME)
		user = str(users.get_current_user())
		bound_Question = Question()
		questions = bound_Question.get_author_question(user)

		show_dashboard_template={
		'dashboard_show_que' : questions,
		'user':user,
		}

		view_dashboard = JINJA_ENVIRONMENT.get_template('body_dashboard.html')
		self.response.write(view_dashboard.render(show_dashboard_template))

	def get(self):
		header(self)
		if users.get_current_user():
			self.show()
		tail(self)

	def post(self):
		header(self)
		if users.get_current_user():
			self.show()
		tail(self)



class Create_Question(webapp2.RequestHandler):
	def show(self):
		create_question_template = {
		    'c_url' :'/dashboard/create',
		    'c_qid' : 'Question QID, this is a unique qid and cannot be modified',
			'c_title' : 'Question Name',
			'c_body':'Enter your question here',
			'c_tags':'tags,here',
			'c_new':1,

		}
		send_create_question_template= JINJA_ENVIRONMENT.get_template('body_create_question.html')
		self.response.write(send_create_question_template.render(create_question_template))

	def get(self):
		header(self)
		if users.get_current_user():
			self.show()
		tail(self)

	def post(self):
		ques = Question()
		if users.get_current_user():
			ques.author = str(users.get_current_user())
			ques.qid = self.request.get('queid')
			ques.title = self.request.get('quetitle')

			if ques.title == '':
				ques.title = 'DEFAULT_QUESTION_NAME'
			ques.body = self.request.get('quebody')
			ques.tags = strip_tags(self.request.get('quetag'))
			ques.put()

		header(self)
		if users.get_current_user():
			self.response.write('<p class="main"><b>Success!</b></p>')
			self.response.write('<p class="main"><a href="/dashboard">My Question and Answers</a></p>')
		tail(self)

class Edit_Question(webapp2.RequestHandler):
	def show(self,key):
		bound_question=Question()
		e_que= bound_question.get_by_id(int(key))
		create_question_template = {
		    'c_url' :"/dashboard/edit="+key,
		    'c_qid': e_que.qid,
			'c_title': e_que.title,
			'c_body': e_que.body,
			'c_tags': ', '.join(e_que.tags),
			'c_new': 0,

		}
		send_create_question_template= JINJA_ENVIRONMENT.get_template('body_create_question.html')
		self.response.write(send_create_question_template.render(create_question_template))

	def get(self, key):
		header(self)
		bound_question=Question()
		cur_question = bound_question.get_by_id(int(key))
		if str(users.get_current_user()) == cur_question.author:
			self.show(key)
		tail(self)

	def post(self,key):
		header(self)
		bound_question=Question()
		ques = bound_question.get_by_id(int(key))

		ques.title = self.request.get('quetitle')

		if ques.title == '':
			ques.title = 'DEFAULT_QUESTION_NAME'
		ques.body = self.request.get('quebody')
		ques.tags = strip_tags(self.request.get('quetag'))
		ques.put()

		if ques.author == str(users.get_current_user()):
			self.response.write('<p class="main"><b>Success!</b></p>')
			self.response.write('<p class="main"><a href="/dashboard">My Question and Answers</a></p>')
		tail(self)



app = webapp2.WSGIApplication([
	('/dashboard/edit=(.*)', Edit_Question),
	('/dashboard/create', Create_Question),
    ('/dashboard/?', Dashboard),
], debug=True)