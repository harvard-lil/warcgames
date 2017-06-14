import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from warcgames import load_challenges, challenge_list, base_dir, read_file

# COMMANDS

def update_files():
    challenges = load_challenges()
    challenge_list(challenges)
    readme_path = os.path.join(base_dir, 'README.md')
    readme_contents = read_file(readme_path)
    readme_contents = re.sub(r'(<!-- CHALLENGES -->\n).*?(\n<!-- END CHALLENGES-->)', r'\1%s\2' % challenge_list(challenges), readme_contents, flags=re.S)
    with open(readme_path, 'w') as out:
        out.write(readme_contents)

# INTERFACE

def main():
    if len(sys.argv) < 2:
        print("Please provide command to run.")
        sys.exit()
    command = globals().get(sys.argv[1])
    if not command:
        print("Unknown command.")
    command()

if __name__ == '__main__':
    main()