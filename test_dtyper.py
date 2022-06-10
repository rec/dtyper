import dtyper
from typer import Argument, Option, Typer
from typing import Optional
import pytest

command = Typer().command


@command(help='test')
def a_command(
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
    ACommand(**locals())()


@dtyper.dataclass(a_command)
class ACommand:
    def __post_init__(self):
        self.bucket += '-post'

    def __call__(self):
        return self.bucket, self.keys, self.pod

    @property
    def pod(self):
        return self.pid


@dtyper.dataclass(a_command)
def a_function(self):
    return self.bucket, self.keys, self.pid


class BCommand:
    post_init = False

    def __init__(self):
        assert False, 'The constructor is not called'

    def __post_init__(self):
        self.post_init = True

    def get(self):
        return self.bucket, self.keys, self.pid


@dtyper.dataclass(a_command, BCommand)
def b_function(self):
    assert self.post_init
    return self.get()


def test_dcommand():
    assert ACommand('bukket')() == ('bukket-post', 'keys', None)
    assert ACommand('bukket', 'kois', pid=3)() == ('bukket-post', 'kois', 3)

    match = 'missing 1 required positional argument: \'bucket\''
    with pytest.raises(TypeError, match=match):
        ACommand()


def test_afunction():
    assert a_function('bukket')() == ('bukket', 'keys', None)


def test_inheritance():
    assert b_function('bukket')() == ('bukket', 'keys', None)
