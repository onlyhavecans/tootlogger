# Toot to Dayone

Take all your toots and make a dayone journal entry.

This saves the last seen toot id so subsiquent runs will only show all the toots since then.
If you miss a day of running this it, it will backfill up to the pagination limit.

At some point I'll probably need to properly handle pagination but... :shrug:

## Setup

You will need to manually generate your access token

1. Log into your mastodon instance 
1. go to `/settings/applications` and create the new app.
    - Read Write and Post permissions are fine
1. Note down the `access_token`
1. Copy `config.toml.example` to `config.toml`
1. Fill out the `access_token` in the `config.toml`
1. Change the `instance` url if necessary


## Usage

1. `pipenv run python toot_to_dayone.py` to upload your toots