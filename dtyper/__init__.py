"""
# 🗝 Fix and improve `typer` 🗝

### What is `dtyper`, in one sentence?

Using `import dtyper as typer` instead of `import typer` would make your
`typer.command`s directly callable.

(There's also a neat way to make dataclasses from typer commands, but that
would be two sentences.)

### Why `dtyper`?

[`typer`](https://typer.tiangolo.com/) is a famously clear and useful system
for writing Python CLIs but it has two issues that people seem to run into a
lot:

1. You can't call the `typer.command` functions it creates directly because
they have the wrong defaults.

2. As you add more arguments to your CLI, there is no easy way to break up the
code sitting in one file without passing around long, verbose parameter lists.

`dtyper` is a tiny, single-file library that adds to an existing installation
of `typer` to solve these two problems without changing existing code at all.

* `dtyper.command` executes `typer.command` then fixes the defaults.

* `dtyper.function` decorates an existing `typer.command` to have correct
  defaults.

* `dtyper.dataclass` automatically makes a `dataclass` from
   a `typer.command`.

### How to use `dtyper`?

Install as usual with `poetry add dtyper`, `pip install dtyper`, or your
favorite package manager.

`dtyper` is a drop-in replacement for `typer` - it copies all `typer`s
properties - so you can even write

    import dtyper as typer

to experiment with it before deciding.

`dtyper` has two new functions that `typer` doesn't, and overrides a `typer`
class:

* `@dtyper.function` is a decorator that takes a `typer` command and returns
  a callable function with the correct defaults.  It is unncessary if you use
  `dtyper.Typer` (below)

* `@dtyper.dataclass` is a decorator that takes an existing `typer` or `dtyper`
command and makes a `dataclass` from it.

* `dtyper.Typer`is a class identical to `typer.Typer`, except it fixes
  `Typer.command` functions so you can call them directly.

None of the `typer` functionality is changed to the slightest degree - adding
`dtyper` will not affect how your command line program runs at all.

## Example 1: using `dtyper` instead of `typer`

    from dtyper import Argument, Option, Typer

    app = Typer()

    @app.command(help='test')
    def get_keys(
        bucket: str = Argument(
            'buck', help='The bucket to use'
        ),

        keys: bool = Option(
            False, help='The keys to download'
        ),
    ):
        print(bucket, keys)

You can call `get_keys()` from other code and get the right defaults.

Without regular `typer`, you sometimes get a `typer.Argument` or
`typer.Option` in place of an expected `str` or `bool`.

### Example 2: a simple `dtyper.dataclass`

Here's a simple CLI in one Python file with two `Argument`s and an `Option`:

    @command(help='test')
    def get_keys(
        bucket: str = Argument(
            ..., help='The bucket to use'
        ),

        keys: str = Argument(
            'keys', help='The keys to download'
        ),

        pid: Optional[int] = Option(
            None, '--pid', '-p', help='process id, or None for this process'
        ),
    ):
        get_keys = GetKeys(**locals())
        print(get_keys.run())


    @dtyper.dataclass(get_keys)
    class GetKeys:
        site = 'https://www.some-websijt.nl'

        def run(self):
            return self.url, self.keys, self.pid

        def __post_init__(self):
            self.pid = self.pid or os.getpid()

        def url(self):
           return f'{self.site}/{self.url}/{self.pid}'


### Example: splitting a large `typer.command` into multiple files

Real world CLIs frequently have dozens if not hundreds of commands, with
hundreds if not thousands of options, arguments, settings or command line
flags.

The natural structure for this is the "big ball of mud", a popular anti-pattern
known to cause misery and suffering to maintainers.

`dtyper.dataclass` can split the user-facing definition of the API from its
implementation and then split that implementation over multiple files in a
natural and convenient way.

The example has three Python files.

`interface.py` contains the Typer CLI definitions for this command.

    @command(help='test')
    def big_calc(
        bucket: str = Argument(
            ..., help='The bucket to use'
        ),
        more: str = Argument(
            '', help='More information'
        ),
        enable_something: boolean = Option(
            False, help='Turn on one of many important parameters'
        ),
        # [dozens of parameters here]
    ):
        d = dict(locals())  # Capture all the command line arguments as a dict

        from .big_calc import BigCalc  # Lazy import to avoid a cycle

        bc = BigCalc(**d)
        bc.run()


`big_calc.py` contains the `dtyper.dataclass` implementation

    from .interface import big_calc
    from . import helper
    import dtyper


    @dtyper.dataclass(big_calc)
    class BigCalc:
        def run(self):
           # Each argument in `big_calc` becomes a dataclass field
           print(self.bucket, self.more)
           print(self)  # dataclass gives you a nice output of all fields

           if helper.huge_thing(self) and self._etc():
              self.stuff()
              helper.more_stuff(self)
              ...

        def _etc(self):
           ...
           # Dozens more methods here perhaps!

Some of the code is offloaded to helper files like `helper.py`:

    def huge_thing(big_calc):
        if has_hole(big_calc.bucket):
           fix_it(big_calc.bucket, big_calc.more)

    def more_stuff(big_calc):
        # even more code
"""

