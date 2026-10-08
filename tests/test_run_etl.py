import logging

from etl import run_etl


def test_main_logs_an_unhandled_error_and_returns_1(monkeypatch, caplog):
    monkeypatch.setattr(run_etl, "setup_logging", lambda: None)

    def boom():
        raise RuntimeError("download esploso")

    monkeypatch.setattr(run_etl, "extract_all", boom)
    with caplog.at_level(logging.ERROR, logger="etl"):
        assert run_etl.main() == 1
    assert "download esploso" in caplog.text


def test_main_returns_1_when_no_csv_is_available(monkeypatch):
    monkeypatch.setattr(run_etl, "setup_logging", lambda: None)
    monkeypatch.setattr(run_etl, "extract_all", lambda: ({}, {2016: "errore di rete"}))
    assert run_etl.main() == 1
