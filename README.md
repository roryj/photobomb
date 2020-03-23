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
python3 main.py --input-file ./test-image.jpg --effect swirl
```

### Face Identify Effect
```
python3 main.py --input-file ./test-image.jpg --effect identify-face
```

### Ghost Effect
```
python3 main.py --input-file ./test-image.jpg --effect ghost
```