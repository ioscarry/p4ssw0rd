from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.renderers import get_renderer
from pyramid.view import view_config
import pass_check

# This acts as the view function
def hello_world(request):
    result = ""
    try:
        if request.POST["password"]:
            password = str(request.POST['password'])
            result = pass_check.main(password)
        else:
            result = ""
            password = ""
    except KeyError:
        result = "No password entered."
        password = ""
    layout = """<html>
    <head>
    <title>p4ssw0rd demo</title>
    </head>
    <body>
    <h2>DO NOT ENTER ANY PERSONAL PASSWORDS INTO THIS.</h2>
    <p>I do not store any information sent, but all text is processed server-side and transmitted in plaintext. Use only for experimentation.</p>
    <p>Please report any bugs or feature requests to <a href="mailto:threehams@gmail.com">threehams@gmail.com</a>.</p>
    <h2>Upcoming features</h2>
    <ul>
    <li>Better cost-checking (best-case and worst-case)</li>
    </ul>
    <form action="." method="POST">
    <input name="password" type="text" value="{}">
    <input name="Analyze" type="submit" >
    </form>
    {}
    </body>
    </html>""".format(password, result)
    return Response(layout)

def main():
    # Grab the config, add a view, and make a WSGI app
    config = Configurator()
    config.add_view(hello_world)
    app = config.make_wsgi_app()
    return app

if __name__ == '__main__':
    # When run from command line, launch a WSGI server and app
    app = main()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()