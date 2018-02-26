from jinja2 import Environment, PackageLoader, select_autoescape
from nameko.extensions import DependencyProvider


class Jinja2(DependencyProvider):

    def setup(self):
        self.template_renderer = TemplateRenderer(
            'temp_messenger', 'templates'
        )

    def get_dependency(self, worker_ctx):
        return self.template_renderer


class TemplateRenderer:

    def __init__(self, package_name, template_dir):
        self.template_env = Environment(
            loader=PackageLoader(package_name, template_dir),
            autoescape=select_autoescape(['html'])
        )

    def render_home(self, messages):
        template = self.template_env.get_template('home.html')
        return template.render(messages=messages)
