import numpy as np
from data_operations.convert_data import denormalize_value_int, max_event_fields_values
from mido import MidiFile, MidiTrack, Message


def vector_to_event(vector):
    event_vector = vector[0:3]
    print(event_vector)
    fields_vector = vector[3:]
    print(fields_vector)

    event_types = ['note_on', 'note_off', 'control_change', 'program_change']
    event_index = np.argmax(event_vector)
    event_type = event_types[event_index]

    channel = denormalize_value_int(fields_vector[0], max_event_fields_values['channel'])
    note = denormalize_value_int(fields_vector[1], max_event_fields_values['note'])
    velocity = denormalize_value_int(fields_vector[2], max_event_fields_values['velocity'])
    control = denormalize_value_int(fields_vector[3], max_event_fields_values['control'])
    value = denormalize_value_int(fields_vector[4], max_event_fields_values['value'])
    program = denormalize_value_int(fields_vector[5], max_event_fields_values['program'])
    time = denormalize_value_int(fields_vector[6], max_event_fields_values['time'])

    kwargs = {'channel': channel, 'time': time}

    if event_type in ['note_on', 'note_off']:
        kwargs.update({'note': note, 'velocity': velocity})
    elif event_type == 'control_change':
        kwargs.update({'control': control, 'value': value})
    elif event_type == 'program_change':
        kwargs.update({'program': program})

    return Message(event_type, **kwargs)


def vectors_to_midi(vectors, output_path='output.mid'):
    midi = MidiFile()
    track = MidiTrack()
    midi.tracks.append(track)
    with open("output.txt", "w") as txt_file:
        for vector in vectors:
            try:
                msg = vector_to_event(vector)
                txt_file.write(str(msg) + "\n")
                track.append(msg)
            except Exception as e:
                print(f"Error decoding vector: {e}")

    midi.save(output_path)
    print(f"Saved MIDI to: {output_path}")
