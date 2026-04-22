"""
Pytest configuration for the cephadm unit test suite.
"""
import pytest


def _drain_patcher_refcount() -> None:
    """Work around pyfakefs' singleton Patcher leaving REF_COUNT > 0 (so the next
    Patcher().setUp() bails out before _refresh, leaving ``patcher.fs`` as
    None). This can happen after a crashed test, or when mixing
    :class:`pyfakefs.fake_filesystem_unittest.TestCase` with the ``fs`` fixture
    in the same session.
    """
    from pyfakefs.fake_filesystem_unittest import Patcher

    # Safety: avoid an infinite loop if the library changes.
    for _ in range(32):
        if Patcher.REF_COUNT <= 0 and Patcher.DOC_REF_COUNT <= 0:
            return
        p = Patcher.PATCHER
        if p is None and Patcher.REF_COUNT:
            Patcher.REF_COUNT = 0
            Patcher.DOC_REF_COUNT = 0
            return
        if p is not None:
            p.tearDown()


@pytest.fixture(scope='function', autouse=True)
def _pyfakefs_patcher_drain() -> None:
    _drain_patcher_refcount()
    yield
    _drain_patcher_refcount()
