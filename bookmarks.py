from http.server import HTTPServer, BaseHTTPRequestHandler

import requests

from urllib.parse import unquote, parse_qs

memory = {}
longuri = ""
shortname = ""

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shortname">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''


def checkURI(uri, timeout=5):

    try:
        r = requests.get(uri)
        return r.status_code == 200
    except requests.RequestException:
        return False


class shortener(BaseHTTPRequestHandler):

    def do_GET(self):
        name = unquote(self.path[1:])

        if name:
            if name in memory:
                self.send_response(303)
                self.send_header('Location', memory[name])
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain;charset=utf-8')
                self.end_headers()
                self.wfile.write("I dont know '{}'.".format(name).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            known = ""
            for key in sorted(memory.keys()):
                known = "".join("{} : {}".format(key, memory[key]))
            self.wfile.write(form.format(known).encode())

    def do_POST(self):
        length = int(self.headers.get('Content-length', 0))

        body = self.rfile.read(length).decode()
        params = parse_qs(body)

        print(params)

        if "longuri" not in params or "shortname" not in params:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain;charset=utf-8')
            self.end_headers()

            self.wfile.write("Missing form fields".encode())

            return

        longuri = params["longuri"][0]
        shortname = params["shortname"][0]

        if checkURI(longuri):
            memory[shortname] = longuri

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain;charset=utf-8')
            self.end_headers()
            self.wfile.write(
                "Couldnt fetch the URI {}".format(longuri).encode())


if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, shortener)
    httpd.serve_forever()
