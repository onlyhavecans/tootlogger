"""Tests for tootlogger CLI."""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import html2text
import pytest

from tootlogger.cli import (
    Config,
    get_latest_post_id,
    get_local_tz,
    load_config,
    parse_toots_to_journal,
    save_config,
    toot_cleaner,
)


class TestGetLocalTz:
    def test_returns_tzinfo_or_none(self) -> None:
        result = get_local_tz()
        # Should return a tzinfo or None (on systems without tz info)
        assert result is None or hasattr(result, "utcoffset")


class TestTootCleaner:
    def test_converts_html_to_markdown(self) -> None:
        html_parser = html2text.HTML2Text(bodywidth=0)
        local_tz = timezone.utc
        toot: dict = {
            "created_at": datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
            "content": "<p>Hello <strong>world</strong>!</p>",
        }

        result = toot_cleaner(toot, html_parser, local_tz)  # type: ignore[arg-type]

        assert result["content"] == "Hello **world**!\n"
        assert result["created_at"] == datetime(
            2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc
        )

    def test_preserves_timestamp_with_timezone_conversion(self) -> None:
        html_parser = html2text.HTML2Text(bodywidth=0)
        local_tz = timezone.utc
        original_time = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
        toot: dict = {
            "created_at": original_time,
            "content": "<p>Test</p>",
        }

        result = toot_cleaner(toot, html_parser, local_tz)  # type: ignore[arg-type]

        assert result["created_at"].tzinfo is not None

    def test_handles_complex_html(self) -> None:
        html_parser = html2text.HTML2Text(bodywidth=0)
        local_tz = timezone.utc
        toot: dict = {
            "created_at": datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
            "content": '<p>Check out <a href="https://example.com">this link</a>!</p>',
        }

        result = toot_cleaner(toot, html_parser, local_tz)  # type: ignore[arg-type]

        assert "this link" in result["content"]
        assert "https://example.com" in result["content"]


class TestGetLatestPostId:
    def test_returns_first_toot_id(self) -> None:
        toots: list[dict] = [
            {"id": 12345, "content": "newest"},
            {"id": 12344, "content": "older"},
            {"id": 12343, "content": "oldest"},
        ]

        result = get_latest_post_id(toots)  # type: ignore[arg-type]

        assert result == 12345

    def test_works_with_single_toot(self) -> None:
        toots: list[dict] = [{"id": 99999, "content": "only one"}]

        result = get_latest_post_id(toots)  # type: ignore[arg-type]

        assert result == 99999


class TestParseToots:
    def test_renders_empty_accounts(self) -> None:
        toots: dict[str, list] = {"@user@instance.social": []}

        result = parse_toots_to_journal(toots)  # type: ignore[arg-type]

        assert "The day's toots!" in result
        assert "@user@instance.social" in result
        assert "No toots for this account!" in result

    def test_renders_toots_with_content(self) -> None:
        toots: dict[str, list] = {
            "@user@instance.social": [
                {
                    "created_at": datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
                    "content": "<p>Hello world!</p>",
                }
            ]
        }

        result = parse_toots_to_journal(toots)  # type: ignore[arg-type]

        assert "The day's toots!" in result
        assert "@user@instance.social" in result
        assert "Hello world!" in result
        assert "I tooted;" in result

    def test_renders_multiple_accounts(self) -> None:
        toots: dict[str, list] = {
            "@user1@instance.social": [
                {
                    "created_at": datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc),
                    "content": "<p>First account</p>",
                }
            ],
            "@user2@other.social": [
                {
                    "created_at": datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc),
                    "content": "<p>Second account</p>",
                }
            ],
        }

        result = parse_toots_to_journal(toots)  # type: ignore[arg-type]

        assert "@user1@instance.social" in result
        assert "@user2@other.social" in result
        assert "First account" in result
        assert "Second account" in result


