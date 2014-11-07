from google.appengine.ext import ndb


class ShareLink(ndb.Model):
    # https://developers.google.com/appengine/docs/python/ndb/
    share_key = ndb.StringProperty()
    user_id = ndb.StringProperty()
    list_id = ndb.StringProperty()