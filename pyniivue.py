from argparse import ArgumentParser
import sys
import os
import socket
import webbrowser
from flask import Flask, send_file, request

# hide warning messages
os.environ["WERKZEUG_RUN_MAIN"] = "true"

# create an app instance
app = Flask(__name__)

# create the index route (default page)
@app.route("/")
def index():
    # send the web page if the base route is requested
    return send_file('./index.html')

@app.route('/files')
def files():
    # http://host:port/files?filename=/path/to/image.nii.gz
    # get the url query parameter 'filename'
    file = request.args.get('filename')
    return send_file(file, as_attachment=True)

def head(title="basic multiplanar", initial_scale=1.0, margin=20):
    """Generates a page header

    Parameters
    ----------
    title: str
        The title of the tab. Default "basic multiplanar".
    initial_scale: float
        The initial scaling. Default 1.0.
    margin: int
        The margin size in pixels. Default 20.

    Returns
    -------
    head, a str representing the header of the document
    """
    # Relevant substrings to replace are
    # - INITIAL_SCALE
    # - TITLE
    # - MARGIN
    headstr =  """
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width,initial-scale=INITIAL_SCALE">
    <title>TITLE</title>
    <style>
      section {
        margin: MARGINpx;
      }
    </style>
  </head>
    """
    headstr = headstr.replace("INITIAL_SCALE", str(initial_scale))
    headstr = headstr.replace("TITLE", title)
    headstr = headstr.replace("MARGIN", str(margin))
    print(headstr)
    return headstr[1:-5]


# The virtual representation of the HTML page
def index():
    """Returns the virtual HTML page

    Returns
    -------
    page: str
        A string representing the HTML index page
    """
    page = """
<!DOCTYPE html>
<html lang="en">
"""
    page += head()
    page += """
  <body style="font-family: sans-serif;">
    <noscript>
      <strong>niivue doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
    </noscript>

    <section>
      <h1>
        NiiVue
      </h1>
    </section>

    <section>
      <div id="demo" style="width:90%; height:400px;">
        <canvas id="gl" height=480 width=640>
        </canvas>
      </div>
    </section>
    <script src="https://unpkg.com/@niivue/niivue@0.22.2/dist/niivue.umd.js">
    </script>
    <script>

                    let urlParams = new URLSearchParams(window.location.search)
            let files = urlParams.get('files')
                    let host = urlParams.get('host')
                    let port = urlParams.get('port')
                    let inFiles = files.split(':')
                    let volumeList = []
                    let colors = ['red', 'green', 'blue']
                    for (i=0; i<inFiles.length; i++) {
                            volumeList.push({
                                    url: `http://${host}:${port}/files?filename=${inFiles[i]}`,
                                    colorMap: i < 1 ? 'gray' : colors[Math.floor(Math.random() * (3 - 0) + 0)]
                            })
                    }
      const nv = new niivue.Niivue()
      nv.attachTo('gl')
      nv.loadVolumes(volumeList)
      nv.setSliceType(nv.sliceTypeMultiplanar)

    </script>
  </body>
</html>
    """
    # Trim off extra characters
    return page[1:-4] + '\n'


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

    # Write the index file
    with open('index.html', 'w') as f:
        f.write(index())

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock.connect_ex(('127.0.0.1', port)):
            sock.close()
        else:
            port += 1
            continue
        # construct the URL to print in the console. The user will navigate to this URL in their browser
        url = f"http://{host}:{port}/?host={host}&port={port}&files={':'.join(in_files_abs)}"
        print('COPY THIS URL TO YOUR BROWSER: ', url)
        if not args.no_open:
            webbrowser.open(url)
        app.run(host, port, debug=False)
        sys.exit(0)

if __name__ == '__main__':
    main()
