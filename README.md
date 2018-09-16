# toot_logger; Journal your toots to DayOne

Take all your toots and make a [DayOne](https://dayoneapp.com/) journal entry.

This saves the last seen toot id so subsequent runs will only show all the toots since then.
If you miss a day of running this it, it will backfill up to the pagination limit.

At some point I'll probably need to properly handle pagination but... :shrug:


## Install

1. Ensure you have at least Python 3.6 on your system
1. `pip install https://onlyhavecans.works/amy/mastodon_to_dayone/archive/master.tar.gz##egg=package-1.0`


## Setup

You will need to manually generate your access token and create a config file

1. Log into your mastodon instance 
1. go to `/settings/applications` and create the new app.
    - Read permissions are fine
1. Note down the `access_token`
1. Copy `toot_logger.toml.example` to `toot_logger.toml`
1. Fill out the `access_token` in the `toot_logger.toml`
1. Change the `instance` url if necessary


## Usage

1. Put your config in one of these places
    1. `$HOME/.toot_logger.toml`
    1. `toot_logger.toml` in the local directory you run the command from.
1. run `toot_logger` to log all of your toots to DayOne
