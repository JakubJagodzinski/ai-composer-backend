# AI Composer - Backend

This is a backend written in python Flask for AI composer app generating music using neural networks.

---

## Contents

- [Music generation](#music-generation)
- [Installing requirements](#installing-requirements)
- [Required files](#required-files)
- [Running the server](#running-the-server)
- [Contributors](#contributors)

---

## Music generation

POST `/generate_music` - returns generated music file

- music_genre (pop / rock / country / undefined)
- main_instrument (trumpet / piano / guitar)
- file_type (midi / wav / mp3)
- sequence_length_percentage (0-100) - percentage of the maximum sequence length
- diversity_percentage (0-100) - percentage of the diversity of the generated music

Sample request

```
{
    "music_genre": "classical",
    "main_instrument": "piano",
    "file_type": "mp3",
    "sequence_length_percentage": 60,
    "diversity_percentage": 50
}
```

---

## Installing requirements

```
pip install -r requirements.txt
```

---

## Required files

Download and extract files

- [Soundfont](https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip) - clicking on link will automatically download file

Download and extract files, then add to PATH

- [Ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-n7.1-latest-win64-gpl-7.1.zip) -
  clicking on link will automatically download file
- [Fluidsynth](https://github.com/FluidSynth/fluidsynth/releases/download/v2.4.3/fluidsynth-2.4.3-win10-x64.zip) -
  clicking on link will automatically download file

---

## Running the server

```
python app.py
```

Server runs by default on http://127.0.0.1:5000.

---

## Contributors

Contributors listed in alphabetical order:

- [BartlomiejJaruga](https://github.com/parsley026) - backend
- [erienx](https://github.com/erienx) - backend
- [JakubJagodzinski](https://github.com/JakubJagodzinski) - backend
- [masloorzech](https://github.com/masloorzech) - neural network
- [parsley026](https://github.com/parsley026) - neural network
