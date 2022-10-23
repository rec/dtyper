# ⌨️dtyper: Call `typer` commands, or make a `dataclass` from them  ⌨️

`typer` is a famously easy and useful system for writing Python CLIs but it has
two issues.

You cannot quite call the `typer.command` functions it creates directly.

And as you add more and more functionality into your CLI, there is no obvious
way to break up the code sitting in one file.

`dtyper` solves these two defects, calling `typer.command` functions
with the right defaults, and constructing a `dataclass` from a `typer.command`.

-----------------------------------------------

`dtyper` is a drop-in replacement for `typer`, so you can even write

    import dtyper as typer

if you like!

 It overrides one member from `typer`, and adds two new ones:

* `dtyper.Typer`is a class identical to `typer.Typer`, except it fixes
  `Typer.command` functions so you can call them directly (with the right
  defaults).

* `@dtyper.dataclass` is a decorator that takes an existing `typer` command
  and makes a `dataclass` from it.

* `@dtyper.function` is a decorator that takes a new `typer` command and returns
  a callable function with the correct defaults.  It is unncessary if you use
  `dtyper.Typer`.

## Installation

    pip install dtyper

## Examples

### Example: a simple `dtyper.dataclass`

Here's a simple CLI in one Python file with two arguments `bucket`, `keys` and
one option `pid`:

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
        print(get_keys())

    @dtyper.dataclass(get_keys)
    class GetKeys:
        site = 'https://www.some-websijt.nl'

        def __call__(self):
            return self.url, self.keys, self.pid

        def __post_init(self):
            self.pid = self.pid or os.getpid()

        def url(self):
           return f'{self.site}/{self.url}/{self.pid}'


### Example: putting the `dtyper.dataclass` into a separate file

In real world CLIs, there are frequently dozen of commands, each with dozens
of options or arguments.

To avoid the "big bowl of mud" anti-pattern, you often want to split off the
user-dash facing definition of the API from its implementation, and in large
programs, you might well want to split the implementation itself into multiple
files.

This example has three Python files.

`interface.py` contains the CLI API for this command.

The `big_calc` module is lazy loaded in interface.py - only loaded when this
command is actually called.

Lazy loading is extremely useful in large projects, because it means you don't
load the entire universe that any command _might_ want just to execute one tiny
command that has no dependencies, and it is necessary in this case to avoid
circular dependencies.

    # In interface.py

    @command(help='test')
    def big_calc(
        bucket: str = Argument(
            ..., help='The bucket to use'
        ),
        # dozens of parameters here
    ):
        d = dict(locals())

        from .big_calc import BigCalc

        return BigCalc(**d)()


Here's the actual dataclass, which knows about everything.


    # In big_calc.py

    from .interface import big_calc
    from . import helper
    from dtyper import dataclass

    @dataclass(big_calc)
    class BigCalc:
        def __call__(self):
           if helper.huge_thing(self) and self.etc():
              self.stuff()
              helper.more_stuff(self)

           # Dozens of methods here



    # In helper.py

    def huge_thing(big_calc):
        # Lots of code

    def more_stuff(big_calc):
