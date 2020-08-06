# BitMEX Async-Rest


[![PyPI](https://img.shields.io/pypi/v/bitmex_async_rest.svg)](https://pypi.python.org/pypi/bitmex-async-rest)
[![Build Status](https://img.shields.io/travis/com/andersea/bitmex-async-rest.svg)](https://travis-ci.com/andersea/bitmex-async-rest)

Async Rest API implementation for BitMEX cryptocurrency derivatives exchange.

* Free software: MIT license

## Features

* Supports authenticated connections using api keys.
* Based on asks and anyio. Should work on all anyio supported event loops.

## Non-features

* This is a beta api. Methods are probably named badly and a lot of stuff you might want is missing.

## Installation

This library requires Python 3.6 or greater. 

To install from PyPI:

    pip install bitmex-async-rest

## Client example

TODO

## API

Read the source code. (Welp..)

This library does not do retrys. If you get overload or similar errors, it is up to the client to handle them.

## Credits

Thanks to the [Trio](https://github.com/python-trio/trio), [Curio](https://github.com/dabeaz/curio), [AnyIO] (https://github.com/agronholm/anyio) and [asks](https://github.com/theelous3/asks) libraries for their awesome work.
