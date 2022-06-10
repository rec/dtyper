from dataclasses import make_dataclass, field
from functools import wraps
import inspect

__version__ = '0.9.0'


@wraps(make_dataclass)
def dataclass(typer_command, base=None, **kwargs):
    def to_field(k, v, default):
        return (k, v) if default is ... else (k, v, field(default=default))

    if base is not None:
        kwargs['bases'] = *kwargs.get('bases', ()), base

    kwargs.setdefault('cls_name', typer_command.__name__)
    kwargs['fields'] = [to_field(*i) for i in _params(typer_command)]

    @wraps(typer_command)
    def dataclass_maker(function_or_class):
        assert callable(function_or_class)

        ka = dict(kwargs)
        ns = ka.setdefault('namespace', {})
        ns['typer_command'] = staticmethod(typer_command)

        if isinstance(function_or_class, type):
            ka['bases'] = *ka.get('bases', ()), function_or_class
        else:
            ns['__call__'] = function_or_class

        return make_dataclass(**ka)

    return dataclass_maker


def function(typer_command):
    params = list(_params(typer_command))

    @wraps(typer_command)
    def wrapped(*args, **kwargs):
        tc = typer_command.__name__ + '()'

        if len(args) > len(params):
            lp = len(params)
            s = 's' * (lp != 1)
            la = len(args)
            raise TypeError(f'{tc} takes {lp} argument{s} but {la} were given')

        for name, _, default in params[len(args):]:
            value = kwargs.pop(name, default)
            if value is ...:
                raise TypeError(f'{tc} missing required parameter \'{name}\'')
            args = *args, value
        return typer_command(*args, **kwargs)

    return wrapped


def _params(typer_command):
    required = True
    params = inspect.signature(typer_command).parameters
    for name, param in params.items():
        t = param.annotation or 'typing.Any'
        default = param.default.default

        if default is not ...:
            required = False
        elif not required:
            raise ValueError('Required value after optional')

        yield name, t, default
