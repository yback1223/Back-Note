import pytest
from core.api_retry_handler import APIRetryHandler


def test_call_with_retry_success_first_try(monkeypatch):
    calls = {"n": 0}

    def func():
        calls["n"] += 1
        return ("ok",)

    result = APIRetryHandler.call_with_retry(func, max_retries=3, retry_delay=0)
    assert result == ("ok",)
    assert calls["n"] == 1


def test_call_with_retry_retries_then_success(monkeypatch):
    calls = {"n": 0}

    def func():
        calls["n"] += 1
        if calls["n"] < 3:
            raise Exception("boom")
        return ("ok",)

    # Avoid actual sleeping
    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    result = APIRetryHandler.call_with_retry(func, max_retries=5, retry_delay=0)
    assert result == ("ok",)
    assert calls["n"] == 3


def test_call_with_retry_all_fail(monkeypatch):
    def func():
        raise Exception("boom")

    monkeypatch.setattr("time.sleep", lambda *_args, **_kwargs: None)

    with pytest.raises(Exception) as exc:
        APIRetryHandler.call_with_retry(func, max_retries=2, retry_delay=0)
    assert "Failed to process after 2 attempts" in str(exc.value)
