<h1 align="center">My parser for Rocket League replays.</h1>

<p align="center">
	<img src="Rocket-League.png" style="width:67%" />
</p>

<p align="center">
<i>Rocket League</i> is a competitive video game based on soccer, except each
player controls a rocket-powered <b>car</b>.
</p>

## Usage

Clone the repository, download all dependencies (`boxcars`, `pandas`), and call
`main.py [PATH]`, specifying the path to the `.replay` file that you wish to
parse.

By default, the program will <b>NOT</b> save the data anywhere, so you will have
to tweak the `main.py` file to do anything with the data. Currently, it simply
prints out a condensed version (every 10 frames) of the `pandas.DataFrame` for
the general game.

## Background Information

Each <i>match</i> in Rocket League can be saved as a <i>replay</i> to be viewed
later. Each replay is characterised by the `.replay` file extension and contains
<b>frame-by-frame</b> data for every <i>actor</i> (an arbitrary name for game
objects, such as the cars, the ball, and even game metadata). Of course,
different types of actors will have different data associated with them, and
this project aims to retrieve and restructure said data for easy use (whether
for exploration or analysis).

Please note that this project started out as a fork of the parser for
[`carball`](https://github.com/SaltieRL/carball), but I quickly found that there
was a lot of dead code and an awkward implementation for handling the many
different actors (ie. not easily extensible). Therefore, I decided to rewrite it
from scratch, which served as great Python practice; and, in the end, my parser
was fully compatible with `carball`, while being slightly faster (at worst,
equally performant). However, the `carball` project was shutdown before I was
confident enough to suggest such a massive change...

## Project Breakdown

To begin with, the binary `.replay` file is parsed into `JSON` via
[`boxcars`](https://github.com/nickbabcock/boxcars), which was originally used
by the `carball` project (see above). The initial `JSON` output is a deeply
nested dictionary of actors and their data, which we wish to restructure in a
logical manner, described later on.

Then, the initial `Replay` object is constructed with some easily accessed
metadata such as the owner's name, the date, total goals, etc. These are stored
under one of the top-level dictionary keys, all of which can be printed with
`boxcars_replay.keys()`.

***

The subsequent parsing is dependent on `config.yml`, which primarily specifies
the actor types as <b>full class names</b> and whether they should be parsed
(otherwise ignored).

<details><summary><b>About actor class names:</b></summary>

> They are found by examining the values under the `objects` top-level key of
> the replay.

> They are specified in the configuration file to allow for easy access and
> modification, in case they change or an additional actor needs to be added.

</details>

***

The `ActorParser` class is then responsible for classifying actors by type,
retrieving data for each actor and ensuring that all actors remain consistent
with their objects. The latter is a crucial detail, since actors may be deleted
and replaced throughout the replay (eg. the ball is deleted and replaced on
every goal/kickoff).

<details><summary><b>About actor parsing:</b></summary>

> For each frame of the replay, I categorise actors by their <i>archetype</i>,
> which can be thought of as a superclass type for the actor types in
> `config.yml` (specifically, I use my custom short types, such as 'Car' and
> 'Ball', which are also reflected in `config.yml`).
>
> Then, for each category, I create an array of dictionaries that store the data
> associated with a given actor object; demonstrated:

```py
{...,
 251:
	{ # Archetypes:
	 'Car':
	   [ # Data per car actor:
		 {'actor_id': 10, 'throttle': 255, ...},
		 {'actor_id': 11, 'throttle': 0,   ...},
		 ...],
	 'Player':
	   [ # Data per player actor:
		 {'actor_id': 0, 'ping': 12, 'name': "Divvy C.",   ...},
		 {'actor_id': 1, 'ping': 19, 'name': "Ballchaser", ...}
		 ...],
	 ...},
 ...}
```

> The actor dictionaries are retrieved by archetype-specific parsers
> (`replay_parsing/actor_parsing/parse_[ARCHETYPE].py`).
>
> Each parser first uses `BaseParser` to retrieve some common data such as actor
> IDs, and then retrieves some data under a specific key such as `car_data` (in
> some cases, it's slightly more involved).

</details>

***

The `DataHandler` class is then responsible for combining actor data in a
logical manner, and subsequently populating the resultant replay objects (see
`replay_objects/replay_object.py`). This is meant to nicely yield the replay
data for analysis, as it will be grouped in a manner that reflects our
perception of the game (ie. a player is the same as their car, which in turn is
the same as the sum of its components). The `ActorParser` calls
`DataHandler.create_dataframes()` at the very end of the parsing process, which
creates
[`pandas.DataFrame`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)
objects for each replay object (this was used by `carball` for analysis).

The `DataFormatter` class just cleans-up the resultant `pandas.DataFrame`
objects. Currently, it only removes the name column for each player, while
recording all unique names directly to the player object.
