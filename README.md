# league-of-legends-champion-randomizer

I play too much League and can never decide who to play when queuing with friends. This is a quick CLI tool I wrote to pick champions for me. It pulls live data directly from Riot's Data Dragon API, caches it locally so it runs instantly, and lets me filter the pool by role, tag, or difficulty.

## Installation

Clone the repository and install the dependencies:

```cmd
pip install -r requirements.txt
```

## How to use

By default, running it with no arguments picks one random champion from the entire pool:

```cmd
python randomizer.py
```

To restrict the selection to a specific role, tag, or difficulty level:

```cmd
python randomizer.py --role jungle --tag Assassin --max-diff 5
```

You can also pick multiple options if you want a pool of choices for a draft:

```cmd
python randomizer.py --role mid --count 3
```

To force-refresh the cached champion data from Riot's servers:

```cmd
python randomizer.py --refresh
```

<!-- updated: 2026-09-16 -->