from __future__ import annotations

import inspect
import typing as t
from dataclasses import field, make_dataclass
from functools import update_wrapper

import typer
from typer import (
    Abort,
    Argument,
    BadParameter,
    CallbackParam,
    Context,
    Exit,
    FileBinaryRead,
    FileBinaryWrite,
    FileText,
    FileTextWrite,
    Option,
    clear,
    colors,
    completion,
    confirm,
    core,
    echo,
    echo_via_pager,
    edit,
    format_filename,
    get_app_dir,
    get_binary_stream,
    get_terminal_size,
    get_text_stream,
    getchar,
    launch,
    main,
    models,
    open_file,
    params,
    pause,
    progressbar,
    prompt,
    run,
    secho,
    style,
    unstyle,
    utils,
)
from typer.core import TyperCommand
from typer.models import CommandFunctionType
from typing_extensions import ParamSpec

P = ParamSpec('P')
R = t.TypeVar('R')

Type = t.Type[t.Any]
Callable = t.Callable[..., t.Any]

__all__ = (
    'Abort',
    'Argument',
    'BadParameter',
    'CallbackParam',
    'Context',
    'Exit',
    'FileBinaryRead',
    'FileBinaryWrite',
    'FileText',
    'FileTextWrite',
    'Option',
    'Typer',
    'clear',
    'colors',
    'completion',
    'confirm',
    'core',
    'echo',
    'echo_via_pager',
    'edit',
    'format_filename',
    'get_app_dir',
    'get_binary_stream',
    'get_terminal_size',
    'get_text_stream',
    'getchar',
    'launch',
    'main',
    'models',
    'open_file',
    'params',
    'pause',
    'progressbar',
    'prompt',
    'run',
    'secho',
    'style',
    'unstyle',
    'utils',
    'dataclass',
    'make_dataclass_args',
    'function',
)


def dataclass(
    typer_command: t.Callable[P, R], **kwargs: t.Any
) -> t.Callable[[t.Union[Type, Callable]], Type]:
    """Automatically construct a dataclass from a typer command.

    One dataclass field is created for each parameter to the typer
    command, using typer default values obtained from
    typer.Argument and typer.Option, if they exist.
    """

    # The ._dtyper_dec logic handles the case where the decorator
    # is called twice on the same function.
    typer_command = getattr(typer_command, '_dtyper_dec', typer_command)

    def dataclass_maker(function_or_class: t.Union[Type, Callable]) -> Type:
        assert callable(function_or_class)

        ka = make_dataclass_args(typer_command, **kwargs)
        if isinstance(function_or_class, type):
            ka['bases'] = *ka.get('bases', ()), function_or_class
        else:
            ka['namespace']['__call__'] = function_or_class

        return make_dataclass(**ka)

    update_wrapper(dataclass_maker, typer_command)
    return dataclass_maker


update_wrapper(dataclass, make_dataclass)


