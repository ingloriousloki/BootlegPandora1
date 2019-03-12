from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import flash, redirect, url_for
from flask_session import Session
import json
import requests
import urllib
import urllib.parse
from urllib.parse import urlencode, quote_plus
from factory import InfoForm



from factory import create_app
import db

#  Client Keys
CLIENT_ID = '4e3f3c32144244c09107fa56c451449c'
CLIENT_SECRET = "2d05d721c21f4ced95e17438dc038e43"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/en/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 56565
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

app = create_app()
app.config.from_object(__name__)
Session(app)

@app.route('/')
def homepage():
    return render_template('base.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    try:
        session["loggedIn"]
    except:
        if db.try_signon(request.form["email"], request.form["password"]):
            session["loggedIn"] = True
            session["username"] = db.get_username(request.form["email"])

            return render_template('loggedIn.html', username=session["username"])

        else:
            return render_template('badLogin.html')
    else:
        return render_template('search.html')


@app.route('/find-artist', methods=["POST"])
def findArtist():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        artist_list, song_list = db.display_artist(request.form["artist"], session["username"])
        print(artist_list)
        return render_template('display_by_artist.html', album_data=artist_list, song_data=song_list,
                               artist=request.form["artist"])


@app.route('/find-song', methods=["POST"])
def findSong():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        song_list = db.display_song(request.form["song"], session["username"])
        print(song_list)
        return render_template('display_song.html', song_data=song_list, song=request.form["song"])


@app.route('/find-album', methods=["POST"])
def findAlbum():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        album_list, artistName = db.display_album(request.form["album"], session["username"])
        print(album_list)
        return render_template('display_album.html', album_data=album_list, album=request.form["album"],
                               artist=artistName)


@app.route('/find-composer', methods=["POST"])
def findComposer():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        composer_list = db.display_composer(request.form["composer"], session["username"])
        print(composer_list)
        return render_template('display_composer.html', composer_data=composer_list, composer=request.form["composer"])


@app.route('/new-artist', methods=["POST"])
def newArtist():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        db.create_artist(request.form["artist"], session["username"])

        return render_template('dataAdded.html', data=request.form["artist"])


@app.route('/new-composer', methods=["POST"])
def newComposer():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        db.create_composer(request.form["composer"], session["username"])

        return render_template('dataAdded.html', data=request.form["composer"])


@app.route('/delete', methods=["post"])
def delete():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        db.delete(session["username"], request.form["data-type"], request.form["data"])
        flash('Deleted {} from your music'.format(request.form["data"]))
        return redirect(url_for('search'))


@app.route('/new-album', methods=["post"])
def newAlbum():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        db.create_album(session["username"], request.form["artist"], request.form["album"])
        flash('Album Added')
        return redirect(url_for('search'))


@app.route('/new-song', methods=["post"])
def newSong():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        db.create_song(session["username"], request.form["artist"], request.form["song"], request.form["album"],
                       request.form["composer"])
        flash('Song Added')
        return redirect(url_for('search'))


@app.route('/update-album', methods=["post"])
def updateAlbum():
    try:
        session["loggedIn"]
    except:
        return render_template('login.html')
    else:
        db.update_album(session["username"], request.form["artist"], request.form["album"],
                        request.form["song"], request.form["composer"], request.form["release"],
                        request.form["genre"], request.form["link"])
        album_list, artistName = db.display_album(request.form["album"], session["username"])
        return render_template('display_album.html', album_data=album_list, album=request.form["album"],
                               artist=request.form["artist"])


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/search')
def search():
    return render_template('search.html')


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/add_song')
def add_song():
    return render_template('add_song.html')


@app.route('/display_data')
def display_data():
    return render_template('displayData.html')


@app.route('/play', methods=["GET", "POST"])
def play():
    form = InfoForm()
    # if form.validate_on_submit():
    #     session['playartist'] = form.artist.data
    #     print(session['playartist'])
    if request.method == 'POST':
        session['playartist'] = form.artist.data
        print(session['playartist'])
        return redirect(url_for('play_artist'))

    return render_template('playlist.html', form=form)


@app.route('/new-user', methods=["POST"])
def new_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    if db.check_for_user(username, email):
        return render_template('userExists.html')

    if len(password) <= 20:
        db.create_user(username, password, email)

        session['username'] = username
        session['loggedIn'] = True

        return render_template('newUser.html', username=username)
    else:
        return render_template('invalidPassword.html')


@app.route('/db-test/', methods=["GET", "POST"])
def dbTest():
    try:
        c, conn = connection()
        return "good"
    except Exception as e:
        return (str(e))


@app.route("/play-artist")
def play_artist():
    # Authorization
    url_args = "&".join(["{}={}".format(key, urllib.parse.quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    print("authorized here")
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, auth=(CLIENT_ID, CLIENT_SECRET))

    # Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    print("response data: ", response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    print(session)
    # Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    print(session['playartist'])
    # Get profile data
    playlist_data = {'q': {session['playartist']}, 'type': 'playlist', 'limit': '3'}
    play_payload = urlencode(playlist_data, quote_via=quote_plus)
    playlist_api_endpoint = "{}/search?{}".format(SPOTIFY_API_URL, play_payload)
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    play_data = json.loads(playlists_response.text)
    print('endpoint: ')
    print(playlist_api_endpoint)
    print('URL is: ')
    play_list_payload = play_data["playlists"]["items"]
    # Combine profile and playlist data to display
    display_arr = [play_data]
    return render_template("displayData.html", playlist=play_list_payload)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=56565)