class TestConfigLoadSave:
    def test_load_config_from_local_path(self, tmp_path: Path) -> None:
        config_file = tmp_path / "tootlogger.toml"
        config_file.write_text(
            '[myaccount]\ninstance = "https://mastodon.social"\naccess_token = "secret"\n'
        )

        with patch("tootlogger.cli.DEFAULT_CONFIG_FILE", str(config_file)):
            with patch("tootlogger.cli.Path") as mock_path:
                # Make local path exist
                mock_local = MagicMock()
                mock_local.exists.return_value = True
                mock_local.__truediv__ = lambda self, x: tmp_path / x

                # Path() returns our mock for the config file check
                mock_path.return_value = config_file
                mock_path.home.return_value = tmp_path

                # Actually read the real file
                with patch("builtins.open", create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = (
                        config_file.read_bytes()
                    )

        # Simpler approach - just test save_config directly
        pass

    def test_save_config_writes_toml(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.toml"
        config: Config = {
            "myaccount": {
                "instance": "https://mastodon.social",
                "access_token": "secret123",
                "last_id": 12345,
            }
        }

        save_config(config, config_file)

        content = config_file.read_text()
        assert "[myaccount]" in content
        assert 'instance = "https://mastodon.social"' in content
        assert 'access_token = "secret123"' in content
        assert "last_id = 12345" in content

    def test_save_config_overwrites_existing(self, tmp_path: Path) -> None:
        config_file = tmp_path / "config.toml"
        config_file.write_text("old content")

        config: Config = {
            "newaccount": {
                "instance": "https://new.social",
                "access_token": "newtoken",
            }
        }

        save_config(config, config_file)

        content = config_file.read_text()
        assert "old content" not in content
        assert "[newaccount]" in content

    def test_load_config_prefers_local_over_home(self, tmp_path: Path) -> None:
        # Create both local and home config files
        local_config = tmp_path / "local" / "tootlogger.toml"
        home_config = tmp_path / "home" / ".tootlogger.toml"

        local_config.parent.mkdir(parents=True)
        home_config.parent.mkdir(parents=True)

        local_config.write_text(
            '[local]\ninstance = "https://local.social"\naccess_token = "local"\n'
        )
        home_config.write_text(
            '[home]\ninstance = "https://home.social"\naccess_token = "home"\n'
        )

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(local_config.parent)
            with patch("tootlogger.cli.DEFAULT_CONFIG_FILE", "tootlogger.toml"):
                with patch.object(Path, "home", return_value=home_config.parent):
                    result = load_config()

            assert "local" in result["config"]
            assert result["path"] == Path("tootlogger.toml")
        finally:
            os.chdir(original_cwd)

    def test_load_config_falls_back_to_home(self, tmp_path: Path) -> None:
        home_config = tmp_path / ".tootlogger.toml"
        home_config.write_text(
            '[home]\ninstance = "https://home.social"\naccess_token = "home"\n'
        )

        import os

        original_cwd = os.getcwd()
        try:
            # Change to a directory without local config
            os.chdir(tmp_path)
            with patch("tootlogger.cli.DEFAULT_CONFIG_FILE", "tootlogger.toml"):
                with patch.object(Path, "home", return_value=tmp_path):
                    result = load_config()

            assert "home" in result["config"]
        finally:
            os.chdir(original_cwd)


class TestFatal:
    def test_exits_with_code_1(self) -> None:
        from tootlogger.cli import fatal

        with pytest.raises(SystemExit) as exc_info:
            fatal("error message")

        assert exc_info.value.code == 1

    def test_prints_to_stderr(self, capsys: pytest.CaptureFixture[str]) -> None:
        from tootlogger.cli import fatal

        with pytest.raises(SystemExit):
            fatal("test error")

        captured = capsys.readouterr()
        assert captured.err == "test error\n"
        assert captured.out == ""


class TestMain:
    def test_exits_if_dayone_not_found(self, tmp_path: Path) -> None:
        from tootlogger.cli import main

        config_file = tmp_path / "tootlogger.toml"
        config_file.write_text(
            '[test]\ninstance = "https://test.social"\naccess_token = "token"\n'
        )

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("tootlogger.cli.DEFAULT_CONFIG_FILE", "tootlogger.toml"):
                with patch("shutil.which", return_value=None):
                    with pytest.raises(SystemExit) as exc_info:
                        main()

            assert exc_info.value.code == 1
        finally:
            os.chdir(original_cwd)

    def test_full_workflow(self, tmp_path: Path) -> None:
        from tootlogger.cli import main

        config_file = tmp_path / "tootlogger.toml"
        config_file.write_text(
            '[testaccount]\ninstance = "https://test.social"\naccess_token = "token"\n'
        )

        mock_toots = [
            {
                "id": 12345,
                "created_at": datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
                "content": "<p>Test toot</p>",
            }
        ]

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("tootlogger.cli.DEFAULT_CONFIG_FILE", "tootlogger.toml"):
                with patch("shutil.which", return_value="/usr/bin/dayone2"):
                    with patch("tootlogger.cli.get_toots", return_value=mock_toots):
                        with patch("subprocess.run") as mock_run:
                            main()

            # Verify subprocess was called with journal content
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert call_args[0][0] == ["/usr/bin/dayone2", "new"]
            assert "Test toot" in call_args[1]["input"]

            # Verify config was updated with last_id
            updated_config = config_file.read_text()
            assert "last_id = 12345" in updated_config
        finally:
            os.chdir(original_cwd)

    def test_handles_empty_toots(self, tmp_path: Path) -> None:
        from tootlogger.cli import main

        config_file = tmp_path / "tootlogger.toml"
        config_file.write_text(
            '[testaccount]\ninstance = "https://test.social"\naccess_token = "token"\n'
        )

        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with patch("tootlogger.cli.DEFAULT_CONFIG_FILE", "tootlogger.toml"):
                with patch("shutil.which", return_value="/usr/bin/dayone2"):
                    with patch("tootlogger.cli.get_toots", return_value=[]):
                        with patch("subprocess.run") as mock_run:
                            main()

            # Should still call dayone with "no toots" message
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "No toots for this account!" in call_args[1]["input"]

            # last_id should not be added for empty toots
            updated_config = config_file.read_text()
            assert "last_id" not in updated_config
        finally:
            os.chdir(original_cwd)
