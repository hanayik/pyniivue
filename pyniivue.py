from argparse import ArgumentParser
import sys
import os
import socket
import webbrowser
from flask import Flask, send_file, request, send_from_directory

# create an app instance
app = Flask(__name__)

# create the index route (default page)
@app.route("/<path:path>")
def index(path="index.html"):
    # send the web page if the base route is requested
    return send_from_directory('.', path)

@app.route('/files')
def files():
    # http://host:port/files?filename=/path/to/image.nii.gz
    # get the url query parameter 'filename'
    file = request.args.get('filename')
    return send_file(file, as_attachment=True)

def main():
    parser = ArgumentParser(description='app for viewing nifti images')
    # Required
    parser.add_argument('files', nargs='+', help='Files to view')
    # Optional
    parser.add_argument(
        '--port', type=int, default=8888,
        help='Port to try to use. Default 8888.'
    )
    parser.add_argument(
        '-n', '--no-open', action='store_true', dest='no_open',
        help='Do not automatically open the link'
    )
    args = parser.parse_args()
    host = 'localhost'
    port = int(args.port)
    in_files = args.files
    in_files_abs = [os.path.abspath(f) for f in in_files] # make sure we have the absolute path for each file

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex(('127.0.0.1', port)):
            sock.close()
        else:
            port += 1
            continue
        # construct the URL to print in the console. The user will navigate to this URL in their browser
        url = f"http://{host}:{port}/index.html?host={host}&port={port}&files={':'.join(in_files_abs)}"
        print('COPY THIS URL TO YOUR BROWSER: ', url)
        if not args.no_open:
            webbrowser.open(url)
        app.run(host, port)
        sys.exit(0)

if __name__ == '__main__':
    main()
