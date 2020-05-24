import random
import string

import pytest


@pytest.fixture
def make_random_str():
    def _make_random_str(length=16, digits=False):
        letters = string.digits if digits else string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    return _make_random_str
