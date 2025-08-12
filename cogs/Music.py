import json
import discord
import asyncio
import random
from datetime import datetime
from discord.ext import commands, tasks
from music_streamer import MusicStreamer, Song

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.streamer = MusicStreamer()
        self.queues = {}  # Guild-specific queues
        self.current_songs = {}  # Currently playing songs per guild
        self.voice_clients = {}  # Voice clients per guild
        self.loop_modes = {}  # Loop modes: 0=off, 1=track, 2=queue
        self.volumes = {}  # Volume levels per guild (default 0.5)

    def get_queue(self, guild_id):
        """Get or create queue for guild"""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def get_voice_client(self, guild):
        """Get voice client for guild"""
        return self.voice_clients.get(guild.id)

    async def join_voice_channel(self, ctx):
        """Join the user's voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel!")
            return None
        
        channel = ctx.author.voice.channel
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.channel != channel:
                await voice_client.move_to(channel)
        else:
            voice_client = await channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
        
        return voice_client

    async def play_next(self, ctx):
        """Play the next song in queue"""
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        voice_client = self.get_voice_client(ctx.guild)
        
        if not queue or not voice_client:
            return
        
        # Handle loop modes
        loop_mode = self.loop_modes.get(guild_id, 0)
        if loop_mode == 1 and guild_id in self.current_songs:  # Loop track
            next_song = self.current_songs[guild_id]
        elif loop_mode == 2 and queue:  # Loop queue
            next_song = queue.pop(0)
            queue.append(next_song)  # Add back to end
        else:  # Normal play
            if not queue:
                return
            next_song = queue.pop(0)
        
        self.current_songs[guild_id] = next_song
        
        # Get audio source
        audio_source = await self.streamer.get_audio_source(next_song.url)
        if not audio_source:
            await ctx.send(f"❌ Failed to play: {next_song.title}")
            await self.play_next(ctx)
            return
        
        # Set volume
        volume = self.volumes.get(guild_id, 0.5)
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=volume)
        
        # Play the song
        voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))
        
        embed = discord.Embed(title="🎵 Now Playing", color=0x00ff00)
        embed.add_field(name="Song", value=next_song.title, inline=False)
        embed.add_field(name="Duration", value=next_song.duration, inline=True)
        embed.add_field(name="Requested by", value=next_song.requester.mention, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def play(self, ctx, *, song: str):
        """Play a song or add it to queue"""
        voice_client = await self.join_voice_channel(ctx)
        if not voice_client:
            return
        
        await ctx.send(f"🔍 Searching for: `{song}`")
        
        # Search for the song
        song_info = await self.streamer.search_song(song)
        if not song_info:
            await ctx.send("❌ No results found!")
            return
        
        song_obj = Song(
            title=song_info['title'],
            url=song_info['url'],
            duration=song_info['duration'],
            requester=ctx.author
        )
        
        queue = self.get_queue(ctx.guild.id)
        
        if voice_client.is_playing():
            queue.append(song_obj)
            embed = discord.Embed(title="📝 Added to Queue", color=0x0099ff)
            embed.add_field(name="Song", value=song_obj.title, inline=False)
            embed.add_field(name="Position", value=f"{len(queue)}", inline=True)
            embed.add_field(name="Duration", value=song_obj.duration, inline=True)
            await ctx.send(embed=embed)
        else:
            self.current_songs[ctx.guild.id] = song_obj
            audio_source = await self.streamer.get_audio_source(song_obj.url)
            if audio_source:
                volume = self.volumes.get(ctx.guild.id, 0.5)
                audio_source = discord.PCMVolumeTransformer(audio_source, volume=volume)
                voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop))
                
                embed = discord.Embed(title="🎵 Now Playing", color=0x00ff00)
                embed.add_field(name="Song", value=song_obj.title, inline=False)
                embed.add_field(name="Duration", value=song_obj.duration, inline=True)
                embed.add_field(name="Requested by", value=song_obj.requester.mention, inline=True)
                await ctx.send(embed=embed)

    @commands.command()
    async def pause(self, ctx):
        """Pause the current song"""
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("⏸️ Music paused!")
        else:
            await ctx.send("❌ Nothing is playing!")

    @commands.command()
    async def resume(self, ctx):
        """Resume the paused song"""
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("▶️ Music resumed!")
        else:
            await ctx.send("❌ Music is not paused!")

    @commands.command()
    async def stop(self, ctx):
        """Stop the music and clear queue"""
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client:
            voice_client.stop()
            self.queues[ctx.guild.id] = []
            if ctx.guild.id in self.current_songs:
                del self.current_songs[ctx.guild.id]
            await ctx.send("⏹️ Music stopped and queue cleared!")
        else:
            await ctx.send("❌ Not connected to voice!")

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        """Skip the current song"""
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()  # This will trigger play_next
            await ctx.send("⏭️ Song skipped!")
        else:
            await ctx.send("❌ Nothing is playing!")
    
    @commands.command()
    async def previous(self, ctx):
        """Go back to previous song (if available)"""
        # This would require keeping a history - placeholder for now
        await ctx.send("⏮️ Previous song feature coming soon!")

    @commands.command()
    async def clear_queue(self, ctx):
        """Clear the song queue"""
        self.queues[ctx.guild.id] = []
        await ctx.send("🗑️ Queue cleared!")

    @commands.command(aliases=['q'])
    async def queue(self, ctx, page: int = 1):
        """Display the current queue"""
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await ctx.send("📭 Queue is empty!")
            return
        
        items_per_page = 10
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        embed = discord.Embed(title="📝 Music Queue", color=0x0099ff)
        
        for i, song in enumerate(queue[start_idx:end_idx], start=start_idx + 1):
            embed.add_field(
                name=f"{i}. {song.title[:50]}{'...' if len(song.title) > 50 else ''}",
                value=f"Duration: {song.duration} | Requested by: {song.requester.mention}",
                inline=False
            )
        
        total_pages = (len(queue) + items_per_page - 1) // items_per_page
        embed.set_footer(text=f"Page {page}/{total_pages} | Total songs: {len(queue)}")
        
        await ctx.send(embed=embed)

    @commands.command(aliases=['np'])
    async def nowplaying(self, ctx):
        """Display currently playing song"""
        if ctx.guild.id not in self.current_songs:
            await ctx.send("❌ Nothing is playing!")
            return
        
        song = self.current_songs[ctx.guild.id]
        voice_client = self.get_voice_client(ctx.guild)
        
        embed = discord.Embed(title="🎵 Now Playing", color=0x00ff00)
        embed.add_field(name="Song", value=song.title, inline=False)
        embed.add_field(name="Duration", value=song.duration, inline=True)
        embed.add_field(name="Requested by", value=song.requester.mention, inline=True)
        
        if voice_client:
            status = "⏸️ Paused" if voice_client.is_paused() else "▶️ Playing"
            embed.add_field(name="Status", value=status, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def volume(self, ctx, volume: int = None):
        """Set or check the volume (0-100)"""
        if volume is None:
            current_vol = int(self.volumes.get(ctx.guild.id, 0.5) * 100)
            await ctx.send(f"🔊 Current volume: {current_vol}%")
            return
        
        if not 0 <= volume <= 100:
            await ctx.send("❌ Volume must be between 0 and 100!")
            return
        
        self.volumes[ctx.guild.id] = volume / 100.0
        voice_client = self.get_voice_client(ctx.guild)
        
        if voice_client and voice_client.source:
            voice_client.source.volume = volume / 100.0
        
        await ctx.send(f"🔊 Volume set to {volume}%")

    @commands.command()
    async def forward(self, ctx, seconds: int):
        """Fast forward (placeholder - requires ffmpeg seek)"""
        await ctx.send(f"⏩ Fast forward {seconds} seconds feature coming soon!")

    @commands.command()
    async def rewind(self, ctx, seconds: int):
        """Rewind (placeholder - requires ffmpeg seek)"""
        await ctx.send(f"⏪ Rewind {seconds} seconds feature coming soon!")

    @commands.command()
    async def shuffle(self, ctx):
        """Shuffle the current queue"""
        queue = self.get_queue(ctx.guild.id)
        if len(queue) < 2:
            await ctx.send("❌ Need at least 2 songs in queue to shuffle!")
            return
        
        random.shuffle(queue)
        await ctx.send("🔀 Queue shuffled!")

    @commands.command()
    async def search(self, ctx, *, query: str):
        """Search for songs and display results"""
        results = await self.streamer.search_multiple(query, limit=5)
        if not results:
            await ctx.send("❌ No results found!")
            return
        
        embed = discord.Embed(title=f"🔍 Search Results for: {query}", color=0x0099ff)
        
        for i, result in enumerate(results, 1):
            embed.add_field(
                name=f"{i}. {result['title'][:50]}{'...' if len(result['title']) > 50 else ''}",
                value=f"Duration: {result['duration']}",
                inline=False
            )
        
        embed.set_footer(text="Use !play <song name> to play a song")
        await ctx.send(embed=embed)

    # Additional commands
    @commands.command()
    async def loop(self, ctx, mode: str = None):
        """Set loop mode: off, track, queue"""
        pass

    @commands.command()
    async def disconnect(self, ctx):
        """Disconnect from voice channel"""
        pass

    @commands.command()
    async def join(self, ctx):
        """Join your voice channel"""
        pass

    @commands.command()
    async def lyrics(self, ctx, *, song: str = None):
        """Get lyrics for current or specified song"""
        pass

    @commands.command()
    async def autoplay(self, ctx):
        """Toggle autoplay mode"""
        pass

    @commands.command()
    async def history(self, ctx):
        """Show recently played songs"""
        pass

    @commands.command()
    async def remove(self, ctx, index: int):
        """Remove song from queue by index"""
        pass

    @commands.command()
    async def move(self, ctx, from_pos: int, to_pos: int):
        """Move song in queue"""
        pass

    @commands.command()
    async def music_help(self, ctx):
        """Show music commands help"""
        embed = discord.Embed(title="🎵 Music Bot Commands", color=0x0099ff)
        
        playback_cmds = """
        `vplay <song>` - Play a song or add to queue
        `vpause` - Pause current song
        `vresume` - Resume paused song
        `vstop` - Stop music and clear queue
        `vskip` or `vnext` - Skip current song
        `vprevious` - Go to previous song
        `vvolume <0-100>` - Set volume
        `vforward <seconds>` - Fast forward
        `vrewind <seconds>` - Rewind
        """
        
        queue_cmds = """
        `vqueue` or `vq` - Show queue
        `vclear_queue` - Clear queue
        `vshuffle` - Shuffle queue
        `vremove <index>` - Remove song from queue
        `vmove <from> <to>` - Move song in queue
        """
        
        info_cmds = """
        `vnowplaying` or `vnp` - Current song info
        `vsearch <query>` - Search for songs
        `vlyrics [song]` - Get song lyrics
        `vhistory` - Recently played songs
        """
        
        utility_cmds = """
        `vjoin` - Join your voice channel
        `vdisconnect` - Leave voice channel
        `vloop <off/track/queue>` - Set loop mode
        `vautoplay` - Toggle autoplay
        """
        
        embed.add_field(name="🎮 Playback", value=playback_cmds, inline=False)
        embed.add_field(name="📝 Queue Management", value=queue_cmds, inline=False)
        embed.add_field(name="ℹ️ Information", value=info_cmds, inline=False)
        embed.add_field(name="🔧 Utility", value=utility_cmds, inline=False)
        
        embed.set_footer(text="Use !music_help to see this message again")
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Music(client))
    print("Music cog loaded successfully!")