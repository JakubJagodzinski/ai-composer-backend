import datetime
import os
import random

import mido
import numpy as np
from tensorflow.keras.models import load_model

from ai_module.resources.filename_generator import generate_filename
from diversity import Diversity

# --- Constants ---
EVENT_TYPES = ['note_on', 'note_off', 'control_change', 'program_change']

MAX_VALUES = {
    'channel': 15,
    'note': 127,
    'velocity': 127,
    'program': 127,
    'control': 127,
    'value': 127,
    'time': 65530
}

POP_GENERATION_VALUES = {
    0.4: [0.03, 0.07],
    0.6: [0.00],
    1.0: [0.03],
    1.7: [0.05],
    2.0: [0.01]
}

ROCK_GENERATION_VALUES = {
    0.4: [0.00, 0.01],
    0.6: [0.01],
    0.8: [0.01],
    2.0: [0.00, 0.01]
}

COUNTRY_GENERATION_VALUES = {
    0.1: [0.00, 0.01],
    0.4: [0.01],
    0.8: [0.01],
}


# --- Vector helpers ---
def denorm(value, key):
    return int(value * MAX_VALUES[key])


def decode_event_vector(event_vector):
    event_type_idx = np.argmax(event_vector[:4])
    event_type = EVENT_TYPES[event_type_idx]
    fields = event_vector[4:]

    if event_type in ['note_on', 'note_off']:
        return mido.Message(
            event_type,
            channel=denorm(fields[0], 'channel'),
            note=denorm(fields[1], 'note'),
            velocity=denorm(fields[2], 'velocity'),
            time=denorm(fields[6], 'time')
        )
    elif event_type == 'control_change':
        return mido.Message(
            event_type,
            channel=denorm(fields[0], 'channel'),
            control=denorm(fields[3], 'control'),
            value=denorm(fields[4], 'value'),
            time=denorm(fields[6], 'time')
        )
    elif event_type == 'program_change':
        return mido.Message(
            event_type,
            channel=denorm(fields[0], 'channel'),
            program=denorm(fields[5], 'program'),
            time=denorm(fields[6], 'time')
        )
    return None


# --- Prediction ---
def pad_sequence_to_length(seq, target_len):
    if len(seq) >= target_len:
        return seq[-target_len:]
    pad_amount = target_len - len(seq)
    padding = np.zeros((pad_amount, seq.shape[1]), dtype=np.float32)
    return np.vstack([padding, seq])


def generate_sequence(
        model,
        seed_sequence,
        genre_vector,
        length=500,
        fixed_length=50,
        temperature=0.01,
        param_noise_std=0.001
):
    def sample_with_temperature(logits, temp):
        logits = np.log(np.clip(logits, 1e-8, 1.0)) / temp
        probs = np.exp(logits) / np.sum(np.exp(logits))
        return np.random.choice(len(probs), p=probs)

    generated = []
    sequence = pad_sequence_to_length(seed_sequence, fixed_length)

    while len(generated) < length:
        input_seq = np.expand_dims(sequence, axis=0)
        input_genre = np.expand_dims(genre_vector, axis=0)

        y_type_logits, y_params = model.predict(
            {"sequence_input": input_seq, "genre_input": input_genre}, verbose=0
        )

        # sample event type using temperature
        event_type_idx = sample_with_temperature(y_type_logits[0], temperature)

        # create one-hot event type
        event_type = np.zeros_like(y_type_logits[0])
        event_type[event_type_idx] = 1.0

        # add noise to params to avoid exact loops
        y_params_noisy = y_params[0] + np.random.normal(0, param_noise_std, size=y_params[0].shape)
        y_params_noisy = np.clip(y_params_noisy, 0, 1)

        # combine and decode
        event_vector = np.concatenate([event_type, y_params_noisy])
        msg = decode_event_vector(event_vector)
        if msg:
            generated.append(msg)

        # update sequence
        next_vec = np.concatenate([event_type, y_params_noisy])
        sequence = np.vstack([sequence[1:], next_vec])

    return generated


# --- Save to MIDI ---
def save_midi(messages, output_path="generated_output_v2.mid", instrument=0):
    midi = mido.MidiFile(ticks_per_beat=1000)
    track = mido.MidiTrack()
    midi.tracks.append(track)

    for i in range(0, MAX_VALUES['channel']):
        track.append(mido.Message('program_change', program=instrument, channel=i, time=0))

    for msg in messages:
        track.append(msg)

    midi.save(output_path)
    print(f"[INFO] Saved MIDI to: {output_path}")

    return midi


def generate_genre_vector(genre):
    genre_dict = {
        'pop': [1, 0, 0],
        'rock': [0, 1, 0],
        'country': [0, 0, 1],
        'undefined': [0, 0, 0],
    }
    return np.array(genre_dict.get(genre.strip().lower(), [0, 0, 0]), dtype=np.float32)


def random_genre_vector():
    genres = ['pop', 'rock', 'country']
    chosen = np.random.choice(genres)
    return generate_genre_vector(chosen), chosen


def create_random_event_vector():
    event_type_idx = np.random.randint(0, len(EVENT_TYPES))
    event_one_hot = np.zeros(len(EVENT_TYPES), dtype=np.float32)
    event_one_hot[event_type_idx] = 1.0

    params = np.zeros(7, dtype=np.float32)

    if EVENT_TYPES[event_type_idx] in ['note_on', 'note_off']:
        params[0] = np.random.rand()
        params[1] = np.random.rand()
        params[2] = np.random.rand()
        params[6] = np.random.rand()
    elif EVENT_TYPES[event_type_idx] == 'control_change':
        params[0] = np.random.rand()
        params[3] = np.random.rand()
        params[4] = np.random.rand()
        params[6] = np.random.rand()
    elif EVENT_TYPES[event_type_idx] == 'program_change':
        params[0] = np.random.rand()
        params[5] = np.random.rand()
        params[6] = np.random.rand()

    return np.concatenate([event_one_hot, params])


