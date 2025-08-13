import discord
import yt_dlp
import asyncio
import re
from datetime import timedelta

class Song:
    """Represents a song with metadata"""
    def __init__(self, title, url, duration, requester):
        self.title = title
        self.url = url
        self.duration = duration
        self.requester = requester

class MusicStreamer:
    """Handles music streaming from various sources using yt-dlp"""
    
    def __init__(self, cookies_file=None):
        self.ytdl_format_options = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': 192,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Add cookie authentication if cookies file is provided
            'cookiefile': cookies_file if cookies_file else None,
            # Additional options to help with authentication issues
            'extractor_retries': 3,
            'fragment_retries': 3,
            'retry_sleep': 1,
            'max_sleep_interval': 5,
        }

        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_format_options)

    def format_duration(self, seconds):
        """Convert seconds to MM:SS or HH:MM:SS format"""
        if not seconds:
            return "Unknown"
        
        duration = timedelta(seconds=int(seconds))
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def is_url(self, query):
        """Check if query is a URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(query) is not None

    def is_spotify_url(self, query):
        """Check if query is a Spotify URL"""
        spotify_pattern = re.compile(r'^(https?://)?(open\.)?spotify\.com/(track|playlist|album)/[a-zA-Z0-9]+')
        return spotify_pattern.match(query) is not None

    async def extract_info(self, query, download=False, process=True):
        """Extracts info for a single song or playlist from a URL or search query."""
        try:
            loop = asyncio.get_event_loop()
            
            # If it's not a URL, search for it
            if not self.is_url(query):
                query = f"ytsearch1:{query}"
            
            data = await loop.run_in_executor(
                None, 
                lambda: self.ytdl.extract_info(query, download=download, process=process)
            )
            return data
        except Exception as e:
            print(f"Error extracting info for {query}: {e}")
            return None

    async def process_query(self, query, requester):
        """Process user query: identify if it's a URL (YouTube/Spotify) or search term, and return song(s) info."""
        songs_info = []
        
        if self.is_url(query):
            # Temporarily allow playlists for URL processing
            temp_options = self.ytdl_format_options.copy()
            temp_options['noplaylist'] = False
            temp_ytdl = yt_dlp.YoutubeDL(temp_options)
            
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    None,
                    lambda: temp_ytdl.extract_info(query, download=False, process=False)
                )

                if not data:
                    return []

                if 'entries' in data: # It's a playlist or album
                    for entry_data in data['entries']:
                        if entry_data:
                            # For playlists, we need to extract full info for each entry
                            full_entry_data = await self.extract_info(entry_data['url'])
                            if full_entry_data:
                                songs_info.append(Song(
                                    title=full_entry_data.get('title', 'Unknown Title'),
                                    url=full_entry_data.get('webpage_url', full_entry_data.get('url')),
                                    duration=self.format_duration(full_entry_data.get('duration')),
                                    requester=requester
                                ))
                else: # Single video/track
                    full_entry_data = await self.extract_info(query)
                    if full_entry_data:
                        songs_info.append(Song(
                            title=full_entry_data.get('title', 'Unknown Title'),
                            url=full_entry_data.get('webpage_url', full_entry_data.get('url')),
                            duration=self.format_duration(full_entry_data.get('duration')),
                            requester=requester
                        ))
            except Exception as e:
                print(f"Error processing URL {query}: {e}")
                return []
        else: # Treat as search query
            result_info = await self.extract_info(query)
            if result_info:
                # search_song used to return a dict, now extract_info returns the raw data
                # We need to process it similarly to how search_song did
                entry = result_info['entries'][0] if 'entries' in result_info else result_info
                songs_info.append(Song(
                    title=entry.get('title', 'Unknown Title'),
                    url=entry.get('webpage_url', entry.get('url')),
                    duration=self.format_duration(entry.get('duration')),
                    requester=requester
                ))
                
        return songs_info

    async def search_song(self, query):
        """Deprecated: Use process_query instead for comprehensive handling."""
        print("Warning: search_song is deprecated. Use process_query instead.")
        results = await self.process_query(query, None) # Requester is None for search
        return results[0] if results else None # Return first result for compatibility

    async def search_multiple(self, query, limit=5):
        """Search for multiple songs and return list"""
        try:
            loop = asyncio.get_event_loop()
            
            # Search for multiple results
            search_query = f"ytsearch{limit}:{query}"
            
            data = await loop.run_in_executor(
                None,
                lambda: self.ytdl.extract_info(search_query, download=False)
            )
            
            if not data or 'entries' not in data:
                return []
            
            results = []
            for entry in data['entries'][:limit]:
                if entry:
                    results.append({
                        'title': entry.get('title', 'Unknown Title'),
                        'url': entry.get('webpage_url', entry.get('url')),
                        'duration': self.format_duration(entry.get('duration')),
                        'uploader': entry.get('uploader', 'Unknown'),
                        'view_count': entry.get('view_count', 0)
                    })
            
            return results
            
        except Exception as e:
            print(f"Error searching for multiple songs: {e}")
            return []

    async def get_audio_source(self, url):
        """Get audio source for Discord from URL"""
        try:
            loop = asyncio.get_event_loop()
            
            # Extract info to get the actual audio stream URL
            data = await loop.run_in_executor(
                None,
                lambda: self.ytdl.extract_info(url, download=False)
            )
            
            if not data:
                return None
            
            # Get the best audio format URL
            if 'entries' in data:
                # Playlist case (shouldn't happen with noplaylist=True, but just in case)
                audio_url = data['entries'][0]['url']
            else:
                audio_url = data['url']
            
            # Create Discord audio source
            source = discord.FFmpegPCMAudio(audio_url, **self.ffmpeg_options)
            return source
            
        except Exception as e:
            print(f"Error getting audio source: {e}")
            return None

    async def get_playlist_info(self, url):
        """Extract playlist information"""
        print("Warning: get_playlist_info is deprecated. Use process_query instead.")
        # This method is now largely redundant with process_query handling playlists
        # However, if you specifically need just playlist metadata without full song processing,
        # you could adapt this. For now, returning empty list as process_query gives full songs.
        return []

    async def get_related_songs(self, current_url, limit=5):
        """Get related/recommended songs (for autoplay feature)"""
        try:
            # This is a placeholder - YouTube's related videos API is limited
            # You could implement this using YouTube Data API v3 or similar services
            # For now, we'll return an empty list
            return []
            
        except Exception as e:
            print(f"Error getting related songs: {e}")
            return []

    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'ytdl'):
                # yt-dlp doesn't need explicit cleanup, but we can clear cache if needed
                pass
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Example usage and testing functions
async def test_streamer():
    """Test function for the music streamer"""
    streamer = MusicStreamer()
    
    # Test search
    print("Testing search...")
    result = await streamer.search_song("Never Gonna Give You Up")
    if result:
        print(f"Found: {result.title} - {result.duration}")
    
    # Test multiple search using process_query
    print("\nTesting multiple search using process_query...")
    results = await streamer.process_query("lofi hip hop", requester="TestUser")
    for i, song in enumerate(results, 1):
        print(f"{i}. {song.title} - {song.duration}")

    # Test YouTube playlist
    print("\nTesting YouTube playlist...")
    # Replace with a real YouTube playlist URL for testing
    youtube_playlist_url = "https://youtube.com/playlist?list=PLNAy3gPVX0W9d1XQB3OV_KZUZqjgbnPZv&si=8sGy6FdrDneZblt_"
    playlist_songs = await streamer.process_query(youtube_playlist_url, requester="PlaylistTester")
    for i, song in enumerate(playlist_songs, 1):
        print(f"{i}. {song.title} - {song.duration}")

    # Test Spotify track (requires yt-dlp to support spotify links)
    print("\nTesting Spotify track...")
    # Replace with a real Spotify track URL for testing
    spotify_track_url = "https://open.spotify.com/track/3be9ACTxtcL6Zm4vJRUiPG?si=743882fc01a54b0d"
    spotify_song = await streamer.process_query(spotify_track_url, requester="SpotifyTester")
    if spotify_song:
        print(f"Found Spotify: {spotify_song[0].title} - {spotify_song[0].duration}")

    # Test Spotify playlist (requires yt-dlp to support spotify links)
    print("\nTesting Spotify playlist...")
    # Replace with a real Spotify playlist URL for testing
    spotify_playlist_url = "https://open.spotify.com/playlist/1r1EjCOumOLeWkkiqocNCH?si=lUb3WIkPRz6ixENL9gnSaw"
    spotify_playlist_songs = await streamer.process_query(spotify_playlist_url, requester="SpotifyPlaylistTester")
    for i, song in enumerate(spotify_playlist_songs, 1):
        print(f"{i}. {song.title} - {song.duration}")

    streamer.cleanup()

if __name__ == "__main__":
    # Run test
    asyncio.run(test_streamer())