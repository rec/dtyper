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


### [API Documentation](https://rec.github.io/dtyper#dtyper--api-documentation)
