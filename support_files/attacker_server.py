import os

try:
    # PY2
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    import SocketServer
except ImportError:
    # PY3
    from http.server import SimpleHTTPRequestHandler
    import socketserver as SocketServer

challenges_dir = '/challenges/'
attacker_port = 8090

def main():
    os.chdir(challenges_dir)
    try:
        httpd = SocketServer.TCPServer(('', attacker_port), SimpleHTTPRequestHandler)
    except OSError:
        print("Unable to bind to port %s. Use --attacker-port to bind to an alternate port." % attacker_port)
        return
    print("Running attack server")
    httpd.serve_forever()

if __name__ == "__main__":
    main()