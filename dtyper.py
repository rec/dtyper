from argparse import Namespace
import dataclasses
import functools
import inspect


@functools.wraps(dataclasses.make_dataclass)
def dataclass(typer_f, base=None, **kwargs):
    required = True

    def field_desc(name, param):
        nonlocal required

        t = param.annotation or 'typing.Any'
        if param.default.default is not ...:
            required = False
            return name, t, dataclasses.field(default=param.default.default)

        if not required:
            raise ValueError('Required value after optional')

        return name, t

    kwargs.setdefault('cls_name', typer_f.__name__)
    if base is not None:
        kwargs['bases'] = *kwargs.get('bases', ()), base

    params = inspect.signature(typer_f).parameters
    kwargs['fields'] = [field_desc(k, v) for k, v in params.items()]

    @functools.wraps(typer_f)
    def dcommand_decorator(function_or_class):
        assert callable(function_or_class)

        ka = dict(kwargs)
        ns = Namespace(**(ka.pop('namespace', None) or {}))
        if isinstance(function_or_class, type):
            ka['bases'] = *ka.get('bases', ()), function_or_class
        else:
            ns.__call__ = function_or_class

        ka['namespace'] = vars(ns)
        return dataclasses.make_dataclass(**ka)

    return dcommand_decorator
