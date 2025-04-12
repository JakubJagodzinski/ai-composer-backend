import io

from flask import Flask, send_file, request, render_template

from file_type import FileType
from files_utils import load_midi_from_disk, midi_to_bytes, midi_to_mp3

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate_music', methods=['POST'])
def generate_music():
    data = request.get_json()
    music_genre = data.get('music_genre')
    main_instrument = data.get('main_instrument')
    seconds = data.get('seconds')
    file_type = data.get('file_type')

    network_args = (music_genre, main_instrument, seconds)

    midi_file = load_midi_from_disk()  # Mock, replace with neural network call
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


if __name__ == '__main__':
    app.run()
