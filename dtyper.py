from __future__ import annotations
from functools import wraps
from typer import models
from typing import TYPE_CHECKING
import inspect
import typer

try:
    from datacls import field, make_dataclass
except ImportError:
    from dataclasses import field, make_dataclass

if TYPE_CHECKING:
    from typing import Callable, Optional, Type, TypeVar, Union

    from typing_extensions import ParamSpec

    P = ParamSpec('P')
    R = TypeVar('R')

__all__ = tuple(sorted(k for k in dir(typer) if not k.startswith('_')))
for _i in __all__:
    globals()[_i] = getattr(typer, _i)  # ! :-)

__all__ = __all__ + ('dataclass', 'function')


@wraps(make_dataclass)
def dataclass(
    typer_command: Callable[P, R],
    base: Optional[Type] = None,
    **kwargs
) -> Callable[[Union[Type, Callable]], Type]:
    """Automatically construct a dataclass from a typer command.

    One dataclass field is created for each parameter to the typer
    command, using the typer defaults.
    """
    typer_command = getattr(typer_command, '_dtyper_dec', typer_command)

    if base is not None:
        kwargs['bases'] = *kwargs.get('bases', ()), base

    def param_to_field_desc(p):
        if p.default is inspect.Parameter.empty:
            return p.name, p.annotation
        else:
            return p.name, p.annotation, field(default=p.default)

    params = _fixed_signature(typer_command).parameters.values()
    kwargs['fields'] = [param_to_field_desc(p) for p in params]
    kwargs.setdefault('cls_name', typer_command.__name__)

    @wraps(typer_command)
    def dataclass_maker(function_or_class: Union[Type, Callable]) -> Type:
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


def function(
    typer_command: Callable[P, R]
) -> Callable[P, R]:
    """
    Decorate a typer.command to be called outside of a typer.Typer app context.

    This allows a function with default argument values of instance
    `typer.Option` and `typer.Argument` to be called without having to provide
    all the defaults manually.
    """
    sig = _fixed_signature(typer_command)

    @wraps(typer_command)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return typer_command(*bound.args, **bound.kwargs)

    wrapped.__signature__ = sig  # type: ignore
    return wrapped


class Typer(typer.Typer):
    """Identical to typer.Typer, except with callable ``command()``.

    The ``command()`` decorator method wraps its functions with ``function``
    above so they can be called from regular Python code.
    """
    @wraps(typer.Typer.command)
    def command(self, *a, **ka):
        decorator = super().command(*a, **ka)

        @wraps(decorator)
        def wrapped(f):
            decorated = decorator(f)
            func = function(decorated)
            func._dtyper_dec = decorated
            return func

        return wrapped


def _fixed_signature(
    typer_command: Callable[P, R]
) -> inspect.Signature:
    """
    Return `inspect.Signature` with fixed default values for typer objects.
    """
    sig = inspect.signature(typer_command)

    def fix_param(p):
        if isinstance(p.default, models.OptionInfo):
            kind = p.KEYWORD_ONLY
        else:
            kind = p.kind

        default = getattr(p.default, 'default', p.default)
        if default is ...:
            default = inspect.Parameter.empty
        return p.replace(default=default, kind=kind)

    parameters = [fix_param(p) for p in sig.parameters.values()]
    return sig.replace(parameters=parameters)
