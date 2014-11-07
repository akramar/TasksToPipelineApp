import hashlib
import random
import json as simplejson
import webapp2
from taskstopipeline.helpers import *
from taskstopipeline.models.sharelink import ShareLink
from taskstopipeline.view_models import *
from jinja2 import Environment, PackageLoader
from Crypto.Cipher import AES
from base_handler import BaseHandler


class ShareHandler(BaseHandler):  # This is the '/share/<route_share_key>' handler
    def get(self, route_share_key):
        req_share_key = route_share_key
        existing_share_links = ShareLink.query(ShareLink.share_key == req_share_key).fetch()

        if len(existing_share_links) == 0:
            template_values = {'error_message': 'list not available'}
            self.render_template('error.html', template_values)
            return

        share_link = existing_share_links[0]
        assert isinstance(share_link, ShareLink)
        vm = ShareHandlerVM(user_id=share_link.user_id)  # (user_id=share_link.user_id)
        vm.selected_list_id = share_link.list_id

        task_list = TaskList(user_id=share_link.user_id)
        task_list.id = share_link.list_id
        vm.selected_task_list = task_list.get_list_info()
        vm.selected_task_list.share_key = share_link.share_key
        vm.selected_task_list.task_groups = vm.selected_task_list.get_groups()
        vm.is_share = True

        assert isinstance(self.request, webapp2.Request)
        vm.template_values['share_url'] = self.request.host_url + '/share/' + vm.selected_task_list.share_key
        vm.template_values['selected_task_list'] = vm.selected_task_list
        vm.template_values['groups_to_show'] = vm.selected_task_list.task_groups
        vm.template_values['is_share'] = vm.is_share
        # self.render_template('index5.html', vm.template_values)
        self.render_template('list_share.html', vm.template_values)


class CreateShareLink(webapp2.RequestHandler):  # /share/create theoretically we're only calling this from javascript
    def get(self):
        user_id_encoded = self.request.get('user_id')  # ''  #
        req_list_id_sent = self.request.get('req_list')  #
        existing_share_links = ShareLink.query(ShareLink.list_id == req_list_id_sent).fetch()

        if len(existing_share_links) > 0:
            json_data = {"share_key": existing_share_links[0].share_key}
            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
            self.response.out.write(simplejson.dumps(json_data))
            return

        user_id_decoded = user_id_decoder(encoded_uid=user_id_encoded)
        existing_credential_models = UserModel.query(UserModel.user_id == user_id_decoded).fetch()
        credential = existing_credential_models[0].credential

        if credential is None:
            template_values = {'error_message': 'credentials not found'}
            env = Environment(loader=PackageLoader('taskstopipeline', 'views'))
            view = env.get_template('error.html')
            self.response.out.write(view.render(template_values))
            return

        http = httplib2.Http()
        http = credential.authorize(http=http)
        service = build('tasks', 'v1', http=http)

        raw_task_lists = service.tasklists().list().execute()
        available_lists = []
        for raw_task_list in raw_task_lists['items']:
            tl = TaskList(user_id=user_id_decoded)
            tl.id = raw_task_list['id']
            tl.title = raw_task_list['title']
            available_lists.append(tl)

        req_list = next((tl for tl in available_lists if tl.id == req_list_id_sent), None)

        if req_list is None:
            template_values = {"error_message": "requested list doesn't exist under user"}
            env = Environment(loader=PackageLoader('taskstopipeline', 'views'))
            view = env.get_template('error.html')
            self.response.out.write(view.render(template_values))
            return

        new_share_key = base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(),
                                         random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')[:16]
        new_share_link = ShareLink(share_key=new_share_key, user_id=user_id_decoded, list_id=req_list.id)
        new_share_link.put()

        json_data = {"share_key": new_share_key}  # , "user_id": user_id_decoded}
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(simplejson.dumps(json_data))


class DeleteShareLink(webapp2.RequestHandler):
    def get(self):
        user_id_encoded = self.request.get('user_id')  # ''  #
        list_id_sent = self.request.get('list_id')  #
        existing_share_links = ShareLink.query(ShareLink.list_id == list_id_sent).fetch()  # catching them all

        if len(existing_share_links) == 0:
            json_data = {"result_message": "no share keys found"}
            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
            self.response.out.write(simplejson.dumps(json_data))
            return

        cipher = AES.new(CRYPTO_SALT)
        decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
        user_id_decoded = decode_aes(cipher, urllib.unquote_plus(user_id_encoded))
        existing_credential_models = UserModel.query(UserModel.user_id == user_id_decoded).fetch()

        if len(existing_credential_models) == 0:
            json_data = {"result_message": "no credentials found"}
            self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
            self.response.out.write(simplejson.dumps(json_data))
            return

        credential = existing_credential_models[0]
        assert isinstance(credential, UserModel)

        delete_count = 0
        for share_link in existing_share_links:
            if share_link.user_id == credential.user_id:
                assert isinstance(share_link, ShareLink)
                share_link.key.delete()
                delete_count += 1

        json_data = {"result_message": "keys deleted: " + str(delete_count)}
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(simplejson.dumps(json_data))
        return