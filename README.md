# photobooth

The photobooth app has a bunch of different effects tailored to spookify some photos!

## Requirements
* [brew](https://brew.sh/)
* cmake
  * `brew install cmake`
* [Install dlib for MacOS with pytho3 extensions](https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf)
* python3

## Initial Setup
```
pip3 install -r requirements.txt
```

## Commands
### Swirl Effect
```
python3 main.py --input-file ./test-image.jpg --effects swirl
```

### Face Identify Effect
```
python3 main.py --input-file ./test-image.jpg --effects identify-face
```

### Ghost Effect
```
python3 main.py --input-file ./test-image.jpg --effects ghost
```

### Running multiple effects
`photobooth` now has support for running multiple effects on top of each other! You can do this by putting a list of filters after the `--effects` flag. These effects are run in the order the are written. For example:

```
python3 main.py --input-file ./test-image.jpg --effects identify-face swirl ghost
```