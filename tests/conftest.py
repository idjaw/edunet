import logging

import pytest


@pytest.fixture(autouse=True)
def set_caplog_level(caplog):
    caplog.set_level(logging.DEBUG)
