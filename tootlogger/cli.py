#!/usr/bin/env python3
"""
Save all your toots from Mastadon as a single journal entry in dayone
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import html2text
import toml
from jinja2 import Environment, select_autoescape, PackageLoader
from mastodon import Mastodon

APP_NAME = "tootlogger"
CONFIG_FILE = "tootlogger.toml"
DAYONE_CLI = "/usr/local/bin/dayone2"
DAYONE_COMMAND = "new"
LOCAL_TZ = datetime.now().tzinfo


def fatal(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)


def load_config():
    global CONFIG_FILE
    try:
        return toml.load(CONFIG_FILE)
    except FileNotFoundError as e:
        try:
            # We write back to the global so that we save to the right file
            CONFIG_FILE = os.path.join(Path.home(), f".{CONFIG_FILE}")
            return toml.load(CONFIG_FILE)
        except FileNotFoundError as e:
            fatal("You need to copy the main config file & add your settings")


def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        toml.dump(config, f)


def get_toots(api_base_url, access_token, last_id=None):
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url=api_base_url,
    )
    my_user_id = mastodon.account_verify_credentials()['id']
    return mastodon.account_statuses(my_user_id, since_id=last_id)


def parse_toots_to_journal(toots):
    cleaned_toot_data = {}
    for account, account_toots in toots.items():
        cleaned_toot_data[account] = map(toot_cleaner, account_toots)

    jinja_env = Environment(
        loader=PackageLoader(APP_NAME, "templates"),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = jinja_env.get_template('template.jinja2')
    return template.render(toot_data=cleaned_toot_data)


def toot_cleaner(toot):
    html_parser = html2text.HTML2Text(bodywidth=0)
    return {
        'created_at': toot['created_at'].astimezone(LOCAL_TZ),
        'content': html_parser.handle(toot['content'])
    }


def get_latest_post_id(toots):
    latest_toot = toots[0]
    return latest_toot['id']


def main():
    conf = load_config()
    if not os.path.isfile(DAYONE_CLI):
        fatal(f"DayOne cli {DAYONE_CLI} is not present. Please install")

    toots = {}
    for account, settings in conf.items():
        toots[account] = get_toots(
            settings['instance'],
            settings['access_token'],
            settings.get('last_id')
        )

    journal = parse_toots_to_journal(toots)
    subprocess.run(
        [DAYONE_CLI, DAYONE_COMMAND],
        input=journal,
        text=True,
        check=True,
    )

    for account, toot_list in toots.items():
        if toot_list:
            conf[account]['last_id'] = get_latest_post_id(toot_list)

    save_config(conf)


if __name__ == '__main__':
    main()
