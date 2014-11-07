import webapp2
from webapp2_extras import jinja2
from jinja2 import Environment, PackageLoader

#template_dir = os.path.join(os.path.dirname(__file__), "taskstopipeline/views")
#jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("taskstopipeline/views"), autoescape=True)
#template_dir = '/path/to/views'
#loader = jinja2.FileSystemLoader(template_dir)
#environment = jinja2.Environment(loader=loader)


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, template_values):  # **template_args):
        env = Environment(loader=PackageLoader('taskstopipeline', 'views'))
        view = env.get_template(filename)
        self.response.out.write(view.render(template_values))
        #self.response.write(self.jinja2.render_template(view, **template_args))