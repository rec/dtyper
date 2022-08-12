from __future__ import annotations
from functools import wraps
from typing import TYPE_CHECKING
import inspect

try:
    from datacls import field, make_dataclass
except ImportError:
    from dataclasses import field, make_dataclass

if TYPE_CHECKING:
    from typing import Callable, Optional, Type, TypeVar, Union

    from typing_extensions import ParamSpec

    P = ParamSpec('P')
    R = TypeVar('R')

__version__ = '1.0.0'


@wraps(make_dataclass)
def dataclass(
    typer_command: Callable[P, R],
    base: Optional[Type] = None,
    **kwargs
) -> Callable[[Union[Type, Callable]], Type]:
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
    """Return function that can be called outside of a typer.Typer app context

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


def _fixed_signature(
    typer_command: Callable[P, R]
) -> inspect.Signature:
    """
    Return `inspect.Signature` with fixed default values for typer objects.
    """
    def fix_param(p):
        default = getattr(p.default, 'default', p.default)
        if default is ...:
            default = inspect.Parameter.empty
        return p.replace(default=default)

    sig = inspect.signature(typer_command)
    parameters = [fix_param(p) for p in sig.parameters.values()]
    return sig.replace(parameters=parameters)
