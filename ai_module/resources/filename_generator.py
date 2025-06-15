import random

reversed_genre_dict = {
    (1, 0, 0): 'pop',
    (0, 1, 0): 'rock',
    (0, 0, 1): 'country'
}

genre_parts = {
    'pop': [
        'glitter', 'bubblegum', 'sparklez', 'autotune', 'neon', 'vibefreak',
        'discofish', 'tiktokqueen', 'pastelstorm', 'bopzilla'
    ],
    'rock': [
        'riffbeast', 'loudboi', 'grungebucket', 'mulletking', 'ampzilla', 'moshghost',
        'shredstorm', 'screamduck', 'metalpickle', 'solo_daddy'
    ],
    'country': [
        'cowpoke', 'banjo_vortex', 'yallinator', 'whiskeytwang', 'bootblast', 'dustghost',
        'haybanger', 'tractorfever', 'twangzilla', 'hoedownlord'
    ],
    'unknown': [
        'weirdcore', 'vibestrash', 'genre404', 'noisepudding', 'errorpop',
        'echosquid', 'uncannybeat', 'glitchcow', 'nonsensefuzz'
    ]
}

adjectives = [
    'epic', 'cursed', 'yeehaw', 'spicy', 'feral', 'chaotic',
    'unholy', 'supreme', 'ultimate', 'awkward', 'demonic', 'baby', 'cringe'
]

emojis = ['🔥', '🎸', '🐴', '🌈', '💀', '👢', '😩', '👑', '🎤', '🚀', '🤠', '💅', '🛸']


def generate_filename(genre_vector):
    genre_key = tuple(int(x) for x in genre_vector[:3].tolist())
    genre = reversed_genre_dict.get(genre_key, 'unknown')

    words = genre_parts.get(genre, genre_parts['unknown'])
    name_parts = random.sample(words, 2)
    adjective = random.choice(adjectives)
    emoji = random.choice(emojis)

    filename = f"{genre}_{adjective}_{name_parts[0]}_{name_parts[1]}_{emoji}.mid"
    return filename
