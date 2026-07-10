
# Valorant Stats Bot

A Discord bot made by faizy_bug that tracks and displays the previous match stats for registered players, pulling data via Riot Games API

## Features/Commands

- ' !lastmatch (discord name) ' -> shows the player's most recent match:
+ Win/Loss banner (green/red)
+ Kills / Deaths
+ Rank
+ Map
+ Result and MMR change

- ' /register ' -> opens a (sign-in) form where the user can connect their account by filling in their:

+ riot name
+ riot tag (without #)
+ region (eu/na)

## Tech Stack

- Python
- Discord.py library
- SQLite
- ".env" for storing API keys
- ".gitignore" to keep files private

## What I Learned

- Working with external APIs (parsing responses)
- Storing and querying user data in a database
- Managing secrets/private stuff safely with environment tools instead of hardcoding
- Building a interactive Discord UI (form / slash commands)

## Status

Done

