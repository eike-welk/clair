# Task List in Elm

This is an experimental implementation of the Task List in Elm.  Elm is a
functional language which looks a like ML or Ocaml. It is compiled into
JavaScript and runs in the web browser.

To run this you must install the Elm tools:

    https://guide.elm-lang.org/install.html

You must also install a browser extension which inserts CORS headers into all
web traffic, because the setup violates the *Same Origin Policy* of the browser.
For Firefox you can use *CORS Everywhere*:

    https://addons.mozilla.org/en-US/firefox/addon/cors-everywhere/

Then start elm's integrated web server with:

    elm-reactor -p 8001

And start the Django server (in its directory `/src/clairweb`) with:

    python manage.py runserver

