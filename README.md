# ⌨️dtyper: Call `typer` commands, or make a `dataclass` from them  ⌨️

`typer` is a famously easy and useful system for writing Python CLIs but it has
two issues.

You cannot quite call the functions it creates directly.

And as you add more and more functionality into your CLI, there is no obvious
way to break up the code sitting in one file.

 -----------------------------------------------

`dtyper` is a drop-in replacement for `typer`, so you can write:

    import dtyper as typer

It adds just two members, and overrides a third:

* `dtyper.dataclass` is a decorator that takes an existing `typer` command
  and makes a dataclass from it.

* `dtyper.function` is a decorator that takes a new `typer` command and returns
  a callable function with the correct defaults.

* `dtyper.Typer`is identical to typer.Typer, except that the `command()`
   decorator method wraps its functions with `dtyper.function`
   above so they can be called from regular Python code.  You can think of it as
   as a fix to a bug in `typer.Typer.command`, if you like. :-)

`dtyper.function` filled a need several people had mentioned online, but I
think developing with `dtyper.dataclass` is the way to go, particularly if you
expect the code to grow medium-sized or beyond.

## Installation

    pip install dtyper

## Examples

### `dtyper.dataclass`: simple

    @command(help='test')
    def get_keys(
        bucket: str = Argument(
            ..., help='The bucket to use'
        ),

        keys: str = Argument(
            'keys', help='The keys to download'
        ),

        pid: Optional[int] = Option(
            None, help='pid'
        ),
    ):
        return GetKeys(**locals())()

    @dtyper.dataclass(get_keys)
    class GetKeys:
        site = 'https://www.some-websijt.nl'

        def __post_init(self):
            self.pid = self.pid or os.getpid()

        def __call__(self):
            return self.url, self.keys, self.pid

        def url(self):
           return f'{self.site}/{self.url}/{self.pid}'


### `dtyper.dataclass`: A pattern for larger CLIs

    # In interface.py

    @command(help='test')
    def compute_everything(
        bucket: str = Argument(
            ..., help='The bucket to use'
        ),
        # dozens of parameters here
    ):
        d = dict(locals())

        from .compute import ComputeEverything

        return ComputeEverything(**d)()

    # In compute.py

    from .interface import compute_everything

    @dtyper.dataclass(compute_everything)
    class ComputeEverything:
        def __call__(self):
           if self.huge_thing() and self.etc():
              self.more_stuff()

           # Dozens of methods here