def generate_random_seed_sequence(length=5, input_dim=11, fixed_length=50):
    seed = np.array([create_random_event_vector() for _ in range(length)], dtype=np.float32)
    return pad_sequence_to_length(seed, fixed_length)


def run_batch_tests():
    model_path = "model/final_model_3.keras"
    if not os.path.exists(model_path):
        print("[ERROR] Model file not found.")
        return

    model = load_model(model_path)
    fixed_length = 50
    input_dim = 11
    sequence_length = 200

    genres = ['pop', 'rock', 'country']
    temperatures = [0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.7, 2.0]
    param_noise_values = [0.0, 0.01, 0.03, 0.05, 0.07]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for genre in genres:
        genre_vector = generate_genre_vector(genre)

        for temp in temperatures:
            for noise in param_noise_values:
                subdir = f"results/Tests_new_model/{genre}/T{temp}_N{noise}"
                os.makedirs(subdir, exist_ok=True)

                seed_sequence = generate_random_seed_sequence(
                    length=np.random.randint(1, 10),
                    input_dim=input_dim,
                    fixed_length=fixed_length
                )

                filename = f"{timestamp}_{genre}_T{temp}_N{noise}.mid"
                output_path = os.path.join(subdir, filename)

                print(f"[GEN] {genre} | T={temp} | noise={noise} -> {filename}")

                midi_msgs = generate_sequence(
                    model,
                    seed_sequence,
                    genre_vector,
                    length=sequence_length,
                    fixed_length=fixed_length,
                    temperature=temp,
                    param_noise_std=noise
                )

                save_midi(midi_msgs, output_path)

                txt_output_path = os.path.splitext(output_path)[0] + ".txt"
                with open(txt_output_path, "w") as txt_file:
                    for msg in midi_msgs:
                        txt_file.write(str(msg) + "\n")


def is_note_message(msg):
    return msg.type == 'note_on' or msg.type == 'note_off'


def is_sufficiently_note_based(midi_msgs, threshold=0.8):
    if not midi_msgs:
        return False
    note_count = sum(1 for msg in midi_msgs if is_note_message(msg))
    return (note_count / len(midi_msgs)) >= threshold


def find_temperature(temperatures, diversity):
    one_third_length = len(temperatures) // 3
    two_third_length = 2 * len(temperatures) // 3

    lower_third = temperatures[:one_third_length]
    middle_third = temperatures[one_third_length:two_third_length]
    upper_third = temperatures[two_third_length:]

    if diversity == Diversity.LOW:
        return random.choice(lower_third)
    elif diversity == Diversity.MEDIUM:
        return random.choice(middle_third)
    else:
        return random.choice(upper_third)


# --- Main function ---
def generate(
        model_path="ai_module/model/final_model_3.keras",
        output_path="ai_module/results/",
        sequence_length=1000,
        genre='undefined',
        instrument=113,
        diversity=Diversity.MEDIUM
):
    if not os.path.exists(model_path):
        print("[ERROR] Model file not found.")
        return

    model = load_model(model_path)

    fixed_length = 50
    input_dim = 11

    if genre is None:
        genre_vector, genre_name = random_genre_vector()
        print(f"[INFO] Losowy gatunek: {genre_name}")
    else:
        genre_vector = generate_genre_vector(genre)
        genre_name = genre
        print(f"[INFO] Użytkownik podał gatunek: {genre_name}")

    print(genre_vector)

    print("[INFO] Generowanie sekwencji...")

    filename = generate_filename(genre_vector)

    if genre_name == 'pop':
        temperature = find_temperature(list(POP_GENERATION_VALUES.keys()), diversity)
        noise = random.choice(POP_GENERATION_VALUES[temperature])
    elif genre_name == 'rock':
        temperature = find_temperature(list(ROCK_GENERATION_VALUES.keys()), diversity)
        noise = random.choice(ROCK_GENERATION_VALUES[temperature])
    elif genre_name == 'country':
        temperature = find_temperature(list(COUNTRY_GENERATION_VALUES.keys()), diversity)
        noise = random.choice(COUNTRY_GENERATION_VALUES[temperature])
    else:
        temperature = 2.0
        noise = 0.01

    print(f"[INFO] Wylosowana temperatura: {temperature}, szum: {noise}")

    while True:

        seed_sequence = generate_random_seed_sequence(
            length=np.random.randint(1, 40),
            input_dim=input_dim,
            fixed_length=fixed_length
        )

        # print(seed_sequence)

        midi_msgs = generate_sequence(
            model,
            seed_sequence,
            genre_vector,
            length=sequence_length,
            fixed_length=fixed_length,
            temperature=temperature,
            param_noise_std=noise
        )
        if not midi_msgs:
            continue

        note_messages = [msg for msg in midi_msgs if msg.type in ('note_on', 'note_off')]
        note_ratio = len(note_messages) / len(midi_msgs)

        if note_ratio >= 0.5:
            print(f"[INFO] Akceptowana sekwencja — {note_ratio:.1%} to note_on/note_off")
            break
        else:
            print(f"[INFO] Odrzucono sekwencję — tylko {note_ratio:.1%} to note_on/note_off")

    return save_midi(midi_msgs, output_path + filename, instrument)


if __name__ == "__main__":
    generate(genre='pop')
