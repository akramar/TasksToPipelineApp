from google.appengine.ext import ndb


class TaskGroupSettings(ndb.Model):
    user_id = ndb.StringProperty()
    task_id = ndb.StringProperty()
    list_id = ndb.StringProperty()
    settings = ndb.JsonProperty()