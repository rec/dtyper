import dtyper
from typer import Argument, Option, Typer
from typing import Optional
import pytest

command = Typer().command
dcommand = dtyper.Typer().command


@dtyper.function
@command(help='test')
def simple_command(
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
    return bucket, keys, pid


def test_simple_command():
    assert simple_command('bukket', pid=3) == ('bukket', 'keys', 3)


@dcommand(help='test')
def simple_command2(
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
    return bucket, keys, pid


def test_simple_command2():
    assert simple_command2('bukket', pid=3) == ('bukket', 'keys', 3)


def test_args():
    with pytest.raises(TypeError, match="unexpected keyword argument 'frog'"):
        simple_command('bukket', frog=30)

    with pytest.raises(TypeError, match='too many positional arguments'):
        simple_command('bukket', 'key', 12, 30)

    with pytest.raises(TypeError, match="required argument: 'bucket'"):
        simple_command()


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
    return ACommand(**locals())()


@dtyper.dataclass(a_command)
class ACommand:
    def __post_init__(self):
        self.bucket += '-post'

    def __call__(self):
        return self.bucket, self.keys, self.pod

    @property
    def pod(self):
        return self.pid


def test_acommand():
    assert ACommand('bukket')() == ('bukket-post', 'keys', None)
    assert ACommand('bukket', 'kois', pid=3)() == ('bukket-post', 'kois', 3)

    match = 'missing 1 required positional argument: \'bucket\''
    with pytest.raises(TypeError, match=match):
        ACommand()


@dtyper.dataclass(a_command)
def c_function(self):
    return self.bucket, self.keys, self.pid


def test_c_function():
    assert c_function('bukket')() == ('bukket', 'keys', None)


@dtyper.dataclass(simple_command2)
def simple_class(sc):
    return sc, True


def test_simple_class():
    cls = simple_class(bucket='b', keys=['key'])
    assert cls() == (cls, True)


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


def test_inheritance():
    assert b_function('bukket')() == ('bukket', 'keys', None)


def test_aliases():
    from dtyper import Argument, Option
    assert Argument is globals()['Argument']
    assert Option is globals()['Option']


@dtyper.function
@command(help='test')
def less_simple_command(
    bucket: str = Argument(
        ..., help='The bucket to use'
    ),

    keys: str = Argument(
        'keys', help='The keys to download'
    ),

    pid: Optional[int] = Option(
        None, help='pid'
    ),

    pod: Optional[int] = Option(
        ..., help='pid'
    ),
):
    return bucket, keys, pid, pod


def test_less_simple_command():
    actual = less_simple_command('bukket', pid=3, pod=2)
    expected = 'bukket', 'keys', 3, 2
    assert actual == expected


def test_less_simple_command_error():
    with pytest.raises(TypeError):
        less_simple_command('bukket', pid=3)


@dtyper.function
@command(help='test')
def required_option_without_default_command(
    bucket: str = Argument(..., help='The bucket to use'),
    keys: str = Argument('keys', help='The keys to download'),
    pid: Optional[int] = Option(..., help='pid'),
    verbose: Optional[int] = Option(
        True,
    ),
):
    return bucket, keys, pid, verbose


def test_required_option_without_default():
    # TODO Test for Arguements and Options in the right sections of help
