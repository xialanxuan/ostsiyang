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
from google.appengine.api import images


import jinja2
import webapp2
import urllib
import re
import time

from model import *




JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def replace_html(string):
  newstring = re.sub(r'(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)', r'<a href="\1">\1</a>', string)
  string = re.sub(r'<a href="(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)">[^\s]+.jpg</a>', r'<img src="\1">', newstring)
  newstring = re.sub(r'<a href="(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)">[^\s]+.png</a>', r'<img src="\1">', string)
  string = re.sub(r'<a href="(\http[s]?://[^\s<>"]+|www\.[^\s<>"]+)">[^\s]+.gif</a>', r'<img src="\1">', newstring)
  return string

def header(self):
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


def body(self):
        user = users.get_current_user()
        if user:
            user_control = 1

        else:
            user_control = 0

        bound_ques = Question()
        m_ques = bound_ques.get_all_question()

        template_body_value = {
            'user_control': user_control,
            'm_ques': m_ques
        }
        body = JINJA_ENVIRONMENT.get_template('body_main.html')
        self.response.write(body.render(template_body_value))


def tail(self):
		tail = JINJA_ENVIRONMENT.get_template('tail.html')
		self.response.write(tail.render())

class MainPage(webapp2.RequestHandler):
    def get(self,page=None):
        header(self)

        user = users.get_current_user()
        if user:
            user_control = 1

        else:
            user_control = 0
        bound_que=Question()

        if not page:
            page = str(0)
            m_ques = bound_que.get_some(1)
            older_url = "/2"
            
        else:        
            m_ques = bound_que.get_some(int(page))
            older_url = "/"+str((int(page)+1))

        template_get_body_value = {
            'user_control': user_control,
            'm_ques': m_ques,
            'page' : page,
            'older_url' : older_url,
        }
        body = JINJA_ENVIRONMENT.get_template('body_main.html')
        self.response.write(body.render(template_get_body_value))

		#body(self)
        tail(self)
 
class QuestionView(webapp2.RequestHandler):
    def get(self,que_key):
        header(self)
        bound_que=Question()
        bound_ans=Answer()
        user = str(users.get_current_user())
        q_v_que=bound_que.get_by_id(int(que_key))
        q_v_ans=bound_ans.get_question(que_key)
        template_values={
        'que_key':que_key,
        'q_v_que': q_v_que,
        'q_v_ans': q_v_ans,
        'user': user,
        }
        display = JINJA_ENVIRONMENT.get_template('body_view_question.html')
        self.response.write(display.render(template_values))
        tail(self)


class AuthorView(webapp2.RequestHandler):
    def get(self,author,page=None):
        header(self)
        bound_que=Question()
        #q_a_que=bound_que.get_author_question_page(author)
        if not page:
            page = str(0)
            q_a_que = bound_que.get_author_question_page(author,1)
            older_url = "/p2"
            
        else:        
            q_a_que = bound_que.get_author_question_page(author,int(page))
            older_url = "/author="+author+"/p"+str((int(page)+1))
        template_values={
        'author': author,
        'q_a_que': q_a_que,
        'page': page,
        'older_url':older_url,
        }
        display = JINJA_ENVIRONMENT.get_template('body_author_question.html')
        self.response.write(display.render(template_values))
        tail(self)

class TagView(webapp2.RequestHandler):
    def get(self, tag, page=None):
        header(self)
        bound_que=Question()
        if page:
            t_que = bound_que.get_tagged_some(tag, int(page))
            older_url = "/tag="+tag+"/"+str((int(page)+1))
        else:
            page = str(0)
            t_que = bound_que.get_tagged_some(tag, 1)
            older_url = "/tag="+tag+"/2"

        
        temp_vals = { 'tag' : tag,
            'page' : page,
            't_que' : t_que,
            'older_url' : older_url
            }

        display = JINJA_ENVIRONMENT.get_template('body_tag.html')
        self.response.write(display.render(temp_vals))
        tail(self)


