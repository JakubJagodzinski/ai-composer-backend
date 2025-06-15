import os

import mido
import numpy as np


def generate_genre_vector(genre):
    genre = genre.strip().lower()
    genre_dict = {
        'pop': [1, 0, 0],
        'rock': [0, 1, 0],
        'country': [0, 0, 1],
    }
    return genre_dict.get(genre, [0, 0, 0])


def generate_event_vector(event):
    event = event.strip().lower()
    event_dict = {
        'note_on': [1, 0, 0, 0],
        'note_off': [0, 1, 0, 0],

        'control_change': [0, 0, 1, 0],
        'program_change': [0, 0, 0, 1],
    }
    return event_dict.get(event, [0, 0, 0, 0])


def normalize_value_float(value, max_value):
    return float(value / max_value)


def denormalize_value_int(value, max_value):
    return int(value * max_value)


max_event_fields_values = {
    'channel': 15,
    'note': 127,
    'velocity': 127,
    'program': 127,
    'control': 127,
    'value': 127,
    'time': 65536
}


def generate_event_fields_vector_float(midi_file, genre):
    data = []
    genre_vector = generate_genre_vector(genre)
    event_dict = ['note_on', 'note_off', 'control_change', 'program_change']

    for track in midi_file.tracks:
        for msg in track:

            if msg.type not in event_dict:
                continue

            event_vector = generate_event_vector(msg.type)

            channel = min(max(getattr(msg, 'channel', 0.0), 0), max_event_fields_values['channel'])
            note = min(max(getattr(msg, 'note', 0.0), 0), max_event_fields_values['note'])
            velocity = min(max(getattr(msg, 'velocity', 0.0), 0), max_event_fields_values['velocity'])
            control = min(max(getattr(msg, 'control', 0.0), 0), max_event_fields_values['control'])
            value = min(max(getattr(msg, 'value', 0.0), 0), max_event_fields_values['value'])
            program = min(max(getattr(msg, 'program', 0.0), 0), max_event_fields_values['program'])
            time = min(max(getattr(msg, 'time', 0.0), 0), max_event_fields_values['time'])

            channel = normalize_value_float(channel, max_event_fields_values['channel'])
            note = normalize_value_float(note, max_event_fields_values['note'])
            velocity = normalize_value_float(velocity, max_event_fields_values['velocity'])
            control = normalize_value_float(control, max_event_fields_values['control'])
            value = normalize_value_float(value, max_event_fields_values['value'])
            program = normalize_value_float(program, max_event_fields_values['program'])
            time = normalize_value_float(time, max_event_fields_values['time'])

            vector = genre_vector + event_vector + [channel, note, velocity, control, value, program, time]
            data.append(vector)

    return np.array(data)


def prepare_sequences_multi_output(data, sequence_length):
    X = []

    y1 = []
    y2 = []

    for i in range(len(data) - sequence_length):
        sequence_in = data[i:i + sequence_length]
        sequence_out = data[i + sequence_length]

        X.append(sequence_in)

        y1.append(sequence_out[3:7])
        y2.append(sequence_out[7:])

    return np.array(X), np.array(y1), np.array(y2)


def generate_event_fields_vectors_float(labels_df, midi_files_dir, sequence_length=25, save_path=None):
    data = []

    for _, row in labels_df.iterrows():
        filename = row['filename']
        genre = row['genre']
        filepath = os.path.join(midi_files_dir, filename)

        if os.path.exists(filepath):
            try:
                midi = mido.MidiFile(filepath)
                track_data = generate_event_fields_vector_float(midi, genre)
                data.extend(track_data)
            except Exception as e:
                print(f"skipping '{filename}': {e}")
        else:
            print(f"missing file: {filename}")

    data = np.array(data)
    X, y1, y2 = prepare_sequences_multi_output(data, sequence_length)

    if save_path:
        np.savez_compressed(save_path, X=X, y1=y1, y2=y2)
        print(f"saved dataset to {save_path}")

    return X, y1, y2
