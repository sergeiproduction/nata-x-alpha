import importlib.util
from pathlib import Path

def get_classes_from_directory(directory: str):
    classes = {}
    for file_path in Path(directory).rglob("*.py"):
        if file_path.name == "__init__.py":
            continue
        # Преобразуем путь в модуль
        module_name = ".".join(file_path.parts[:-1]) + "." + file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type):
                classes[attr_name] = attr
    return classes

def build_dispatcher_kwargs(repositories_path: str, services_path: str):
    repo_classes = get_classes_from_directory(repositories_path)
    service_classes = get_classes_from_directory(services_path)

    kwargs = {}

    for name, cls in repo_classes.items():
        # Пример: UserRepository -> user_repo
        key = to_snake_case(name.replace("Repository", "")) + "_repo"
        kwargs[key] = cls

    for name, cls in service_classes.items():
        # Пример: UserService -> user_service
        key = to_snake_case(name.replace("Service", "")) + "_service"
        kwargs[key] = cls

    return kwargs

def to_snake_case(name: str) -> str:
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()