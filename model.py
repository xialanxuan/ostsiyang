from google.appengine.ext import ndb


DEFAULT_QUESTION_NAME = 'untitled_question'
DEFAULT_ANSWER_NAME = 'untitled_answer'
DEFAULT_IMAGE_NAME = 'untitled_image'



def que_key(c_title=DEFAULT_QUESTION_NAME):
	return ndb.key('Question', c_title)

def ans_key(c_title=DEFAULT_ANSWER_NAME):
    return ndb.key('Answer', c_title)

def img_key(c_title=DEFAULT_IMAGE_NAME):
    return ndb.key('Image', i_name)

class Image(ndb.Model):
    image = ndb.BlobProperty()
    url = ndb.StringProperty()
    name = ndb.StringProperty()
    author = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_author(cls, user):
        q = Image.query(Image.author == user).order(-Image.date)
        q.order(-Image.name)
        return q.fetch()

    def get_url(cls, url):
         q = Image.query(Image.url == url)
         return q.fetch()



class Question(ndb.Model):  
    author = ndb.StringProperty()
    qid = ndb.StringProperty()
    title = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    edit = ndb.DateTimeProperty(auto_now=True)
    body = ndb.TextProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)
    up = ndb.StringProperty(repeated=True, indexed=False)
    down = ndb.StringProperty(repeated=True, indexed=False)
    vote = ndb.ComputedProperty(lambda self: len(self.up) - len(self.down))


    def get_all_question(cls,page):
        q = Question.query().order(-Question.date)
        q.order(-Question.title)
        if int(page) > 0:
            p = int(page)*10 - 10
            return q.fetch(10, offset=p)
        else:
            return q.fetch(10)

    def get_author_question(cls,user):
        q = Question.query(Question.author == user).order(-Question.date)
        q.order(-Question.title)
        return q.fetch()


    def get_author_question_page(cls,user,page):
        q = Question.query(Question.author == user).order(-Question.date)
        q.order(-Question.title)
        if int(page) > 0:
            p = int(page)*10 - 10
            return q.fetch(10, offset=p)
        else:
            return q.fetch(10)

    def get_some(cls, page):
        q = Question.query().order(-Question.date)
        if int(page) > 0:
            p = int(page)*10 - 10
            return q.fetch(10, offset=p)
        else:
            return q.fetch(10)

    def get_tagged_some(cls, tag, page):
        q = Question.query(Question.tags == tag).order(-Question.date)
        q.order(-Question.title)
        if int(page) > 0:
            p = int(page)*10 - 10
            return q.fetch(10, offset=p)
        else:
            return q.fetch(10)



class Answer(ndb.Model):
    qkey = ndb.StringProperty()
    qauthor = ndb.StringProperty()
    qtitle = ndb.StringProperty()
    qbody = ndb.TextProperty(indexed=False)
    qtags = ndb.StringProperty(repeated=True)
    author = ndb.StringProperty()
    title = ndb.StringProperty()
    body = ndb.TextProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    edit = ndb.DateTimeProperty(auto_now=True)
    up = ndb.StringProperty(repeated=True, indexed=False)
    down = ndb.StringProperty(repeated=True, indexed=False)
    vote = ndb.ComputedProperty(lambda self: len(self.up) - len(self.down))


    def get_author(cls,user):
        q = Answer.query(Answer.author == user).order(-Answer.date)
        q.order(-Answer.title)
        return q.fetch()

    def get_question(cls,qkey):
        q = Answer.query(Answer.qkey == qkey).order(-Answer.vote)
        q.order(-Answer.date)
        return q.fetch()

    def has_que(cls,user,que):
    	q = Answer.query(ndb.AND(Answer.author == user, Answer.title == que))
    	x = q.get()
    	if x:
    		return True
    	else:
    		return False
