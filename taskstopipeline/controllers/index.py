import logging
from jinja2 import Environment, PackageLoader
from google.appengine.api import users
import webapp2
from taskstopipeline.config import *
from taskstopipeline.view_models import *
from base_handler import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        self.redirect('/list')


class AuthCallbackHandler(webapp2.RequestHandler):
    def get(self):
        auth_code = self.request.get('code')
        logging.info("authCode = " + auth_code)
        user = users.get_current_user()
        FLOW.redirect_uri = OAUTH_REDIRECT_URI
        new_credential = FLOW.step2_exchange(auth_code)
        #new_user_key = base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(),
        #                               random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')[:16]

        #credential.user_ref_id.content = 'test_id'  ##see if this works
        #storage = StorageByKeyName(CredentialsModel, 'defaultKey', 'credential')

        if new_credential.refresh_token is not None:
            #storage = StorageByKeyName(CredentialsModel, user.user_id(), 'credential')
            #storage.put(credential)
            new_credential = UserModel(user_id=user.user_id(), credential=new_credential)
            new_credential.put()
            self.redirect('/list')

        else:
            template_values = {'error_message': 'no refresh token provided'}
            env = Environment(loader=PackageLoader('taskstopipeline', 'views'))
            view = env.get_template('error.html')
            self.response.out.write(view.render(template_values))


class UserTestHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Hello, ' + user.nickname())
            self.response.write('_User__user_id' + user.user_id())

        else:
            self.redirect(users.create_login_url(self.request.uri))