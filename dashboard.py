import os
import cgi
import urllib
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images


import jinja2
import webapp2
import time

from main import *
from model import *

def replace_html(string):
  newstring = re.sub(r'(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)', r'<a href="\1">\1</a>', string)
  string = re.sub(r'<a href="(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)">[^\s]+.jpg</a>', r'<img src="\1">', newstring)
  newstring = re.sub(r'<a href="(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)">[^\s]+.png</a>', r'<img src="\1">', string)
  string = re.sub(r'<a href="(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)">[^\s]+.gif</a>', r'<img src="\1">', newstring)
  return string

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
	def get(self,page=None):
		header(self)
		if users.get_current_user():
			c_title = self.request.get('c_title', DEFAULT_QUESTION_NAME)
			user = str(users.get_current_user())
			bound_Question = Question()
			bound_Answer=Answer()
			questions = bound_Question.get_author_question(user)

			if not page:
				page = str(0)
				questions = bound_Question.get_author_question_page(user,1)
				older_url = "/dashboard/2"
            
			else:        
				questions = bound_Question.get_author_question_page(user,int(page))
				older_url = "/dashboard/"+str((int(page)+1))

			#answers = bound_Answer.get_author_answer(user)
			show_dashboard_template={
				'dashboard_show_que' : questions,
				'user':user,
				'older_url' : older_url,
			}

			view_dashboard = JINJA_ENVIRONMENT.get_template('body_dashboard.html')
			self.response.write(view_dashboard.render(show_dashboard_template))

		tail(self)

class DashboardAnswer(webapp2.RequestHandler):
	def get(self,page=None):
		header(self)
		if users.get_current_user():
			c_title = self.request.get('c_title', DEFAULT_QUESTION_NAME)
			user = str(users.get_current_user())
			bound_Answer=Answer()
			answer = bound_Answer.get_author(user)
			#answers = bound_Answer.get_author_answer(user)
			show_dashboard_template={
				'answer' : answer,
				'user':user,
				
			}

			view_dashboard = JINJA_ENVIRONMENT.get_template('body_dashboardanswer.html')
			self.response.write(view_dashboard.render(show_dashboard_template))

		tail(self)


class DashboardImage(webapp2.RequestHandler):
	def get(self,page=None):
		header(self)
		if users.get_current_user():
			user = str(users.get_current_user())
			bound_Image=Image()
			image = bound_Image.get_author(user)
			#answers = bound_Answer.get_author_answer(user)
			show_dashboard_template={
				'image' : image,
				'user':user,
				
			}
			view_dashboard = JINJA_ENVIRONMENT.get_template('body_dashboardimage.html')
			self.response.write(view_dashboard.render(show_dashboard_template))

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
			ques.bodyreplace = replace_html(self.request.get('quebody'))
			ques.bodyreplace = ques.bodyreplace.replace('\n', '<br>')
			ques.tags = strip_tags(self.request.get('quetag'))
			ques.put()

		header(self)
		if users.get_current_user():
			self.response.write('<p class="main"><b>Success!</b></p>')
			self.response.write('<p class="main"><a href="/dashboard">My Question and Answers</a></p>')
			time.sleep(0.1)
			self.redirect('/dashboard') 
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
		ques.bodyreplace = replace_html(self.request.get('quebody'))
		ques.bodyreplace = ques.bodyreplace.replace('\n', '<br>' )

		ques.tags = strip_tags(self.request.get('quetag'))
		ques.put()

		if ques.author == str(users.get_current_user()):
			self.response.write('<p class="main"><b>Success!</b></p>')
			self.response.write('<p class="main"><a href="/dashboard">My Question and Answers</a></p>')
		time.sleep(0.1)
		self.redirect('/dashboard') 
		tail(self)


class Delete_Question(webapp2.RequestHandler):
	def get(self, key):
		header(self)
		bound_question=Question()
		bound_answer=Answer()
		if users.get_current_user():
			cur_question = bound_question.get_by_id(int(key))
			if cur_question.author == str(users.get_current_user()):		
				cur_question.key.delete()
				answer=bound_answer.get_question(key)
				for ans in answer:
					ans.key.delete()
				self.response.write('<p class="main"><b>Success!</b></p>')
				self.response.write('<p class="main"><a href="/dashboard">My Questions</a></p>')
				time.sleep(0.1)
				self.redirect('/dashboard') 
		else:
			self.response.write('<p class="main"><b>Permission Denial</b></p>')
			self.response.write('<p class="main"><a href="/dashboard">My Questions</a></p>')
		tail(self)



class Create_Answer(webapp2.RequestHandler):
    def show(self,key):
        bound_question=Question()
        cur_question = bound_question.get_by_id(int(key))
        create_question_template = {
            'c_url' :"/dashboard/questionkey="+key+"/answer",
            'c_title' : 'Answer Name',
            'c_body':'Enter your Answers here',
            'c_new':1,
            'cur_question':cur_question

        }
        send_create_question_template= JINJA_ENVIRONMENT.get_template('body_create_answer.html')
        self.response.write(send_create_question_template.render(create_question_template))

    def get(self,key):
        header(self)
        if users.get_current_user():
            self.show(key)
        tail(self)

    def post(self,key):
        ans= Answer()
        bound_question=Question()
        cur_question = bound_question.get_by_id(int(key))
        if users.get_current_user():
            ans.author = str(users.get_current_user())
            ans.qkey = key
            ans.qauthor = cur_question.author
            ans.qtitle= cur_question.title
            ans.qbody = cur_question.body
            ans.qbodyreplace = replace_html(cur_question.body)
            ans.qbodyreplace = ans.qbody.replace('\n', '<br>' )

            ans.title = self.request.get('anstitle')

            if ans.title == '':
                ans.title = 'DEFAULT_ANSWER_NAME'
            ans.body = self.request.get('ansbody')
            ans.bodyreplace = replace_html(self.request.get('ansbody'))
            ans.bodyreplace = ans.bodyreplace.replace('\n', '<br>' )

            ans.put()

        header(self)
        if users.get_current_user():
            self.response.write('<p class="main"><b>Success!</b></p>')
            self.response.write('<p class="main"><a href="/">MainPage</a></p>')
            self.response.write('<p class="main"><a href="/view=%s">To the Question</a></p>' %key)
            time.sleep(0.1)
            self.redirect("/view=%s" %key) 
        tail(self)

