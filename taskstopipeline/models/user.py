from oauth2client.appengine import CredentialsNDBProperty
from google.appengine.ext import ndb


#class CredentialsModel(ndb.Model):
class UserModel(ndb.Model):
    # https://developers.google.com/appengine/docs/python/ndb/
    #credential = CredentialsProperty()
    credential = CredentialsNDBProperty()
    user_id = ndb.StringProperty()
    user_raw = ndb.UserProperty()
    user_email = ndb.StringProperty()
    last_login = ndb.DateTimeProperty()