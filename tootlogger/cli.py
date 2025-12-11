#!/usr/bin/env python3
"""
Save all your toots from Mastodon as a single journal entry in DayOne
"""

import shutil
import subprocess
import sys
import tomllib
from datetime import datetime, tzinfo
from pathlib import Path
from typing import Any, NoReturn, NotRequired, TypedDict

import html2text
import tomli_w
from jinja2 import Environment, PackageLoader, select_autoescape
from mastodon import Mastodon
from mastodon.return_types import Status

APP_NAME: str = "tootlogger"
DEFAULT_CONFIG_FILE: str = "tootlogger.toml"
DAYONE_CLI: str = "dayone2"
DAYONE_COMMAND: str = "new"


def get_local_tz() -> tzinfo | None:
    """Get the local timezone at runtime rather than import time."""
    return datetime.now().tzinfo


class CleanedToot(TypedDict):
    created_at: datetime
    content: str


class AccountConfig(TypedDict):
    instance: str
    access_token: str
    last_id: NotRequired[int]


Config = dict[str, AccountConfig]


class ConfigResult(TypedDict):
    config: Config
    path: Path


def fatal(*args: object, **kwargs: Any) -> NoReturn:
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)


def load_config() -> ConfigResult:
    """Load config from local dir or home dir, returning config and its path."""
    local_path = Path(DEFAULT_CONFIG_FILE)
    home_path = Path.home() / f".{DEFAULT_CONFIG_FILE}"

    for path in (local_path, home_path):
        if path.exists():
            with open(path, "rb") as f:
                return {"config": tomllib.load(f), "path": path}

    fatal("You need to copy the main config file & add your settings")


def save_config(config: Config, path: Path) -> None:
    with open(path, "wb") as f:
        tomli_w.dump(config, f)


def get_toots(
    api_base_url: str, access_token: str, last_id: int | None = None
) -> list[Status]:
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url=api_base_url,
    )
    my_user_id = mastodon.account_verify_credentials()["id"]
    return list(mastodon.account_statuses(my_user_id, since_id=last_id))


def parse_toots_to_journal(toots: dict[str, list[Status]]) -> str:
    html_parser = html2text.HTML2Text(bodywidth=0)
    local_tz = get_local_tz()

    cleaned_toot_data: dict[str, list[CleanedToot]] = {
        account: [toot_cleaner(t, html_parser, local_tz) for t in account_toots]
        for account, account_toots in toots.items()
    }

    jinja_env = Environment(
        loader=PackageLoader(APP_NAME, "templates"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = jinja_env.get_template("template.jinja2")
    return template.render(toot_data=cleaned_toot_data)


def toot_cleaner(
    toot: Status, html_parser: html2text.HTML2Text, local_tz: tzinfo | None
) -> CleanedToot:
    return {
        "created_at": toot["created_at"].astimezone(local_tz),
        "content": html_parser.handle(toot["content"]),
    }


def get_latest_post_id(toots: list[Status]) -> int:
    latest_toot = toots[0]
    return latest_toot["id"]


def main() -> None:
    result = load_config()
    conf = result["config"]
    config_path = result["path"]

    cli = shutil.which(DAYONE_CLI)
    if not cli:
        fatal(f"DayOne cli {DAYONE_CLI} is not present. Please install")

    toots: dict[str, list[Status]] = {}
    for account, settings in conf.items():
        toots[account] = get_toots(
            settings["instance"], settings["access_token"], settings.get("last_id")
        )

    journal = parse_toots_to_journal(toots)
    subprocess.run(
        [cli, DAYONE_COMMAND],
        input=journal,
        text=True,
        check=True,
    )

    for account, toot_list in toots.items():
        if toot_list:
            conf[account]["last_id"] = get_latest_post_id(toot_list)

    save_config(conf, config_path)


if __name__ == "__main__":
    main()
