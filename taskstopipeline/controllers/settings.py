import json as simplejson
import webapp2
import logging
from taskstopipeline.helpers import *
from taskstopipeline.models.taskgroupsettings import TaskGroupSettings
from taskstopipeline.view_models import *
from Crypto.Cipher import AES

#  Available settings:
#  sort: alpha
#  color: anything
#  hidden: true|false
#  arrow: none


class GroupSettingsHandler(webapp2.RequestHandler):
    def post(self):

        posted_json = simplejson.loads(self.request.body)

        user_id_encoded = posted_json['user_id']  # '185804764220139124118'  #
        req_list_id_sent = posted_json['list_id']  # MDA0OTc3MTMzMjcwMzk0NTQ5NjM6Nzow
        req_task_id_sent = posted_json["task_id"]
        #settings_key = self.request.get('key')
        #settings_val = self.request.get('val')

        #  Settings sent
        setting_hidden = posted_json["is_hidden"]
        setting_color = posted_json["color"]
        setting_arrow = posted_json["show_arrow"]
        setting_sort = posted_json["sort"]

        cipher = AES.new(CRYPTO_SALT)
        decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
        user_id_decoded = decode_aes(cipher, urllib.unquote_plus(user_id_encoded))
        existing_credential_models = UserModel.query(UserModel.user_id == user_id_decoded).fetch()

        if len(existing_credential_models) == 0:
            self.settings_response("invalid credentials")

        credential = existing_credential_models[0].credential

        # Get the task group in question
        #http = httplib2.Http()
        #http = credential.authorize(http)
        #service = build('tasks', 'v1', http=http)
        #task = service.tasks().get(tasklist=req_list_id_sent, task=req_task_id_sent).execute()

        #if task is None:
        #    self.settings_response("task not found")

        """
        data_lines = [s.strip() for s in task['notes'].splitlines()]
        notes_dict = dict(s.split(':') for s in data_lines)

        if settings_key == 'color':
            if int(settings_val, 16) < 16777216 or len(settings_val) == 3:
                notes_dict['color'] = settings_val
                self.update_settings(service=service, list_id=req_list_id_sent, task=task, settings_dict=notes_dict)
                self.settings_response("have set color")
        """

        settings_entities = TaskGroupSettings.query(TaskGroupSettings.user_id == user_id_decoded
                                                    and TaskGroupSettings.list_id == req_list_id_sent
                                                    and TaskGroupSettings.task_id == req_task_id_sent).fetch()

        new_settings = TaskGroupSettings()

        #  If it doesn't exist in results, assign it basic properties
        if len(settings_entities) == 0:
            new_settings.populate(
                user_id=user_id_decoded,
                list_id=req_list_id_sent,
                task_id=req_task_id_sent
            )

        else:
            new_settings = settings_entities[0]

        new_settings.settings = {}

        #  The Hidden setting  #
        if type(setting_hidden) is bool:
            new_settings.settings["hidden"] = setting_hidden

        #  The Color setting  #
        #  Sanitize our color then insert
        setting_color = setting_color.replace('#', '')
        try:
            if int(setting_color, 16) < 16777216 or len(setting_color) == 3:
                new_settings.settings["color"] = '#' + setting_color

        except Exception:
            logging.warning('not a valid color: ' + str(setting_color))
            logging.warning(Exception.message)

        #  The Arrow setting  #
        if type(setting_arrow) is bool:
            new_settings.settings['arrow'] = setting_arrow

        #  The Sort setting  #
        #  shorten in case of bad input, longest string is "alpha"
        if len(setting_sort) < 6 and setting_sort != 'none':
            new_settings.settings['sort'] = setting_sort

        new_settings.put()

        """
            def update_settings(self, service, list_id, task, settings_dict):
                set1 = [str(kv) for kv in settings_dict]
                set2 = set1.join('\n')
                task['notes'] = set2
                result = service.tasks().update(tasklist=list_id, task=task['id'], body=task).execute()
                return
        """

        json_reply = {"setting_result": "settings saved"}
        self.response.headers.add_header('content-type', 'application/json', charset='utf-8')
        self.response.out.write(simplejson.dumps(json_reply))
        return


class ListSettingsHandler(webapp2.RequestHandler):
    def post(self):
        pass