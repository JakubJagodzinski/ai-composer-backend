# AI Composer - Backend

This is a simple Flask backend for AI composer app generating music using neural networks.

## Contents
- [Features](#features)
- [Endpoints](#endpoints)
- [Installing requirements](#installing-requirements)
- [Running the server](#running-the-server)
- [Contributors](#contributors)

## Endpoints
POST `/generate_music` - returns midi or mp3 file
- music_genre (e.g. jazz, classical, rock)
- main_instrument (e.g. piano, guitar, drums)
- seconds (length in seconds)
- file_type (mp3 or midi)

Sample request
```
{
    "music_genre": "classical",
    "main_instrument": "piano",
    "seconds": 120,
    "file_type": "mp3"
}
```
## Installing requirements
```
pip install -r requirements.txt
```

## Running the server
```
python app.py
```
Server runs by default on http://127.0.0.1:5000.

## Contributors (alphabetical order)
- [erienx](https://github.com/erienx) - endpoint
- [JakubJagodzinski](https://github.com/JakubJagodzinski) - endpoint
- [masloorzech](https://github.com/masloorzech) - neural network
- [parsley026](https://github.com/parsley026) - neural network