class Edit_Answer(webapp2.RequestHandler):
    def show(self,key):
        bound_answer=Answer()
        bound_question=Question()
        cur_answer = bound_answer.get_by_id(int(key))
        cur_question = bound_question.get_by_id(int(cur_answer.qkey))
        create_question_template = {
            'c_url' :"/dashboard/answeredit="+key,
            'c_title' : cur_answer.title,
            'c_body': cur_answer.body,
            'c_new':0,
            'cur_question':cur_question

        }
        send_create_question_template= JINJA_ENVIRONMENT.get_template('body_create_answer.html')
        self.response.write(send_create_question_template.render(create_question_template))

    def get(self,key):
        header(self)
        if users.get_current_user():
            self.show(key)
        tail(self)

    def post(self,key):
        bound_answer= Answer()
        bound_question=Question()
        cur_answer = bound_answer.get_by_id(int(key))
        qkey =cur_answer.qkey
        cur_question = bound_question.get_by_id(int(cur_answer.qkey))
        if users.get_current_user():

            cur_answer.title = self.request.get('anstitle')

            if cur_answer.title == '':
                cur_answer.title = 'DEFAULT_ANSWER_NAME'
            cur_answer.body = self.request.get('ansbody')
            cur_answer.bodyreplace = replace_html(self.request.get('ansbody'))
            cur_answer.bodyreplace = cur_answer.bodyreplace.replace('\n', '<br>' )
            cur_answer.put()

        header(self)
        if users.get_current_user():
            self.response.write('<p class="main"><b>Success!</b></p>')
            self.response.write('<p class="main"><a href="/">MainPage</a></p>')
            self.response.write('<p class="main"><a href="/view=%s">To the Question</a></p>' %qkey)
            time.sleep(0.1)
            self.redirect('/view=%s' % qkey)
        tail(self)

class Delete_Answer(webapp2.RequestHandler):
	def get(self, key):
		header(self)
		bound_answer=Answer()
		if users.get_current_user():
			cur_answer = bound_answer.get_by_id(int(key))
			if cur_answer.author == str(users.get_current_user()):		
				cur_answer.key.delete()
				
				self.response.write('<p class="main"><b>Success!</b></p>')
				self.response.write('<p class="main"><a href="/dashboard/answer">My Answers</a></p>')
		else:
			self.response.write('<p class="main"><b>Permission Denial</b></p>')
			self.response.write('<p class="main"><a href="/dashboard/answer">My Answers</a></p>')
		tail(self)


class Upload_Image(webapp2.RequestHandler):
	def get(self):
		header(self)
		display = JINJA_ENVIRONMENT.get_template('body_upload.html')
		self.response.write(display.render())
		tail(self)


	def post(self):
		header(self)
		if users.get_current_user():
			bound_image = Image()
			avatar = self.request.get('img')
			bound_image.name = self.request.get('i_name')
			if bound_image.name  == '':
				bound_image.name  = 'DEFAULT_IMAGE_NAME'
			bound_image.image = avatar

			bound_image.author = str(users.get_current_user())
			image_key = bound_image.put()
			image = bound_image.get_by_id(image_key.id())
			image.url = str(image_key.id())+"_"+self.request.params['img'].filename

			image.put()

			self.response.write('<p class="main">Upload Success!</p>')
			self.response.write('<p class="main"><a href="/dashboard/image">My Images</a></p>')

		tail(self)


class Delete_Image(webapp2.RequestHandler):
	def get(self, key):
		header(self)
		bound_image=Image()
		if users.get_current_user():
			cur_image = bound_image.get_by_id(int(key))
			if cur_image.author == str(users.get_current_user()):		
				cur_image.key.delete()
				
				self.response.write('<p class="main"><b>Success!</b></p>')
				self.response.write('<p class="main"><a href="/dashboard/image">My Images</a></p>')
				time.sleep(1)
				self.redirect('/dashboard/image')
		else:
			self.response.write('<p class="main"><b>Permission Denial</b></p>')
			self.response.write('<p class="main"><a href="/dashboard/image">My Images</a></p>')
			#time.sleep(3)
			#self.redirect('/dashboard/image')
		tail(self)		

app = webapp2.WSGIApplication([
	('/dashboard/upload', Upload_Image),
	('/dashboard/imagedelete=(.*)', Delete_Image),
	('/dashboard/image', DashboardImage),
	('/dashboard/answerdelete=(.*)', Delete_Answer),
	('/dashboard/delete=(.*)', Delete_Question),
	('/dashboard/edit=(.*)', Edit_Question),
	('/dashboard/questionkey=(.*)/answer', Create_Answer),
	('/dashboard/answeredit=(.*)', Edit_Answer),
	('/dashboard/answer', DashboardAnswer),
	('/dashboard/create', Create_Question),
	('/dashboard/([0-9]*)', Dashboard),
    ('/dashboard', Dashboard),
], debug=True)