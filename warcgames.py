from __future__ import print_function

import argparse
import distutils.dir_util
import os
import socket
import subprocess
import sys
from collections import OrderedDict

try:
    # PY2
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    import SocketServer
except ImportError:
    # PY3
    from http.server import SimpleHTTPRequestHandler
    import socketserver as SocketServer

import shutil

# paths
base_dir = os.path.abspath(os.path.dirname(__file__))
webrecorder_dir = os.path.join(base_dir, 'contrib/webrecorder')
archive_server_dir = os.path.join(base_dir, 'archive_server_temp')
support_files_dir = os.path.join(base_dir, 'support_files')
init_script_path = os.path.join(archive_server_dir, 'init-default.sh')
env_path = os.path.join(archive_server_dir, 'wr.env')
data_dir = os.path.join(archive_server_dir, 'data')
hosts_path = os.path.join(support_files_dir, 'hosts')
attacker_files_dir = os.path.join(base_dir, 'attacker_files')
wr_config_path = os.path.join(archive_server_dir, 'webrecorder/webrecorder/config/wr.yaml')
challenges_dir = os.path.join(base_dir, 'challenges')
overlay_files_dir = os.path.join(support_files_dir, 'overlay_files')
output_template_dir = os.path.join(archive_server_dir, 'webrecorder/webrecorder/templates')

# constants
PY2 = sys.version_info[0] < 3
APP_HOST = "warcgames.test:8089"
DEFAULT_CONTENT_HOST = "warcgames-content.test:8089"
ATTACKER_HOST = "attacker.test:8090"

# https://stackoverflow.com/a/287944/307769
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


### HELPERS ###

def read_file(path):
    with open(path) as in_file:
        return in_file.read()

def set_env(**kwargs):
    with open(env_path, 'a') as out:
        out.write("\n# warcgames additions\n")
        for key, val in kwargs.items():
            out.write("%s=%s\n" % (key, val))

def get_input(*args):
    if PY2:
        return raw_input(*args)
    else:
        return input(*args)

def import_path(module_name, path):
    """
        Import python module by path. 
    """
    if PY2:
        import imp
        return imp.load_source(module_name, path)
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


### STANDARD INIT SCRIPT ###

def init():
    # check hosts file
    hosts_file = read_file(hosts_path)
    hosts = [line.split()[1] for line in hosts_file.strip().split("\n")]
    for host in hosts:
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            print("%s does not resolve. Please add the following to /etc/hosts:\n\n%s" % (host, hosts_file))
            sys.exit(1)

    # load git submodules
    if not os.path.exists(init_script_path):
        print("Loading git submodules ...")
        subprocess.check_call(['git', 'submodule', 'init'])

    # attempt to update submodules
    subprocess.call(['git', 'submodule', 'update', '--recursive', '--remote'])

    # create temp archive server
    if os.path.exists(archive_server_dir):
        shutil.rmtree(archive_server_dir)
    subprocess.check_call(['git', '-C', webrecorder_dir, 'checkout-index', '-a', '-f', '--prefix='+archive_server_dir.rstrip('/')+'/'])

    # init archive_server
    subprocess.check_call(['sh', init_script_path])

    # copy overlay files
    distutils.dir_util.copy_tree(overlay_files_dir, archive_server_dir)

    # default env
    set_env(
        APP_HOST=APP_HOST,
        CONTENT_HOST=DEFAULT_CONTENT_HOST,
    )

def configure_challenge(challenge):
    config = challenge['config']
    print("%sChallenge: %s%s" % (bcolors.WARNING, config.short_message, bcolors.ENDC))

    # write env
    set_env(
        CONTENT_HOST=getattr(config, 'CONTENT_HOST', DEFAULT_CONTENT_HOST)
    )

    # write homepage message
    challenge_url = "http://%s/%s/challenge.html" % (ATTACKER_HOST, challenge['name'])
    message = config.message.format(
        challenge_url=challenge_url,
        challenge_path=challenge['path']
    )
    with open(os.path.join(output_template_dir, "challenge.html"), 'w') as out:
        out.write("""
            <h2>Current challenge: %s</h2>
            %s
        """ % (config.short_message, message))

    # write extra config to wr.yaml
    metadata = {
        'product': 'WARCgames Archive Server',
        'target_url': challenge_url
    }
    with open(wr_config_path, 'a') as out:
        out.write("metadata:\n" + "\n".join("    %s: %s" % (k, v) for k, v in metadata.items()) + "\n")

    # disable wombat template
    if not getattr(config, 'include_wombat', False):
        with open(os.path.join(output_template_dir, "head_insert.html"), 'w'):
            pass  # write blank file

    # write wsgi file
    wsgi_path = os.path.join(challenge['path'], 'wsgi.py')
    if os.path.exists(wsgi_path):
        shutil.copy(wsgi_path, os.path.join(support_files_dir, 'challenge_wsgi.py'))

def launch(debug):
    os.chdir(archive_server_dir)
    docker_command = ['docker-compose', '-f', 'docker-compose.yml', '-f', os.path.join(support_files_dir, 'docker-compose.override.yml'), 'up', '--remove-orphans']
    env = dict(os.environ, WARCGAMES_ROOT=base_dir)
    if debug:
        subprocess.check_call(docker_command, env=env)
    else:
        subprocess.check_call(docker_command+['-d'], env=env)
        print(bcolors.OKGREEN, end='')
        print("Archive server is now running:   http://%s/" % APP_HOST)
        print("Attack server is now running:    http://%s/" % ATTACKER_HOST)
        print(bcolors.ENDC, end='')
        get_input("Press return to quit ...")
        print("Shutting down Docker containers ...")
        subprocess.call(['docker-compose', 'down'])


### CHALLENGES ###

def load_challenges():
    """
        Load challenges from challenges dir. 
    """
    challenges = OrderedDict()
    challenge_names = next(os.walk(challenges_dir))[1]
    for challenge_name in challenge_names:
        challenge_path = os.path.join(challenges_dir, challenge_name)
        challenges[challenge_name] = {
            'config': import_path(challenge_name+'.config', os.path.join(challenge_path, 'config.py')),
            'name': challenge_name,
            'path': challenge_path,
        }
    return challenges

def challenge_list(challenges):
    return "\n".join("* %s: %s" % (short_name, c['config'].short_message) for short_name, c in challenges.items())

### interface ###

def main():
    challenges = load_challenges()
    parser = argparse.ArgumentParser(description='WARCgames.')
    parser.add_argument('challenge_name',
                        help='name of challenge to run',
                        choices=challenges.keys(),
                        nargs='?')
    # parser.add_argument('--attacker-port',
    #                     # dest='attacker_port',
    #                     help='port to serve attacker files',
    #                     default=8090,
    #                     type=int)
    parser.add_argument('--debug',
                        help='print debug output to console',
                        action='store_true')
    args = parser.parse_args()
    if not args.challenge_name:
        print("Please supply a challenge name:\n\n"+challenge_list(challenges))
        sys.exit()

    init()
    configure_challenge(challenges[args.challenge_name])
    launch(debug=args.debug)



if __name__ == '__main__':
    main()
