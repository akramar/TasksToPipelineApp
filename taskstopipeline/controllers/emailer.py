from jinja2 import Environment, PackageLoader
from google.appengine.api import mail
from taskstopipeline.models.sharelink import ShareLink
from taskstopipeline.view_models import *
from taskstopipeline.helpers import *
import premailer
from base_handler import BaseHandler
import logging


class EmailerHandler(BaseHandler):
    def post(self):
        user_id_encoded = self.request.get('user_id')  # ''  #
        req_list_id_sent = self.request.get('req_list')  #
        email_dest = self.request.get('email_dest')
        email_subj = self.request.get('email_subj')

        user_id_decoded = user_id_decoder(encoded_uid=user_id_encoded)
        #existing_credential_models = UserModel.query(UserModel.user_id == user_id_decoded).fetch()
        #credential = existing_credential_models[0].credential

        vm = ListHandlerVM(user_id=user_id_decoded)
        vm.is_share = True
        logging.info("req_list_id = " + (req_list_id_sent if req_list_id_sent is not None else "no list specified"))
        available_lists = vm.get_available_lists()

        #  Get the first list matching req_list_id
        vm.selected_task_list = next((tl for tl in available_lists if tl.id == req_list_id_sent), None)
        vm.selected_task_list.settings = vm.selected_task_list.get_settings()
        vm.selected_task_list.task_groups = vm.selected_task_list.get_groups()
        logging.info(vm.selected_task_list)

        #  Search for a share key
        existing_share_links = ShareLink.query(ShareLink.list_id == vm.selected_task_list.id).fetch()
        if len(existing_share_links) > 0:
            vm.selected_task_list.share_key = existing_share_links[0].share_key
            vm.template_values['share_url'] = self.request.host_url + '/share/' + vm.selected_task_list.share_key

        vm.template_values['selected_task_list'] = vm.selected_task_list
        vm.template_values['groups_to_show'] = vm.selected_task_list.task_groups
        vm.template_values['is_share'] = vm.is_share
        vm.template_values['page_is_email'] = True
        # self.render_template('index5.html', vm.template_values)

        env = Environment(loader=PackageLoader('taskstopipeline', 'views'))
        #  view = env.get_template('index5.html')
        view = env.get_template('list_email.html')
        view_rendered = view.render(vm.template_values)

        external_style_links = ['/assets/css/style-email.css']
        # external_styles=external_style_links

        view_styled = premailer.Premailer(html=view_rendered, base_url=self.request.host_url,
                                          exclude_pseudoclasses=True, external_styles=external_style_links).transform()


        #logging.info(view_styled)

        message = mail.EmailMessage(sender="akramar@coahadesign.com",
                                    subject=email_subj)  # "test outgoing")

        #if to contains ;, then split
        message.to = email_dest  # "alain.kramar@gmail.com"
        message.body = view_styled
        message.html = view_styled
        message.send()

        logging.info("returning to calling method.")

        # self.response.out.write(view.render(vm.template_values))

        return