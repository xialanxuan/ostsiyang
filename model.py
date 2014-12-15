from google.appengine.ext import ndb


DEFAULT_QUESTION_NAME = 'untitled_question'

def que_key(c_title=DEFAULT_QUESTION_NAME):
	return ndb.key('Question', c_title)

class Image(ndb.Model):
    ifile = ndb.BlobProperty()
    url = ndb.StringProperty()
    user = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_author(cls, user):
        q = Image.query(Image.user == user)
        q.order(-Image.date)
        return q.fetch()




class Question(ndb.Model):  
    author = ndb.StringProperty()
    qid = ndb.StringProperty()
    title = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
    edit = ndb.DateTimeProperty(auto_now=True)
    body = ndb.TextProperty(indexed=False)
    tags = ndb.StringProperty(repeated=True)
    up = ndb.StringProperty()
    down = ndb.StringProperty()

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
    author = ndb.StringProperty()
    title = ndb.StringProperty()
    body = ndb.TextProperty(indexed=False)


    def get_author(cls,user):
    	q = Short_Ques.query(Short_Ques.author == user)
    	return q.fetch()


    def has_que(cls,user,que):
    	q = Short_Ques.query(ndb.AND(Short_Ques.author == user, Short_Ques.title == que))
    	x = q.get()
    	if x:
    		return True
    	else:
    		return False
