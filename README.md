# AI Composer - Backend

This is a backend written in python Flask for AI composer app generating music using neural networks.

## Contents
- [Endpoints](#endpoints)
- [Installing requirements](#installing-requirements)
- [Required files](#required-files)
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

## Required files
Download and extract files, then add to PATH
- [Soundfont](https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip) - clicking on link will automatically download file
- [Ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-latest-win64-gpl-7.1.zip) - clicking on link will automatically download file

## Running the server
```
python app.py
```
Server runs by default on http://127.0.0.1:5000.

## Contributors
Contributors listed in alphabetical order:
- [BartlomiejJaruga](https://github.com/parsley026) - endpoints
- [erienx](https://github.com/erienx) - endpoints
- [JakubJagodzinski](https://github.com/JakubJagodzinski) - endpoints
- [masloorzech](https://github.com/masloorzech) - neural network
- [parsley026](https://github.com/parsley026) - neural network
