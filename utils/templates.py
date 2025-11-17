from jinja2 import Environment, FileSystemLoader

async def load_template_text(template_name: str, templates_dir: str = './templates/', **kwargs) -> str:
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(f"{template_name}.j2")
    return template.render(**kwargs)