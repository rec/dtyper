⌨️dtyper: Call typer commands or make dataclasses from them ⌨️

Install using ``pip install dtyper``.

``dtyper.function`` takes a ``typer`` command and returns a callable function
with the correct defaults.

``dtyper.dataclass`` is a decorator that takes a ``typer`` command and makes a
dataclass from it, wrapping either a function or a callable class.

See ``test_dtyper.py`` for examples of use.
