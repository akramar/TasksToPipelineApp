from oauth2client.client import OAuth2WebServerFlow
import settings

SCOPE = 'https://www.googleapis.com/auth/tasks'

# WATCH THESE PORTS, THEY DIFFER BETWEEN GAE SDK AND PYCHARM, OTHERWISE
# YOU'LL GET REDIRECT ERRORS. MUST CHANGE BACK BEFORE DEPLOYING
OAUTH_REDIRECT_URI = 'http://localhost:8080/oauth2callback'
#OAUTH_REDIRECT_URI = 'http://taskstopipeline.com/oauth2callback'

FLOW = OAuth2WebServerFlow(client_id=settings.CLIENT_ID,
                           client_secret=settings.CLIENT_SECRET,
                           scope=SCOPE,
                           redirect_uri=OAUTH_REDIRECT_URI,
                           user_agent='taskstopipeline',
                           #access_type='offline', #  set by default
                           approval_prompt='force')


