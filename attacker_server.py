import os

try:
    # PY2
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    import SocketServer
except ImportError:
    # PY3
    from http.server import SimpleHTTPRequestHandler
    import socketserver as SocketServer

current_dir = os.path.abspath(os.path.dirname(__file__))
attacker_path = os.path.join(current_dir, 'attacker_files')
attacker_port = 8090

def main():
    os.chdir(attacker_path)
    try:
        httpd = SocketServer.TCPServer(('', attacker_port), SimpleHTTPRequestHandler)
    except OSError:
        print("Unable to bind to port %s. Use --attacker-port to bind to an alternate port." % attacker_port)
        return
    print("Running attack server")
    httpd.serve_forever()

if __name__ == "__main__":
    main()