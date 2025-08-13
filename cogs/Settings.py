import discord
from discord.ext import commands
import json
import aiofiles

ALLOWED_CHANNELS_FILE = 'allowed_textspam_channels.json'

class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.allowed_channels_per_guild = self.load_allowed_channels()

    def load_allowed_channels(self):
        try:
            with open(ALLOWED_CHANNELS_FILE, 'r') as f:
                data = json.load(f)
                # Convert keys to integers for guild IDs
                return {int(k): v for k, v in data.items()}
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding {ALLOWED_CHANNELS_FILE}. Starting with empty dictionary.")
            return {}

    async def save_allowed_channels(self):
        async with aiofiles.open(ALLOWED_CHANNELS_FILE, 'w') as f:
            # Convert integer keys back to strings for JSON serialization
            await f.write(json.dumps({str(k): v for k, v in self.allowed_channels_per_guild.items()}, indent=4))

    @commands.group(invoke_without_command=True)
    async def settings(self, ctx):
        await ctx.send("Please specify a setting to modify. Usage: `vsettings textspam <add|remove> <channel>`")

    @settings.command(name='textspam', aliases=["ts", "TS", "Ts", "tS"])
    @commands.has_permissions(manage_channels=True)
    async def settings_textspam(self, ctx, action: str = None, channel: discord.TextChannel = None):
        """
        Allows or disallows textspam command in a channel.
        Usage: vsettings textspam <add|remove> <#channel>
        Examples: vsettings textspam remove #general, vsettings textspam add #spam
        """
        if channel is None or action is None:
            return await ctx.send("Please specify a channel and an action (add/remove). Usage: `vsettings textspam <add|remove> <#channel>`")

        action = action.lower()
        guild_id = ctx.guild.id
        channel_id = channel.id

        if guild_id not in self.allowed_channels_per_guild:
            self.allowed_channels_per_guild[guild_id] = []

        if action == 'add':
            if channel_id not in self.allowed_channels_per_guild[guild_id]:
                self.allowed_channels_per_guild[guild_id].append(channel_id)
                await self.save_allowed_channels()
                await ctx.send(f"Added {channel.mention} to the allowlist for textspam in this guild.")
            else:
                await ctx.send(f"{channel.mention} is already in the allowlist for this guild.")
        elif action == 'remove':
            if channel_id in self.allowed_channels_per_guild[guild_id]:
                self.allowed_channels_per_guild[guild_id].remove(channel_id)
                await self.save_allowed_channels()
                await ctx.send(f"Removed {channel.mention} from the allowlist for textspam in this guild.")
            else:
                await ctx.send(f"{channel.mention} is not in the allowlist for this guild.")
        else:
            await ctx.send("Invalid action. Please use 'add' or 'remove'.")

    @settings_textspam.error
    async def settings_textspam_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Could not find that channel. Please mention the channel (e.g., #general).")
        else:
            print(f"Error in settings_textspam: {error}")
            await ctx.send("An error occurred while processing your request.")

async def setup(client):
    await client.add_cog(Settings(client))
