import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


CLIENT_ID = ""
CLIENT_SECRET = ""

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

playlist_url = "https://open.spotify.com/playlist/43VhyOk0yfm5LMdo9MotR4?si=2603f00c590c4f46"

def fetch_all_tracks(playlist_url: str):
    """
    Fetch ALL tracks from a public playlist, handling pagination (100 per page).
    Skips local files and podcast episodes.
    Returns list of (artist(s), title, album, year).
    """
    items = []
    # first page
    results = sp.playlist_items(
        playlist_url,
        limit=100,
        offset=0,
        additional_types=("track",),  # ignore episodes
        fields="items(track(name,artists(name),album(name,release_date),is_local,type)),next,total"
    )
    while True:
        for item in results.get("items", []):
            track = item.get("track")
            if not track:
                continue
            if track.get("type") != "track":
                continue
            if track.get("is_local"):
                continue

            title = track.get("name") or ""
            artists = ", ".join(a.get("name", "") for a in (track.get("artists") or []))
            album = (track.get("album") or {}).get("name", "")
            release_date = (track.get("album") or {}).get("release_date", "")
            year = release_date[:4] if release_date else ""
            items.append((artists, title, album, year))

        nxt = results.get("next")
        if not nxt:
            break
        # Spotipy helper to follow 'next' URL:
        results = sp.next(results)
    return items

tracks = fetch_all_tracks(playlist_url)

# Print & save
header = "Artist | Song | Album | Year"
lines = [header, "-" * len(header)]
for a, t, al, y in tracks:
    lines.append(f"{a} | {t} | {al} | {y}")

print("\n".join(lines))

out_file = "playlist_songs.txt"
with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅ Saved {len(tracks)} songs to {out_file}")
