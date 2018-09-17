# tootlogger

## Journal your toots to DayOne

Take all your toots and make a [DayOne](https://dayoneapp.com/) journal entry.

This saves the last seen toot id so subsequent runs will only show all the toots since then.
If you miss a day of running this it, it will backfill up to the pagination limit.

## Install

1. Ensure you have at least Python 3.6 on your mac
    - [homebrew](https://brew.sh/) makes this easy with `brew install python`
1. Install the [DayOne Command Line Interface](http://help.dayoneapp.com/tips-and-tutorials/command-line-interface-cli)
1. Install tootlogger with `pip3 install tootlogger`


## Setup

You will need to manually generate your access token and create a config file

1. Log into your mastodon instance 
1. go to `/settings/applications` and create the new app.
    - Read permissions are fine
1. Note down the `access_token`
1. Create a config file like the example below (or in this repo) in one of two places
    1. `$HOME/.tootlogger.toml`
    1. `tootlogger.toml` in the local directory you run the command from.


### Config file
```toml
instance = "https://mastodon.social"
access_token = "really big string"
```

## Usage

1. run `tootlogger` to log all of your toots to DayOne
