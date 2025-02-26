import json
from os import popen
from sys import argv
from subprocess import run
from contextlib import suppress
from pathlib import Path

import version


###############################################################################


shorthand = {
    '-maj': 'major',
    '-min': 'minor',
    '-d': 'development',
    '-dev': 'development'
}


###############################################################################


def main():
    prompt_text = 'Major, Minor, or Development Update?\n'
    try:
        update_type = argv[1].lower()
    except IndexError:
        update_type = input(prompt_text)

    if (commit_message := [arg for arg in argv[2:]]) != []:
        commit_message = ' '.join(commit_message)
    else:
        commit_message = input('Enter Git Commit message:\n')

    _update_version_number(update_type, prompt_text)
    _push_to_github(commit_message)


#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#


def _update_version_number(update_type, prompt_text):
    with suppress(KeyError):
        update_type = shorthand[update_type]

    try:
        version.update_code_version(update_type)
    except ValueError:
        while True:
            print("Invalid Input")
            update = input(prompt_text)

            try:
                version.update_code_version(update_type)
            except ValueError:
                continue
            break


def _push_to_github(commit_message):
    run(('git', 'add', '.'))
    run(('git', 'commit', '-m', commit_message))

    # Slicing off the attached '\n'
    git_hash = popen('git rev-parse @').read()[:-2]
    update = {
        'version': version.get_version_number(which='code').as_str,
        'hash': git_hash,
        'message': commit_message
    }
    with open(Path('version', 'updates.jsonl'), 'a') as f:
        f.write(f'{update}\n')

    run(('git', 'push'))


###############################################################################


if __name__ == '__main__':
    main()


###############################################################################
