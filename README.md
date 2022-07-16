<h1 align="center">My parser for Rocket League replays.</h1>

<p align="center">
	<img src="Rocket-League.png" style="width:67%" />
</p>

<p align="center">
<i>Rocket League</i> is a competitive video game based on soccer, except each
player controls a rocket-powered <b>car</b>.
</p>

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

### Parsing

Then, the initial `Replay` object is constructed with some easily accessed
metadata such as the owner's name, the date, total goals, etc. These are stored
under one of the top-level dictionary keys, all of which can be printed with
`boxcars_replay.keys()`.

The subsequent parsing is dependent on `config.yml`, which primarily specifies
the actor types as <b>full class names</b> and whether they should be parsed
(otherwise ignored).

<details><summary><b>About actor class names:</b></summary>

> They are found by examining the values under the `objects` top-level key of
> the replay.

> They are specified in the configuration file to allow for easy access and
> modification, in case they change or an additional actor needs to be added.

</details>

The `ActorParser` class is then responsible for distinguishing actors by type
and ensuring that all actors correspond to the correct objects. The latter is
a crucial detail, since actors may be deleted and replaced throughout the
replay (eg. the ball is deleted and replaced on every goal/kickoff).

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

</details>

### ...
