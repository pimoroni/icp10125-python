import sys
import mock
import pytest


@pytest.fixture(scope='function', autouse=False)
def smbus2():
    """Mock smbus module."""
    sys.modules['smbus2'] = mock.MagicMock()
    yield sys.modules['smbus2']
    del sys.modules['smbus2']


@pytest.fixture(scope='function', autouse=False)
def icp10125():
    """Import icp10125 module."""
    import icp10125
    yield icp10125
    del sys.modules['icp10125']
