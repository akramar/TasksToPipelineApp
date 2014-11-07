from google.appengine.ext import ndb


class TaskListSettings(ndb.Model):
    user_id = ndb.StringProperty()
    list_id = ndb.StringProperty()
    settings = ndb.JsonProperty()