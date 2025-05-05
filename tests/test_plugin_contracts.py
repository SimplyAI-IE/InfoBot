import importlib
import pkgutil

from backend.apps.base_app import BaseApp


def discover_app_modules(package):
    prefix = package.__name__ + "."
    return [
        importlib.import_module(name)
        for _, name, _ in pkgutil.iter_modules(package.__path__, prefix)
    ]


def test_all_extract_classes_implement_baseapp():
    import backend.apps

    app_modules = discover_app_modules(backend.apps)
    failures = []

    for module in app_modules:
        try:
            extract = importlib.import_module(f"{module.__name__}.extract")
            for name in dir(extract):
                attr = getattr(extract, name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BaseApp)
                    and attr is not BaseApp
                ):
                    missing = getattr(attr, "__abstractmethods__", set())
                    if missing:
                        failures.append(f"{attr.__name__} is missing: {missing}")
        except (ModuleNotFoundError, AttributeError):
            continue

    assert (
        not failures
    ), "Some extract classes are missing required methods:\\n" + "\\n".join(failures)
