from oauth2client.client import AccessTokenRefreshError
import logging
from taskstopipeline.config import *
from taskstopipeline.helpers import *
from taskstopipeline.models.sharelink import ShareLink
from taskstopipeline.view_models import *
from google.appengine.api import users
from base_handler import BaseHandler


class TaskListHandler(BaseHandler):
    def get(self, route_list_id=None):
        user = users.get_current_user()

        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            #self.response.headers['Content-Type'] = 'text/plain'
            #self.response.write('Hello, ' + user.nickname())
            #self.response.write('_User__user_id' + user.user_id())
            return

        else:
            #storage = StorageByKeyName(CredentialsModel, user.user_id(), 'credential')
            #credential = storage.get()

            existing_credential_models = UserModel.query(UserModel.user_id == user.user_id()).fetch()

            if len(existing_credential_models) == 0:
                #template_values = {'error_message': 'no credentials found'}
                #self.render_template('error.html', template_values)
                auth_uri = FLOW.step1_get_authorize_url(OAUTH_REDIRECT_URI)
                self.redirect(auth_uri)
                return

            else:
                credential = existing_credential_models[0].credential

            #our loan tasklist is MDA0OTc3MTMzMjcwMzk0NTQ5NjM6Nzow
            #

            try:
                #https://developers.google.com/gmail/api/auth/web-server?hl=es
                #https://accounts.google.com/IssuedAuthSubTokens
                if credential is None or credential.invalid:
                    # if credentials.refresh_token is not None:
                    # store_credentials(user_id, credentials)
                    # return credentials
                    # else:
                    # credentials = get_stored_credentials(user_id)
                    # if credentials and credentials.refresh_token is not None:
                    # return credentials

                    #if credential and credential.refresh_token is not None:
                    #FLOW.access_token = credential.refresh_token
                    #   FLOW.refresh_token = credential.refresh_token
                    #credential.authorize(self)

                    #else:
                    #if credential is None and credential.refresh_token is None:
                    auth_uri = FLOW.step1_get_authorize_url(OAUTH_REDIRECT_URI)
                    self.redirect(auth_uri)
                    return

                else:
                    vm = ListHandlerVM(user_id=user.user_id())

                    vm.is_share = False  # This is already False by default, but just being sure
                    req_list_id = route_list_id
                    logging.info("req_list_id = " + (req_list_id if req_list_id is not None else "no list specified"))
                    available_lists = vm.get_available_lists()

                    if len(available_lists) == 0:
                        template_values = {'error_message': 'no lists available'}
                        self.render_template('error.html', template_values)
                        return

                    if len(available_lists) > 0 and (req_list_id is None or ''):  # defaults to selecting the first id
                        vm.selected_task_list = available_lists[0]
                        self.redirect('/list/' + vm.selected_task_list.id)
                        return

                    #  Get the first list matching req_list_id
                    vm.selected_task_list = next((tl for tl in available_lists if tl.id == req_list_id), None)
                    vm.selected_task_list.settings = vm.selected_task_list.get_settings()
                    vm.selected_task_list.task_groups = vm.selected_task_list.get_groups()
                    logging.info(vm.selected_task_list)

                    #  Search for a share key
                    existing_share_links = ShareLink.query(ShareLink.list_id == vm.selected_task_list.id).fetch()
                    if len(existing_share_links) > 0:
                        vm.selected_task_list.share_key = existing_share_links[0].share_key

                    #  Encode the userId
                    user_id_encoded = user_id_encoder(decoded_uid=user.user_id())

                    vm.template_values['task_lists'] = available_lists
                    vm.template_values['user_id_encoded'] = user_id_encoded
                    vm.template_values['selected_task_list'] = vm.selected_task_list
                    vm.template_values['groups_to_show'] = vm.selected_task_list.task_groups
                    vm.template_values['is_share'] = vm.is_share
                    # self.render_template('index5.html', vm.template_values)
                    self.render_template('list_private.html', vm.template_values)
                    #self.render_template('index3.html', listofloanstages=tasklist)

            except AccessTokenRefreshError:
                #self.response.write("An error occurred, please reload the page")
                #time.sleep(2)
                #self.redirect('/')
                #else:
                #   template_values = {
                #      'error_message': 'no key given'
                # }
                #self.render_template('error.html', template_values)
                template_values = {'error_message': 'token refresh error'}
                self.render_template('error.html', template_values)
                return

