from flask import Flask, request, redirect, session, render_template, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
REDIRECT_URI = 'http://localhost:4002/callback'
SCOPE = 'user-read-currently-playing user-modify-playback-state user-read-playback-state playlist-read-private'

def create_spotify_oauth():
    return SpotifyOAuth(
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_handler=None
    )
@app.route('/welcome')
def welcome():
    return render_template('landing.html')
@app.route('/')
def index():
    sp_oauth = create_spotify_oauth()
    if not session.get('token_info'):
        auth_url = sp_oauth.get_authorize_url()
        if request.referrer and 'welcome' in request.referrer:
            return redirect(auth_url)
        return redirect('/welcome')
    return render_template('player.html')

@app.route('/callback')
def callback():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect('/')

@app.route('/current-track')
def get_current_track():
    if not session.get('token_info'):
        return jsonify({'error': 'Not authenticated'})
    
    try:
        token_info = session['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])
        current_track = sp.current_playback()
        
        if current_track is None:
            return jsonify({'error': 'No track playing'})
        
        track_data = {
            'name': current_track['item']['name'],
            'artist': current_track['item']['artists'][0]['name'],
            'album': current_track['item']['album']['name'],
            'cover_art': current_track['item']['album']['images'][0]['url'],
            'is_playing': current_track['is_playing'],
            'duration': current_track['item']['duration_ms'] / 1000,
            'current_time': current_track['progress_ms'] / 1000
        }
        return jsonify(track_data)
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/control/<action>', methods=['POST'])
def control_playback(action):
    if not session.get('token_info'):
        return jsonify({'error': 'Not authenticated'})
    
    try:
        token_info = session['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        if action == 'play':
            sp.start_playback()
        elif action == 'pause':
            sp.pause_playback()
        elif action == 'next':
            sp.next_track()
        elif action == 'previous':
            sp.previous_track()
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/prev-song', methods=['POST'])
def prev_song():
    if not session.get('token_info'):
        return jsonify({'error': 'Not authenticated'})
    
    try:
        token_info = session['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.previous_track()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/next-song', methods=['POST'])
def next_song():
    if not session.get('token_info'):
        return jsonify({'error': 'Not authenticated'})
    
    try:
        token_info = session['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.next_track()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/seek', methods=['POST'])
def seek():
    if not session.get('token_info'):
        return jsonify({'error': 'Not authenticated'})
    
    try:
        data = request.get_json()
        seek_time = int(data['time'] * 1000) 
        
        token_info = session['token_info']
        sp = spotipy.Spotify(auth=token_info['access_token'])
        sp.seek_track(seek_time)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(port=4002, debug=True)
