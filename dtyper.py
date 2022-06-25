from __future__ import annotations

import inspect
from dataclasses import field, make_dataclass
from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Optional, Type, TypeVar, Union

    from typing_extensions import ParamSpec

    P = ParamSpec("P")
    R = TypeVar("R")

__version__ = '0.9.0'


@wraps(make_dataclass)
def dataclass(
    typer_command: Callable[P, R], base: Optional[Type] = None, **kwargs
) -> Callable[[Union[Type, Callable]], Type]:

    if base is not None:
        kwargs['bases'] = *kwargs.get('bases', ()), base

    kwargs.setdefault('cls_name', typer_command.__name__)
    kwargs['fields'] = [
        (p.name, p.annotation)
        if p.default is inspect.Parameter.empty
        else (p.name, p.annotation, field(default=p.default))
        for p in _fixed_signature(typer_command).parameters.values()
    ]

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


def function(typer_command: Callable[P, R]) -> Callable[P, R]:
    """Return function that can be called outside of a typer.Typer app context

    This allows a function with default argument values of instance `typer.Option`
    and `typer.Argument` to be called without having to provide all the defaults
    manually.
    """

    new_sig = _fixed_signature(typer_command)

    @wraps(typer_command)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = new_sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return typer_command(*bound.args, **bound.kwargs)

    wrapped.__signature__ = new_sig  # type: ignore
    return wrapped


def _fixed_signature(typer_command: Callable[P, R]) -> inspect.Signature:
    """Return `inspect.Signature` with fixed default values for typer objects."""
    sig = inspect.signature(typer_command)

    fixed_parameters = []
    for param in sig.parameters.values():
        new_default = getattr(param.default, "default", param.default)
        if new_default is Ellipsis:
            new_default = inspect.Parameter.empty
        fixed_parameters.append(param.replace(default=new_default))

    return sig.replace(parameters=fixed_parameters)
