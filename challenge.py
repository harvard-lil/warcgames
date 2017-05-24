from __future__ import print_function

import argparse
from glob import glob

import os
import socket
import subprocess
import sys
import re
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

current_dir = os.path.abspath(os.path.dirname(__file__))
archive_server_dir = os.path.join(current_dir, 'archive_server')
init_script_path = os.path.join(archive_server_dir, 'init-default.sh')
env_path = os.path.join(archive_server_dir, 'wr.env')
hosts_path = os.path.join(current_dir, 'hosts')
attacker_path = os.path.join(current_dir, 'attacker_files')
overlay_path = os.path.join(current_dir, 'archive_server_overlays')
orig_template_dir = os.path.join(archive_server_dir, 'webrecorder/webrecorder/templates')
overlay_template_dir = os.path.join(overlay_path, 'archive_server_templates/templates_src')
output_template_dir = os.path.join(overlay_path, 'archive_server_templates/templates')
PY2 = sys.version_info[0] < 3
wr_host = "warcgames.test:8089"



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
    try:
        return raw_input(*args)
    except NameError:
        return input(*args)


### STANDARD INIT SCRIPT ###

def init():

    # load git submodules
    if not os.path.exists(init_script_path):
        print("Loading git submodules ...")
        subprocess.check_call(['git', 'submodule', 'init'])

    # check hosts file
    hosts_file = read_file(hosts_path)
    hosts = [line.split()[1] for line in hosts_file.strip().split("\n")]
    for host in hosts:
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            print("%s does not resolve. Please add the following to /etc/hosts:\n\n%s" % (host, hosts_file))
            sys.exit(1)

    # init archive_server
    if os.path.exists(env_path):
        os.unlink(env_path)
        shutil.rmtree(os.path.join(archive_server_dir, 'data'))
    subprocess.check_call(['sh', init_script_path])

    # copy templates
    if os.path.exists(output_template_dir):
        shutil.rmtree(output_template_dir)
    os.mkdir(output_template_dir)
    for filename in glob(os.path.join(orig_template_dir, '*.html')):
        shutil.copy(filename, output_template_dir)
    for filename in glob(os.path.join(overlay_template_dir, '*.html')):
        shutil.copy(filename, output_template_dir)

def configure_challenge(challenge_name):
    challenge = challenges[challenge_name]
    challenge_config_function = globals()['challenge_'+challenge_name]
    challenge_config_function()
    print("Challenge: %s\n\n%s\n\n" % (challenge['short_message'], challenge['message']))
    with open(os.path.join(output_template_dir, "challenge.html"), 'w') as out:
        out.write("""
            <h2>Current challenge: %s</h2>
            <pre>%s</pre>
        """ % (challenge['short_message'], challenge['message']))


def launch(attacker_port, debug):
    os.chdir(archive_server_dir)
    docker_command = ['docker-compose', '-f', 'docker-compose.yml', '-f', '../archive_server_overlays/docker-compose.override.yml', 'up']
    if debug:
        subprocess.check_call(docker_command)
    else:
        subprocess.check_call(docker_command+['-d'])
        print("Archive server is now running:   http://%s/" % wr_host)
        print("Attack server is now running:    http://attacker.test:%s/" % attacker_port)
        get_input("Hit a key to quit ...")
        subprocess.call(['docker-compose', 'down'])


### CHALLENGES ###

def challenge_same_domain():
    set_env(APP_HOST=wr_host, CONTENT_HOST=wr_host)

def challenge_same_subdomain():
    set_env(APP_HOST=wr_host, CONTENT_HOST="content.%s" % wr_host)

challenges = OrderedDict([
    ["same_domain", {
        "short_message": "Use cross-site scripting to control an archive user's account.",
        "message": """
            In this challenge, the archive server is configured to serve the user interface and captured web archive content
            on the same domain. This means that captured web content can fully control the user account of any
            logged-in user who views a capture.
            
            Your mission is to edit attacker_files/challenge_same_domain.html so that, when 
            http://attacker.test:8000/challenge_same_domain.html is captured and played back, it deletes all archives belonging
            to the current user.
        """
    }],
    ["same_subdomain", {
        "short_message": "Use session fixation to log in a viewer as another user.",
        "message": """
            In this challenge, the archive server is configured to serve the user dashboard at %s and 
            captured web archive content at content.%s. This means that captured web content can use
            session fixation to log in a visitor to a web archive as a different user. 
    
            Your mission is to edit attacker_files/challenge_same_subdomain.html so that, when 
            http://attacker.test:8000/challenge_same_domain.html is captured and played back, it deletes all archives belonging
            to the current user.
        """ % (wr_host, wr_host)
    }]
])


### interface ###

def main():
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
        print("Please supply a challenge name:\n\n"+"\n".join("* %s: %s" % (short_name, c['short_message']) for short_name, c in challenges.items()))
        sys.exit()

    init()
    configure_challenge(args.challenge_name)
    launch(attacker_port=8090, debug=args.debug)



if __name__ == '__main__':
    main()
