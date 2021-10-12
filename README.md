# photobooth

The photobooth app has a bunch of different effects tailored to spookify some photos!

## Requirements

* [brew](https://brew.sh/)
* cmake
  * `brew install cmake`
* [Install dlib for MacOS with pytho3 extensions](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)
* python3
* [pipenv](https://pypi.org/project/pipenv/)

## Initial Setup

```shell
pipenv install --python python3
```

## Commands

### photobomb.py

This script is used to test individual effects, as well as different combinations of effects.

#### Swirl Effect

```shell
pipenv run python photobomb.py --input-file ./resources/input/test-image.jpg --effects swirl
```

#### Face Identify Effect

```shell
pipenv run python photobomb.py --input-file ./resources/input/test-image.jpg --effects identify-face
```

#### Ghost Effect

```shell
pipenv run python3 photobomb.py --input-file ./resources/input/test-image.jpg --effects ghost
```

#### Running multiple effects

`photobooth` now has support for running multiple effects on top of each other! You can do this by putting a list of filters after the `--effects` flag. These effects are run in the order the are written. For example:

```shell
pipenv run python3 photobomb.py --input-file ./resources/input/test-image.jpg --effects identify-face swirl ghost
```

### photobooth.py

This script is used to test out the photobooth workflow

```shell
python3 photobooth.py --input-files ./resources/input/test-image.jpg ./resources/input/test-image.jpg --border-size 5 --output-file photo_booth_result.png
```

### photobooth_server.py

This is runs the server that listens for key presses, to start the photobooth workflow

```shell
python3 photobooth_server.py
```
