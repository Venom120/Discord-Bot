import json
import discord
import asyncio
import random
from datetime import datetime
from discord.ext import commands, tasks
from .music_streamer import MusicStreamer, Song

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.streamer = MusicStreamer()
        self.queues = {}  # Guild-specific queues
        self.current_songs = {}  # Currently playing songs per guild
        self.voice_clients = {}  # Voice clients per guild
        self.loop_modes = {}  # Loop modes: 0=off, 1=track, 2=queue
        self.volumes = {}  # Volume levels per guild (default 0.5)
        self.skip_override_loop = {} # Flag to make skip command ignore loop track

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
        
        # Check bot permissions
        permissions = channel.permissions_for(ctx.guild.me)
        if not permissions.connect or not permissions.speak:
            await ctx.send("❌ I don't have permission to join/speak in that voice channel!")
            return None
        
        try:
            if ctx.guild.id in self.voice_clients:
                voice_client = self.voice_clients[ctx.guild.id]
                if voice_client.channel != channel:
                    await voice_client.move_to(channel)
                    await ctx.send(f"🔄 Moved to **{channel.name}**")
            else:
                voice_client = await channel.connect()
                self.voice_clients[ctx.guild.id] = voice_client
                await ctx.send(f"✅ Connected to **{channel.name}**")
            
            return voice_client
            
        except discord.ClientException as e:
            await ctx.send(f"❌ Failed to connect to voice channel: {str(e)}")
            return None
        except asyncio.TimeoutError:
            await ctx.send("❌ Timeout while trying to connect to voice channel!")
            return None

    async def play_next(self, ctx):
        """Play the next song in queue"""
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        voice_client = self.get_voice_client(ctx.guild)
        

        if not queue and not (self.loop_modes.get(guild_id, 0) == 1 and guild_id in self.current_songs):
            # If queue is empty and not looping current track, clear current_song and return
            if guild_id in self.current_songs: # Only clear if it was set
                del self.current_songs[guild_id]
            await ctx.send("🎶 Queue finished!")
            return # No more songs to play

        if not voice_client:
            return
        
        # Handle loop modes
        loop_mode = self.loop_modes.get(guild_id, 0)
        next_song = None

        # Check for skip override
        is_skip_override = self.skip_override_loop.pop(guild_id, False)
        if is_skip_override and loop_mode == 1:
            print(f"DEBUG: Skip override active. Temporarily ignoring loop track for guild {guild_id}.")
            loop_mode = 0 # Treat as normal play for this instance

        if loop_mode == 1:  # Loop track
            if guild_id in self.current_songs:
                next_song = self.current_songs[guild_id]
            else:
                if queue:
                    next_song = queue.pop(0)
                else:
                    # Should not happen if play command correctly puts first song in current_songs
                    return
        elif loop_mode == 2:  # Loop queue
            if queue:
                next_song = queue.pop(0)
                queue.append(next_song)  # Add back to end
            else:
                return
        else:  # Normal play (loop_mode == 0)
            if queue:
                next_song = queue.pop(0)
            else:
                return

        if next_song: # Ensure next_song is not None before proceeding
            self.current_songs[guild_id] = next_song
        else:
            return
        
        # Get audio source
        audio_source = await self.streamer.get_audio_source(next_song.url)
        if not audio_source:
            await ctx.send(f"❌ Failed to play: {next_song.title}")
            # If playback fails, try the next song in the queue (or exit if looping current)
            if loop_mode == 1: # If current track failed, stop looping it and try next from queue
                del self.current_songs[guild_id]
                if queue: await self.play_next(ctx)
                else: await ctx.send("Queue empty after failed track loop.")
                return
            else: # For normal play or queue loop, just try next song
                await self.play_next(ctx)
            return
        
        # Set volume
        volume = self.volumes.get(guild_id, 0.5)
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=volume)
        
        # Play the song
        def after_playing(error):
            if error:
                # Schedule ctx.send to run in the bot's event loop
                asyncio.run_coroutine_threadsafe(ctx.send(f'Player error in after_playing: {error}'), self.client.loop)
            # Use self.client.loop to ensure coroutine runs in bot's event loop
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.client.loop)
        
        voice_client.play(audio_source, after=after_playing)
        
        embed = discord.Embed(title="🎵 Now Playing", color=0x00ff00)
        embed.add_field(name="Song", value=next_song.title, inline=False)
        embed.add_field(name="Duration", value=next_song.duration, inline=True)
        embed.add_field(name="Requested by", value=next_song.requester.mention, inline=True)
        embed.add_field(name="Loop Mode", value={0: "Off", 1: "Track", 2: "Queue"}[loop_mode], inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def play(self, ctx, *, song: str):
        """Play a song or add it to queue"""
        # Check if user is in voice channel
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel to play music!")
            return
            
        voice_client = await self.join_voice_channel(ctx)
        if not voice_client:
            return
        
        # Send searching message
        search_msg = await ctx.send(f"🔍 Searching for: `{song}`")
        
        try:
            # Search for the song using the new process_query
            # process_query returns a list of Song objects
            songs_found = await self.streamer.process_query(song, ctx.author)
            
            if not songs_found:
                await search_msg.edit(content="❌ No results found! Try a different search term.")
                return
            
            # Handle single song or playlist
            is_playlist = len(songs_found) > 1
            first_song_obj = songs_found[0]
            queue = self.get_queue(ctx.guild.id)

            if not voice_client.is_playing() and not voice_client.is_paused():
                # If nothing is playing, the first song is the 'current' song and we initiate playback
                queue.insert(0, first_song_obj) # Add to front so play_next plays it
                if is_playlist: # Add the rest of the playlist after the first song
                    queue.extend(songs_found[1:])
                await search_msg.edit(content="🎵 Loading audio...")
                await self.play_next(ctx)
                if is_playlist: # Send playlist added embed after playback starts
                    embed = discord.Embed(title="📝 Playlist Added to Queue", color=0x0099ff)
                    embed.add_field(name="Playlist Size", value=f"{len(songs_found)} songs", inline=False)
                    embed.add_field(name="First Song", value=first_song_obj.title, inline=True)
                    embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                    await ctx.send(embed=embed) # Send in a new message, not edit search_msg
            else:
                # If something is already playing, add all found songs to the end of the queue
                queue.extend(songs_found) # Add all songs found (single or playlist)
                
                if is_playlist:
                    embed = discord.Embed(title="📝 Playlist Added to Queue", color=0x0099ff)
                    embed.add_field(name="Playlist Size", value=f"{len(songs_found)} songs", inline=False)
                    embed.add_field(name="First Song", value=first_song_obj.title, inline=True)
                else:
                    embed = discord.Embed(title="📝 Added to Queue", color=0x0099ff)
                    embed.add_field(name="Song", value=first_song_obj.title, inline=False)
                
                embed.add_field(name="Position", value=f"{len(queue)}", inline=True)
                embed.add_field(name="Duration", value=first_song_obj.duration, inline=True)
                embed.add_field(name="Requested by", value=first_song_obj.requester.mention, inline=True)
                await search_msg.edit(content="", embed=embed)
            
        except Exception as e:
            await search_msg.edit(content=f"❌ An error occurred: {str(e)}")
            print(f"Play command error: {e}")
            import traceback
            traceback.print_exc()

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
            guild_id = ctx.guild.id
            if self.loop_modes.get(guild_id, 0) == 1: # If looping current track
                self.skip_override_loop[guild_id] = True # Set flag to ignore loop for this skip
            
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
        guild_id = ctx.guild.id
        queue = self.get_queue(guild_id)
        current_song = self.current_songs.get(guild_id)
        
        embed = discord.Embed(title="📝 Music Queue", color=0x0099ff)
        
        # Display currently playing song
        if current_song:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**[{current_song.title}]({current_song.url})** | Duration: {current_song.duration} | Requested by: {current_song.requester.mention}",
                inline=False
            )
        
        if not queue and not current_song:
            await ctx.send("📭 Queue is empty! Nothing is playing.")
            return

        # Display upcoming songs
        if queue:
            items_per_page = 10
            # If current song is displayed, start indexing from 0 for queue, otherwise from page 1
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            
            # Use a list slice to get songs for the current page
            display_queue = queue[start_idx:end_idx]

            if not display_queue:
                await ctx.send(f"📭 Page {page} of queue is empty.")
                return

            # Add a field for upcoming songs only if there are any
            if current_song:
                embed.add_field(name="Upcoming Songs", value="** **", inline=False) # Spacer

            for i, song in enumerate(display_queue, start=start_idx + 1):
                embed.add_field(
                    name=f"{i}. {song.title[:50]}{'...' if len(song.title) > 50 else ''}",
                    value=f"Duration: {song.duration} | Requested by: {song.requester.mention}",
                    inline=False
                )
            
            total_pages = (len(queue) + items_per_page - 1) // items_per_page
            # Adjust page number display based on whether current song is shown as part of the queue or separately
            footer_text = f"Page {page}/{total_pages} | Total songs in queue: {len(queue)}"
            if current_song and not queue: # Only current song, no queue
                footer_text = "" # No pages if only one song playing and no queue
            elif current_song: # Current song + queue
                footer_text = f"Queue Page {page}/{total_pages} | Total songs in queue: {len(queue)}"
            
            if footer_text: # Only set footer if there's text
                embed.set_footer(text=footer_text)
        else:
            # If there's a current song but no queue, ensure the embed is sent
            if current_song and not embed.fields:
                # This case is handled by the first if block for current_song
                pass
            elif not current_song and not queue:
                await ctx.send("📭 Queue is empty! Nothing is playing.")
                return
            
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
        
        embed.set_footer(text="Use `vplay <song name>` to play a song")
        await ctx.send(embed=embed)

    # Additional commands
    @commands.command()
    async def loop(self, ctx, mode: str = None):
        """Set loop mode: off, track, queue"""
        guild_id = ctx.guild.id
        if mode is None:
            current_mode = self.loop_modes.get(guild_id, 0)
            modes = {0: "Off", 1: "Track", 2: "Queue"}
            await ctx.send(f"🔄 Current loop mode: **{modes[current_mode]}**")
            return
        
        mode = mode.lower()
        if mode in ['off', '0', 'none']:
            self.loop_modes[guild_id] = 0
            await ctx.send("🔄 Loop mode set to: **Off**")
        elif mode in ['track', '1', 'song']:
            self.loop_modes[guild_id] = 1
            await ctx.send("🔄 Loop mode set to: **Track**")
        elif mode in ['queue', '2', 'all']:
            self.loop_modes[guild_id] = 2
            await ctx.send("🔄 Loop mode set to: **Queue**")
        else:
            await ctx.send("❌ Invalid loop mode! Use: `off`, `track`, or `queue`")

    @commands.command(aliases=['leave', 'dc'])
    async def disconnect(self, ctx):
        """Disconnect from voice channel"""
        voice_client = self.get_voice_client(ctx.guild)
        if voice_client:
            await voice_client.disconnect()
            if ctx.guild.id in self.voice_clients:
                del self.voice_clients[ctx.guild.id]
            if ctx.guild.id in self.current_songs:
                del self.current_songs[ctx.guild.id]
            self.queues[ctx.guild.id] = []
            await ctx.send("👋 Disconnected from voice channel!")
        else:
            await ctx.send("❌ Not connected to any voice channel!")

    @commands.command()
    async def join(self, ctx):
        """Join your voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel!")
            return
        
        voice_client = await self.join_voice_channel(ctx)
        if voice_client:
            await ctx.send(f"✅ Joined **{ctx.author.voice.channel.name}**!")

    @commands.command()
    async def lyrics(self, ctx, *, song: str = None):
        """Get lyrics for current or specified song"""
        if song is None:
            if ctx.guild.id in self.current_songs:
                song = self.current_songs[ctx.guild.id].title
            else:
                await ctx.send("❌ No song is currently playing! Specify a song name.")
                return
        
        # Placeholder - you can implement lyrics API integration
        await ctx.send(f"🎵 Lyrics search for **{song}** is coming soon!\n"
                      "You can implement this using services like:\n"
                      "• Genius API\n• AZLyrics scraping\n• LyricFind API")

    @commands.command()
    async def autoplay(self, ctx):
        """Toggle autoplay mode"""
        # Placeholder for autoplay functionality
        await ctx.send("🎲 Autoplay feature coming soon!\n"
                      "This will automatically add related songs when the queue is empty.")

    @commands.command()
    async def history(self, ctx, limit: int = 10):
        """Show recently played songs"""
        # Placeholder - you would need to implement song history tracking
        await ctx.send(f"📜 Song history (last {limit} songs) feature coming soon!\n"
                      "This will show recently played tracks.")

    @commands.command()
    async def remove(self, ctx, index: int):
        """Remove song from queue by index"""
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await ctx.send("❌ Queue is empty!")
            return
        
        if index < 1 or index > len(queue):
            await ctx.send(f"❌ Invalid index! Use a number between 1 and {len(queue)}")
            return
        
        removed_song = queue.pop(index - 1)
        await ctx.send(f"🗑️ Removed **{removed_song.title}** from queue!")

    @commands.command()
    async def move(self, ctx, from_pos: int, to_pos: int):
        """Move song in queue"""
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await ctx.send("❌ Queue is empty!")
            return
        
        if from_pos < 1 or from_pos > len(queue) or to_pos < 1 or to_pos > len(queue):
            await ctx.send(f"❌ Invalid position! Use numbers between 1 and {len(queue)}")
            return
        
        # Convert to 0-based indexing
        from_idx = from_pos - 1
        to_idx = to_pos - 1
        
        # Move the song
        song = queue.pop(from_idx)
        queue.insert(to_idx, song)
        
        await ctx.send(f"✅ Moved **{song.title}** from position {from_pos} to {to_pos}!")
        
async def setup(client):
    await client.add_cog(Music(client))
    print("Music cog loaded successfully!")