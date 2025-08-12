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
    
    def __init__(self):
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

    async def search_song(self, query):
        """Search for a single song and return info"""
        try:
            loop = asyncio.get_event_loop()
            
            # If it's not a URL, search for it
            if not self.is_url(query):
                query = f"ytsearch1:{query}"
            
            data = await loop.run_in_executor(
                None, 
                lambda: self.ytdl.extract_info(query, download=False)
            )
            
            if 'entries' in data and len(data['entries']) > 0:
                # Handle search results
                entry = data['entries'][0]
            else:
                # Handle direct URL
                entry = data
            
            if not entry:
                return None
            
            return {
                'title': entry.get('title', 'Unknown Title'),
                'url': entry.get('webpage_url', entry.get('url')),
                'duration': self.format_duration(entry.get('duration')),
                'uploader': entry.get('uploader', 'Unknown'),
                'view_count': entry.get('view_count', 0)
            }
            
        except Exception as e:
            print(f"Error searching for song: {e}")
            return None

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
        try:
            loop = asyncio.get_event_loop()
            
            # Temporarily allow playlists
            temp_options = self.ytdl_format_options.copy()
            temp_options['noplaylist'] = False
            temp_ytdl = yt_dlp.YoutubeDL(temp_options)
            
            data = await loop.run_in_executor(
                None,
                lambda: temp_ytdl.extract_info(url, download=False, process=False)
            )
            
            if not data or 'entries' not in data:
                return []
            
            playlist_info = []
            for entry in data['entries']:
                if entry:
                    # Extract basic info without full processing
                    playlist_info.append({
                        'title': entry.get('title', 'Unknown Title'),
                        'url': entry.get('webpage_url', f"https://www.youtube.com/watch?v={entry['id']}"),
                        'duration': self.format_duration(entry.get('duration')),
                        'uploader': entry.get('uploader', 'Unknown')
                    })
            
            return playlist_info
            
        except Exception as e:
            print(f"Error extracting playlist info: {e}")
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
        print(f"Found: {result['title']} - {result['duration']}")
    
    # Test multiple search
    print("\nTesting multiple search...")
    results = await streamer.search_multiple("lofi hip hop", limit=3)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']} - {result['duration']}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_streamer())