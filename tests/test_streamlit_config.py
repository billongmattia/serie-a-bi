import tomllib

from etl import config


def test_streamlit_listens_on_localhost_only():
    path = config.ROOT / ".streamlit" / "config.toml"
    settings = tomllib.loads(path.read_text(encoding="utf-8"))
    assert settings["server"]["address"] == "localhost"
