from google.appengine.ext.webapp.util import run_wsgi_app
from taskstopipeline.controllers.emailer import *
from taskstopipeline.controllers.index import *
from taskstopipeline.controllers.list import *
from taskstopipeline.controllers.share import *
from taskstopipeline.controllers.settings import *


app = webapp2.WSGIApplication([('/', IndexHandler),
                               ('/oauth2callback', AuthCallbackHandler),
                               ('/share/create', CreateShareLink),
                               ('/share/delete', DeleteShareLink),
                               ('/usertest', UserTestHandler),
                               webapp2.Route(r'/list', handler=TaskListHandler),
                               webapp2.Route(r'/list/', handler=TaskListHandler),
                               webapp2.Route(r'/list/<route_list_id>', handler=TaskListHandler),
                               webapp2.Route(r'/share/<route_share_key>', handler=ShareHandler),
                               webapp2.Route(r'/emailer/send', handler=EmailerHandler),
                               ('/settings/task', GroupSettingsHandler)],
                              debug=True)


def main():
    run_wsgi_app(app)