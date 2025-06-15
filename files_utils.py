import io
import os

from midi2audio import FluidSynth
from mido import MidiFile
from pydub import AudioSegment


def midi_to_bytes(midi: MidiFile) -> bytes:
    """Convert a MidiFile object to bytes."""
    midi_buffer = io.BytesIO()
    midi.save(file=midi_buffer)
    midi_buffer.seek(0)
    return midi_buffer.getvalue()


def midi_to_mp3(midi_bytes: bytes, soundfont_path: str, return_wav=False) -> bytes:
    """Convert MIDI bytes to MP3 bytes using FluidSynth and pydub."""

    # Save MIDI to temporary file
    with open('temp.mid', 'wb') as midi_file:
        midi_file.write(midi_bytes)

    # Convert MIDI to WAV using FluidSynth
    fs = FluidSynth(soundfont_path)
    fs.midi_to_audio('temp.mid', 'temp.wav')

    if return_wav:
        with open('temp.wav', 'rb') as wav_file:
            wav_bytes = wav_file.read()
        os.remove('temp.mid')
        return wav_bytes

    # Convert WAV to MP3 using pydub
    audio = AudioSegment.from_wav('temp.wav')
    mp3_io = io.BytesIO()
    audio.export(mp3_io, format='mp3')
    mp3_io.seek(0)

    # Remove temporary files
    os.remove('temp.mid')
    os.remove('temp.wav')

    return mp3_io.getvalue()


def load_midi_from_disk():
    """Mock function to load a MIDI file from disk."""
    return MidiFile('sample.mid')
