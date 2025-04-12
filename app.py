import io

from flask import Flask, send_file, request, render_template
from pydub import AudioSegment

app = Flask(__name__)


def generate_music_with_neural_network(args):
    filename = r"C:\Users\kubaj\Desktop\music.wav"
    audio = AudioSegment.from_wav(filename)
    mp3_file = io.BytesIO()
    audio.export(mp3_file, format="mp3")
    mp3_file.seek(0)
    return mp3_file


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/generate_music', methods=['POST'])
def generate_music():
    data = request.get_json()
    music_genre = data.get('music_genre')
    main_instrument = data.get('main_instrument')
    seconds = data.get('seconds')
    file_type = data.get('file_type')

    args = (music_genre, main_instrument, seconds, file_type)

    mp3_file = generate_music_with_neural_network(args)

    return send_file(mp3_file, mimetype='audio/mpeg', as_attachment=True, download_name='music.mp3')


if __name__ == '__main__':
    app.run()
