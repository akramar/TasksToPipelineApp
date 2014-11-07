from apiclient.discovery import build
import httplib2
from taskstopipeline.models.tasklist import TaskList
from taskstopipeline.models.user import UserModel


class BaseVM(object):
    template_values = {}

    def __init__(self):
        pass


class BaseListVM(BaseVM):
    selected_task_list = None
    is_share = True  # TODO: remove this variable, it's confusing. we are now rendering children through jinja instead
    user = UserModel()

    def __init__(self, user_id):
        self.selected_task_list = TaskList(user_id=user_id)
        existing_user_models = UserModel.query(UserModel.user_id == user_id).fetch()
        if len(existing_user_models) > 0:
            self.user = existing_user_models[0]

            http = httplib2.Http()
            #assert isinstance(credential, oauth2client.client.OAuth2Credentials)
            http = self.user.credential.authorize(http=http)
            self.service = build('tasks', 'v1', http=http)
        else:
            raise Exception("Disaster in BaseListVM, existing_user_models is empty. user_id=" + user_id)

    def get_groups(self):
        return self.selected_task_list.get_groups()  # self)


class ListHandlerVM(BaseListVM):  # This is for the private page
    available_task_lists = []

    def __init__(self, user_id):
        super(ListHandlerVM, self).__init__(user_id=user_id)
        self.is_share = False

    def get_available_lists(self):
        raw_task_lists = self.service.tasklists().list().execute()
        self.available_task_lists = []
        for raw_task_list in raw_task_lists['items']:
            #logging.info(raw_task_list)
            tl = TaskList(user_id=self.user.user_id)
            #logging.info(raw_task_list['id'])
            tl.id = raw_task_list['id']
            tl.title = raw_task_list['title']
            self.available_task_lists.append(tl)

        return self.available_task_lists


class ShareHandlerVM(BaseListVM):  # This is for the public (share) page

    def __init__(self, user_id):
        super(ShareHandlerVM, self).__init__(user_id=user_id)
        self.is_share = True