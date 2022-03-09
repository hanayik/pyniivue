import sys
import os
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

if __name__ == '__main__':
    host = 'localhost'
    port = 8888 # any port you want that does not require root access
    in_files = sys.argv[1:] # all command line arguments are considered files that the user would like to open
    in_files_abs = [os.path.abspath(f) for f in in_files] # make sure we have the absolute path for each file

    # construct the URL to print in the console. The user will navigate to this URL in their browser
    url = f"http://{host}:{port}/?host={host}&port={port}&files={':'.join(in_files_abs)}"
    print('COPY THIS URL TO YOUR BROWSER: ', url)
    #webbrowser.open(url) uncomment to open automatically in your default browser. Will not work if done within WSL
    app.run(host, port, debug=False)
