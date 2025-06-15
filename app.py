import io

from flask import Flask, send_file, request
from flask_cors import CORS

import ai_module.generator
from diversity import Diversity
from file_type import FileType
from files_utils import midi_to_bytes, midi_to_mp3

app = Flask(__name__)

CORS(app, origins=["http://localhost:7666"], methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])


@app.route('/')
def home():
    return 'Welcome to AI Composer!'


instrument_codes = {
    'trumpet': 57,
    'piano': 1,
    'guitar': 28,
}


def get_instrument_code(instrument_name):
    return instrument_codes.get(instrument_name.lower(), 1)  # Default to piano if not found


def get_diversity_level(percentage: float) -> Diversity:
    if percentage < 33.0:
        return Diversity.LOW
    elif percentage < 66.0:
        return Diversity.MEDIUM
    else:
        return Diversity.HIGH


def percent_to_value(percent):
    min_val = 100
    max_val = 1000

    return max(min_val, (percent / 100.0) * max_val)


@app.route('/generate_music', methods=['POST'])
def generate_music():
    data = request.get_json()

    music_genre = data.get('music_genre').lower()
    main_instrument = get_instrument_code(data.get('main_instrument').lower())
    file_type = data.get('file_type').lower()
    sequences = percent_to_value(data.get('sequence_length_percentage'))
    diversity = get_diversity_level(data.get('diversity_percentage'))

    print(sequences)

    midi_file = ai_module.generator.generate(
        genre=music_genre,
        instrument=main_instrument,
        sequence_length=sequences,
        diversity=diversity
    )

    midi_bytes = midi_to_bytes(midi_file)

    if file_type == FileType.MP3:
        mp3_bytes = midi_to_mp3(midi_bytes, 'FluidR3_GM.sf2')
        mp3_buffer = io.BytesIO(mp3_bytes)
        mp3_buffer.seek(0)
        return send_file(mp3_buffer, mimetype='audio/mpeg', as_attachment=True, download_name='music.mp3')
    elif file_type == FileType.MIDI:
        midi_buffer = io.BytesIO(midi_bytes)
        midi_buffer.seek(0)
        return send_file(midi_buffer, mimetype='audio/midi', as_attachment=True, download_name='music.mid')
    elif file_type == FileType.WAV:
        mp3_bytes = midi_to_mp3(midi_bytes, 'FluidR3_GM.sf2', return_wav=True)
        mp3_buffer = io.BytesIO(mp3_bytes)
        mp3_buffer.seek(0)
        return send_file(mp3_buffer, mimetype='audio/mpeg', as_attachment=True, download_name='music.wav')


if __name__ == '__main__':
    app.run()
