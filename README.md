<h1 align="center">My parser for Rocket League replays.</h1>

<i>Rocket League</i> is a competitive video game based on football (soccer),
except each player controls a rocket-powered <b>car</b>:

<p align="center">
	<img src="Rocket-League.png" style="width:50%" />
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

## The Fundamentals

The `.replay` files are initially binaries (I believe) that need to be decoded.
I am not familiar with the process, yet, so my parser is reliant on `boxcars`,
which does exactly that.

By itself, the output of `boxcars` is not useable. The provided data is a lot of
nested dictionaries and arrays that can be identified by a variety of IDs,
relating to the object type and the object instance; these are not necessarily
constant throughout the replay. Furthermore, the data relating to each object is
structured in a complex manner. (And there are many more intricacies here).

This is where this parser comes in.
