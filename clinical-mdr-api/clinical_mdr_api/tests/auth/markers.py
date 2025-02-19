import pytest

from common.auth import config

if_oauth_enabled = pytest.mark.skipif(
    not config.OAUTH_ENABLED, reason="Authentication is disabled"
)
