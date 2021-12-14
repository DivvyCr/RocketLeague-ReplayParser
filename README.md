# My Parser for Rocket League replays.

The video game 'Rocket League' has a feature to save match replays. 
Each replay is stored in a `.replay` file, which contains frame-by-frame 
data for every 'actor' (eg. position, velocity). This project's goal is
to retrieve this data and provide it in an easy-to-use manner for exploration
or other uses.

Note that this is based on `carball`'s parser, as I initially was looking
for Python practice. However, on investigation, I found that there are many
ways to improve `carball`'s parser, in terms of maintainability, extensibility,
and readability. I have not extensively benchmarked my parser.

## The Fundamentals

The `.replay` files are initially binaries (I believe) that need to be decoded. 
I am not familiar with the process, yet, so my parser is reliant on `boxcars`,
which does exactly that.

By itself, the output of `boxcars` is not useable. The provided data is a lot of
nested dictionaries and arrays that can be identified by a variety of IDs, relating
to the object type and the object instance; these are not necessarily constant 
throughout the replay. Furthermore, the data relating to each object is structured
in a complex manner. (And there are many more intricacies here).

This is where this parser comes in.
