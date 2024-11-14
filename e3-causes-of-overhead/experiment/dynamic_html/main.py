# Workload Libraries
from datetime import datetime
from random import sample
from os import path
from jinja2 import Template


SCRIPT_DIR = path.abspath(path.join(path.dirname(__file__)))


# Dyanmic HTML function
def task(event, span):
    name = event.get('username')
    size = event.get('random_len')
    cur_time = datetime.now()

    # Add attributes to the span
    span.set_attribute("username", name)
    span.set_attribute("random_len", size)

    random_numbers = sample(range(0, 1000000), size)
    template_path = path.join(SCRIPT_DIR, 'templates', 'template.html')

    # Read and render template
    with open(template_path, 'r') as file:
        template = Template(file.read())

    html = template.render(username=name, cur_time=cur_time, random_numbers=random_numbers)

    # Set additional attributes if needed
    span.set_attribute("template_path", template_path)
    span.set_attribute("render_time", str(cur_time))

    # end timing and return result
    return {'result': html}

