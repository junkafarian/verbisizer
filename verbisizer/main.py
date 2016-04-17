import argparse
import random
from os.path import exists, join

WORD_TYPES = (
    'adjective', 'adverb', 'noun', 'pronoun', 'preposition', 'verb'
)

EXPECTED_WORD_FILES = ['{}s.txt'.format(t) for t in WORD_TYPES]

TEMPLATES = (
    '{subject} {verb} {adverb} {preposition}',
    '{adverb} {subject} {verb} {preposition}',
    '{preposition} {subject} {verb} {adverb}',
)

SUBJECTS_REQUIRING_CONJUGATION = (
    'all',
    'few',
    'I',
    'many',
    'most',
    'none',
    'others',
    'ours',
    'several',
    'some',
    'theirs',
    'these',
    'they',
    'those',
    'we',
    'you',
    'yours',
)

WORD_MAP = {}


def load_words(basedir):
    for filename in EXPECTED_WORD_FILES:
        abs_filename = join(basedir, filename)

        if not exists(abs_filename):
            raise RuntimeError

        with open(abs_filename, 'r') as f:
            WORD_MAP[t] = [word.strip() for word in f.readlines()]


def get_word(word_type):
    words = WORD_MAP.get(word_type)

    if not words:
        raise RuntimeError('No words loaded for {}'.format(word_type))

    return random.choice(words)


def probability(value):
    """ Accepts a floating point number between 0.0 and 1.0 and
    returns a boolean.
    """
    return value <= random.random()


def conjugate_verb(subject, verb):
    if subject not in SUBJECTS_REQUIRING_CONJUGATION:
        return verb

    # todo: handle alternative suffixes (address -> addresses)
    return verb + 's'


def get_descriptive_noun(with_adjective, with_article):
    """ Uses some random seeding to mark up a Noun with 'the' and/or
    an adjective.

    """
    struct = []

    if with_article:
        struct.append('the')

    if with_adjective:
        struct.append(get_word('adjective'))

    struct.append(get_word('noun'))

    return ' '.join(struct)


def get_preposition(with_adjective):
    struct = [get_word('preposition'), 'the']

    if with_adjective:
        struct.append(get_word('adjective'))

    struct.append(get_word('noun'))

    return ' '.join(struct)


def get_subject(noun_adjective, noun_article):
    """ Returns either a (descriptive) Noun or a Pronoun for the line.
    """
    return random.choice([
        get_descriptive_noun(
            with_adjective=noun_adjective, with_article=noun_article,
        ),
        get_word('pronoun')
    ])


def get_line(args):
    subject = ''
    verb = ''
    adverb = ''
    preposition = get_preposition(
        with_adjective=probability(args.include_adjective_with_preposition)
    )

    if probability(args.include_subject):
        subject = get_subject(
            noun_adjective=probability(args.include_adjective_with_noun),
            noun_article=probability(args.include_article_with_noun),
        )
        verb = conjugate_verb(subject, get_word('verb'))

    if probability(args.include_adverb):
        adverb = get_word('adverb')

    template = random.choice(TEMPLATES)

    return template.format(
        subject=subject, verb=verb, adverb=adverb, preposition=preposition
    )


def format_line(line):
    return line.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the verbisizer',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        'worddir', type=str,
        help=(
            'The base directory where the dictionary files are stored. '
            'The following files should be available: {}'.format(
                ', '.join(EXPECTED_WORD_FILES)
            )
        )
    )
    parser.add_argument(
        '--lines', type=int, metavar='N', default=10,
        help='The number of lines to be verbisized'
    )
    parser.add_argument(
        '--include-subject', type=float, metavar='P', default=0.5,
        help=(
            'Likelyhood of including a random subject & associated '
            'verb in the line'
        )
    )
    parser.add_argument(
        '--include-adverb', type=float, metavar='P', default=0.2,
        help='Likelyhood of including an adverb in the line'
    )
    parser.add_argument(
        '--include-adjective-with-preposition', type=float, default=0.5,
        help='Likelyhood of including an adjective with the preposition'
    )
    parser.add_argument(
        '--include-adjective-with-noun', type=float, default=0.5,
        help=(
            'Likelyhood of prefixing the subject noun with an adjective '
            '(if generated)'
        )
    )
    parser.add_argument(
        '--include-article-with-noun', type=float, default=0.3,
        help=(
            'Likelyhood of prefixing the subject noun with the '
            'article "the" (if generated)'
        )
    )

    # Parse the commandline args
    args = parser.parse_args()

    try:
        load_words(basedir=args.worddir)
    except RuntimeError:
        parser.print_help()
        exit(1)

    for n in range(args.lines):
        print(get_line(args))