def make_dataclass_args(
    typer_command: t.Callable[P, R], **kwargs: t.Any
) -> t.Dict[str, t.Any]:
    """Take a typer comamnd and return the arguments to be passed to
    dataclasses.make_dataclass to construct a dataclass whose elements correspond
    to the Arguments and Options to the typer command.
    """

    # The ._dtyper_dec logic handles the case where the decorator
    # is called twice on the same function.
    typer_command = getattr(typer_command, '_dtyper_dec', typer_command)

    def param_to_field_desc(p) -> t.Tuple[t.Any, ...]:  # type: ignore[no-untyped-def]
        if p.default is inspect.Parameter.empty:
            return p.name, p.annotation
        else:
            return p.name, p.annotation, field(default=p.default)

    params = _fixed_signature(typer_command).parameters.values()
    kwargs['fields'] = [param_to_field_desc(p) for p in params]
    kwargs.setdefault('cls_name', typer_command.__name__)
    kwargs.setdefault('namespace', {})['typer_command'] = staticmethod(typer_command)

    return kwargs


update_wrapper(make_dataclass_args, make_dataclass)


def function(typer_command: t.Callable[P, R]) -> t.Callable[P, R]:
    """
    Decorate a typer.command to be called outside of a typer.Typer app context.

    This allows a function with default argument values of instance
    `typer.Option` and `typer.Argument` to be called without having to provide
    all the defaults manually.
    """
    sig = _fixed_signature(typer_command)

    def wrapped(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        return typer_command(*bound.args, **bound.kwargs)

    update_wrapper(wrapped, typer_command)
    wrapped.__signature__ = sig  # type: ignore
    return wrapped


class Typer(typer.Typer):
    """Identical to typer.Typer, except with callable ``command()``.

    The ``command()`` decorator method wraps its functions with ``function``
    above so they can be called from regular Python code.
    """

    def command(
        self,
        name: t.Optional[str] = None,
        *,
        cls: t.Optional[t.Type[TyperCommand]] = None,
        context_settings: t.Optional[t.Dict[t.Any, t.Any]] = None,
        help: t.Optional[str] = None,
        epilog: t.Optional[str] = None,
        short_help: t.Optional[str] = None,
        options_metavar: str = '[OPTIONS]',
        add_help_option: bool = True,
        no_args_is_help: bool = False,
        hidden: bool = False,
        deprecated: bool = False,
        # Rich settings
        rich_help_panel: t.Union[str, None] = models.Default(None),
    ) -> t.Callable[[CommandFunctionType], CommandFunctionType]:
        decorator = super().command(
            name,
            cls=cls,
            context_settings=context_settings,
            help=help,
            epilog=epilog,
            short_help=short_help,
            options_metavar=options_metavar,
            add_help_option=add_help_option,
            no_args_is_help=no_args_is_help,
            hidden=hidden,
            deprecated=deprecated,
            rich_help_panel=rich_help_panel,
        )

        def wrapped(f: CommandFunctionType) -> CommandFunctionType:
            decorated = decorator(f)
            func = function(decorated)
            func._dtyper_dec = decorated  # type: ignore[attr-defined]
            return t.cast(CommandFunctionType, func)

        update_wrapper(wrapped, decorator)
        return wrapped


update_wrapper(Typer.command, typer.Typer.command)


def _fixed_signature(typer_command: t.Callable[P, R]) -> inspect.Signature:
    """
    Return `inspect.Signature` with fixed default values for typer objects.
    """
    sig = inspect.signature(typer_command)

    def fix_param(p: inspect.Parameter) -> inspect.Parameter:
        if isinstance(p.default, models.OptionInfo):
            kind: t.Any = p.KEYWORD_ONLY
        else:
            kind = p.kind

        default = getattr(p.default, 'default', p.default)
        if default is ...:
            default = inspect.Parameter.empty
        return p.replace(default=default, kind=kind)

    parameters = [fix_param(p) for p in sig.parameters.values()]
    return sig.replace(parameters=parameters)