class UpQuestion(webapp2.RequestHandler):
    def get(self,key):
        header(self) 
        self.redirect('/view=' + key) 
        tail(self)       

    def post(self,key):
        header(self) 
        user=str(users.get_current_user())
        bound_que=Question()
        question=bound_que.get_by_id(int(key))
        if user:
            if question:
                if user in question.up:
                    self.redirect('/view=' + key) 
                else:
                    question.up.append(user)
                    question.put()
        else:
            self.response.write('<p class="main"><b>Wrong</b></p>')
            self.response.write('<p class="main"><a href="/">MainPage</a></p>')
        time.sleep(1)
        self.redirect('/view=' + key) 
        tail(self)
        
class DownQuestion(webapp2.RequestHandler):
    def get(self,key):
        header(self) 
        self.redirect('/view=' + key) 
        tail(self)       

    def post(self,key):
        header(self) 
        user=str(users.get_current_user())
        bound_que=Question()
        question=bound_que.get_by_id(int(key))
        if user:
            if question:
                if user in question.down:
                    self.redirect('/view=' + key) 
                else:
                    question.down.append(user)
                    question.put()
        else:
            self.response.write('<p class="main"><b>Wrong</b></p>')
            self.response.write('<p class="main"><a href="/">MainPage</a></p>')
        time.sleep(1)
        self.redirect('/view=' + key) 
        tail(self)


class UpAnswer(webapp2.RequestHandler):
    def get(self,qkey,akey):
        header(self) 
        self.redirect('/view=' + qkey) 
        tail(self)       

    def post(self,qkey,akey):
        header(self) 
        user=str(users.get_current_user())
        bound_ans=Answer()
        answer=bound_ans.get_by_id(int(akey))
        if answer:
            if user in answer.up:
                self.redirect('/view=' + qkey) 
            else:
                answer.up.append(user)
                answer.put()
        else:
            self.response.write('<p class="main"><b>Wrong</b></p>')
            self.response.write('<p class="main"><a href="/">MainPage</a></p>')
        time.sleep(1)
        self.redirect('/view=' + qkey) 
        tail(self)
        
class DownAnswer(webapp2.RequestHandler):
    def get(self,qkey,akey):
        header(self) 
        self.redirect('/view=' + qkey) 
        tail(self)       

    def post(self,qkey,akey):
        header(self) 
        user=str(users.get_current_user())
        bound_ans=Answer()
        answer=bound_ans.get_by_id(int(akey))
        if user:
            if answer:
                if user in answer.down:
                    self.response.write('<p class="main"><b>No</b></p>')

                    #self.redirect('/view=' + qkey) 
                else:
                    answer.down.append(user)
                    answer.put()
        else:
            self.response.write('<p class="main"><b>Wrong</b></p>')
            self.response.write('<p class="main"><a href="/">MainPage</a></p>')
        time.sleep(1)
        self.redirect('/view=' + qkey) 
        tail(self)

class ImageView(webapp2.RequestHandler):
    def get(self, url):
        bound_image=Image()
        image = bound_image.get_url(url)
        for im in image:
            if im.image:
                self.response.headers['Content-Type'] = 'image/png'
                self.response.out.write(im.image)


app = webapp2.WSGIApplication([
    (r'/upans/qkey=(.*)/akey=(.*)', UpAnswer),
    (r'/downans/qkey=(.*)/akey=(.*)', DownAnswer),
    (r'/up/qkey=(.*)', UpQuestion),
    (r'/down/qkey=(.*)', DownQuestion),
    (r'/image=(.*)', ImageView),
    (r'/tag=(.*)/([0-9]*)', TagView),
    (r'/tag=(.*)', TagView),
    (r'/author=(.*)/p([0-9]*)', AuthorView),
    (r'/author=(.*)', AuthorView),
    (r'/view=(.*)', QuestionView),
    ('/([0-9]*)', MainPage),
    ('/', MainPage),
], debug=True)