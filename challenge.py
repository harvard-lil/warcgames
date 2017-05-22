from __future__ import print_function

import argparse
import os
import socket
import subprocess
import sys
import re
import threading
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
webrecorder_dir = os.path.join(current_dir, 'webrecorder')
init_script_path = os.path.join(webrecorder_dir, 'init-default.sh')
env_path = os.path.join(webrecorder_dir, 'wr.env')
hosts_path = os.path.join(current_dir, 'hosts')
attacker_path = os.path.join(current_dir, 'attacker_files')
PY2 = sys.version_info[0] < 3
wr_host = "warcgames.test:8089"



### HELPERS ###

def read_file(path):
    with open(path) as in_file:
        return in_file.read()

def set_env(**kwargs):
    env_file = read_file(env_path)
    for key, val in kwargs.items():
        pattern = r'^\s*'+key+r'\s*=\s*'
        if re.search(pattern, env_file):
            env_file = re.sub(pattern, val, env_file)
        else:
            env_file += "\n%s=%s\n" % (key, val)
    with open(env_path, 'w') as out:
        out.write(env_file)

# def get_input(*args):
#     try:
#         return raw_input(*args)
#     except NameError:
#         return input(*args)


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

    # init webrecorder
    if os.path.exists(env_path):
        os.unlink(env_path)
        shutil.rmtree(os.path.join(webrecorder_dir, 'data'))
    subprocess.check_call(['sh', init_script_path])

def launch(attacker_port, debug):
    os.chdir(webrecorder_dir)
    docker_command = ['docker-compose', '-f', 'docker-compose.yml', '-f', '../docker-compose.override.yml', 'up']
    if debug:
        docker_thread = threading.Thread(target=lambda: subprocess.check_call(docker_command))
        docker_thread.daemon=True
        docker_thread.start()
    else:
        subprocess.check_call(docker_command+['-d'])
    print("Webrecorder is now running: http://%s/" % wr_host)

    os.chdir(attacker_path)
    try:
        httpd = SocketServer.TCPServer(('', attacker_port), SimpleHTTPRequestHandler)
    except OSError:
        print("Unable to bind to port %s. Use --attacker-port to bind to an alternate port." % attacker_port)
        return
    # threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print("Running attack server: http://attacker.test:%s/\nHit ctrl-c to exit." % attacker_port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

def cleanup():
    subprocess.call(['docker-compose', 'down'])

### CHALLENGES ###

def challenge_same_domain():
    set_env(APP_HOST=wr_host, CONTENT_HOST=wr_host)

def challenge_same_subdomain():
    set_env(APP_HOST=wr_host, CONTENT_HOST="content.%s" % wr_host)

challenges = OrderedDict([
    ["same_domain", {
        "short_message": "Use cross-site scripting to control a Webrecorder account.",
        "message": """
            In this challenge, Webrecorder is configured to serve the user interface and captured web archive content
            on the same domain. This means that captured web content can fully control the Webrecorder account of any
            logged-in user who views a capture, via cross-site scripting.
            
            Your mission is to edit attacker_files/challenge_same_domain.html so that, when 
            http://attacker.test:8000/challenge_same_domain.html is captured and played back, it deletes all archives belonging
            to the current user.
        """
    }],
    ["same_subdomain", {
        "short_message": "Use session fixation to log in a viewer as another user.",
        "message": """
            In this challenge, Webrecorder is configured to serve the user dashboard at %s and 
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
    parser.add_argument('--attacker-port',
                        # dest='attacker_port',
                        help='port to serve attacker files',
                        default=8090,
                        type=int)
    parser.add_argument('--debug',
                        help='print Webrecorder debug output to console',
                        action='store_true')
    args = parser.parse_args()
    if not args.challenge_name:
        print("Please supply a challenge name:\n\n"+"\n".join("* %s: %s" % (short_name, c['short_message']) for short_name, c in challenges.items()))
        sys.exit()
    challenge = challenges[args.challenge_name]
    challenge_config_function = globals()['challenge_'+args.challenge_name]

    init()
    challenge_config_function()
    print("Challenge: %s\n\n%s\n\n" % (challenge['short_message'], challenge['message']))
    launch(attacker_port=args.attacker_port, debug=args.debug)



if __name__ == '__main__':
    main()
