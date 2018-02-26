from .menu_item import MenuItem

from pytify.core import search_artist
from pytify.core import get_artist_albums
from pytify.core import get_album_tracks
from pytify.core import play

from .empty_results_error import EmptyResultsError

from pytify.auth import authenticate
from pytify.core import read_config


class DataManager():

    def __init__(self):
        self._conf = read_config()
        self._auth = authenticate(self._conf)

    def search_artist(self, criteria):
        results = search_artist(criteria, self._auth)
        items = results['artists']['items']

        if not items:
            raise EmptyResultsError(f'Could not find the artist: {criteria}')

        return items[0]

    def _format_artist_label(self, item):
        return f'{item["name"]} ({item["type"]})'

    def _format_track_label(self, item):
        time = int(item['duration_ms'])
        minutes = int((time / 60000) % 60)
        seconds = int((time / 1000) % 60)

        track_name = item['name']

        return f'{track_name} - [{minutes}:{seconds}]'

    def get_artist_albums(self, artist_id, max_items=20):

        albums = get_artist_albums(artist_id, self._auth)['items']

        if not bool(albums):
            raise EmptyResultsError(('Could not find any albums for'
                                     f'the artist_id: {artist_id}'))

        return [MenuItem(self._format_artist_label(album), album)
                for album in albums[:max_items]]

    def get_album_tracklist(self, album_id):

        results = get_album_tracks(album_id, self._auth)

        if not results:
            raise EmptyResultsError('Could not find the tracks for this album')

        tracks = results['items']

        return [MenuItem(self._format_track_label(track), track)
                for track in tracks]

    def play(self, track_uri):
        play(track_uri, self._auth)