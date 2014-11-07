from apiclient.discovery import build
import httplib2
import logging
import re
from taskstopipeline.models.task import Task
from taskstopipeline.models.taskgroup import TaskGroup
from taskstopipeline.models.taskgroupsettings import TaskGroupSettings
from taskstopipeline.models.tasklistsettings import TaskListSettings
from taskstopipeline.models.user import UserModel


class TaskList:
    id = ''
    title = ''
    task_groups = []
    share_key = ''
    settings = {}
    user_id = ''

    def __init__(self, user_id):
        self.user_id = user_id

    def get_list_info(self):
        if id == '':
            logging.debug('no list id available')
            return None

        #storage = StorageByKeyName(CredentialsModel, user_id, 'credential')
        #credential = storage.get()

        existing_credential_models = UserModel.query(UserModel.user_id == self.user_id).fetch()
        credential = existing_credential_models[0].credential

        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('tasks', 'v1', http=http)

        task_list_data = service.tasklists().get(tasklist=self.id).execute()
        self.title = task_list_data['title']
        #  "kind": "tasks#taskList",
        #  "id": "MDA0OTc3MTMzMjcwMzk0NTQ5NjM6Nzow",
        #  "etag": "\"MkJ9AekQH8ZX7XUvmO-wEa1_AO0/bvOHa-boMXGy91a8f3ABNlSS1mo\"",
        #  "title": "HLM Loans",
        #  "updated": "2014-08-15T04:25:30.000Z",
        #  "selfLink": "https://www.googleapis.com/tasks/v1/users/@me/lists/MDA0OTc3MTMzMjcwMzk0NTQ5NjM6Nzow"

        return self

    def get_settings(self):
        if id == '':
            logging.debug('no list id available')
            return None

        setting_models = TaskListSettings.query(TaskListSettings.list_id == self.id
                                                and TaskListSettings.user_id == self.user_id).fetch()

        if len(setting_models) == 0:
            return None

        self.settings = setting_models[0].settings
        return self.settings

    def get_groups(self):
        logging.info("list_id: " + self.id)

        #storage = StorageByKeyName(CredentialsModel, user_id, 'credential')
        #credential = storage.get()
        existing_user_models = UserModel.query(UserModel.user_id == self.user_id).fetch()
        credential = existing_user_models[0].credential

        http = httplib2.Http()
        http = credential.authorize(http)
        service = build('tasks', 'v1', http=http)

        #raw_list = http.service.tasks().list(tasklist=id).execute(http=http)
        raw_list = service.tasks().list(tasklist=self.id).execute(http=http)
        #result = self.service.tasks().list(tasklist='MDA0OTc3MTMzMjcwMzk0NTQ5NjM6Nzow').execute(http=self.http)
        all_tasks = raw_list.get('items', [])
        logging.info("all tasks count: " + str(len(all_tasks)))
        # for task in alltasks:
        # task['title_short'] = truncate(task['title'], 26)

        self.task_groups = []
        # Build our main loan groups that start with ***
        for task in all_tasks:
            #if task['title'].startswith('***') or ('parent' not in task and task['title'].strip() != ''):
            if 'parent' not in task and task['title'].strip() != '':
                new_group = TaskGroup()

                settings_entities = TaskGroupSettings.query(TaskGroupSettings.user_id == self.user_id
                                                            and TaskGroupSettings.list_id == self.id
                                                            and TaskGroupSettings.task_id == task['id']).fetch()

                if len(settings_entities) > 0:
                    new_group.settings = settings_entities[0].settings

                '''
                if task.has_key('notes'):
                    data_lines = [s.strip() for s in task['notes'].splitlines()]
                    #new_group.notes = dict(s.split(':') for s in data_lines)
                    #new_group.notes = [dict(s.split(':')) for s in task['notes'].splitlines()]
                    new_group.settings = dict(s.split(':') for s in data_lines)
                '''

                if 'hidden' in new_group.settings and new_group.settings['hidden'] is True:
                    continue

                new_group.task_raw = task
                #new_group.title = task['title'][3:-3]  ##this is the part truncating the stars, make optional
                #new_group.title = task['title'].translate(None, '*') #  breaks in GAE
                new_group.title = re.sub('[*]', '', task['title'])
                new_group.id = task['id']
                new_group.task_items = []
                logging.info("new group: " + str(new_group))
                self.task_groups.append(new_group)

                filtered_tasks = filter(lambda t: t.has_key('parent')  # 'parent' in t)  # 'parent' breaks in GAE
                                        and t['parent'] == new_group.id
                                        and t['title'].strip() != ''
                                        and t['status'] == 'needsAction', all_tasks)

                logging.info("filtered_tasks count: " + str(len(filtered_tasks)))
                for ft in filtered_tasks:
                    new_task = Task()
                    index_of_first_hyphen = ft['title'].index(' - ') if ' - ' in ft['title'] else None
                    if index_of_first_hyphen is not None:
                        new_task.title = ft['title'][:index_of_first_hyphen]
                        new_task.text = ft['title'][index_of_first_hyphen + 3:]

                    else:
                        new_task.title = ft['title']
                        new_task.text = ""

                    new_group.task_items.append(new_task)

                if 'sort' in new_group.settings:
                    if new_group.settings['sort'] == 'alpha':
                        new_group.task_items.sort(key=lambda t: t.title)

        logging.info("group list: ")
        logging.info(self.task_groups)
        return self.task_groups

