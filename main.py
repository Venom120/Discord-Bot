import discord
from discord.ext import commands
import os,json,aiofiles,asyncio
from keep_alive import keep_alive
from cogs.Help import CustomHelpCommand

secrets_path = "secrets.json" # Path to your secrets.json file (which contains the token)



intents = discord.Intents.all()
client = commands.Bot(
    command_prefix=commands.when_mentioned_or("v","V","v ","V "),
    help_command=CustomHelpCommand(), # Assign the custom help command here
    insensitive=True,
    intents=intents
)

@client.event
async def on_ready():
    try:
        for guild in client.guilds:
            async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
                pass
        print(client.user.name + " is ready.")
    except Exception as e:
        print(e)

@client.event
async def on_guild_join(guild):
    client.warnings[guild.id] = {}

@client.event
async def on_member_join(ctx):
    role1 = ctx.guild.get_role(893886494371106937)
    await ctx.add_roles(role1)
    role2 = ctx.guild.get_role(893885617514086482)
    await ctx.add_roles(role2)
    role3 = ctx.guild.get_role(893888258205974648)
    await ctx.add_roles(role3)
    role4 = ctx.guild.get_role(893888256863772713)
    await ctx.add_roles(role4)
    role5 = ctx.guild.get_role(893906974566154261)
    await ctx.add_roles(role5)
    role6 = ctx.guild.get_role(893885822280032256)
    await ctx.add_roles(role6)
    role7 = ctx.guild.get_role(893886175285215272)
    await ctx.add_roles(role7)
    role8 = ctx.guild.get_role(893886650558603264)
    await ctx.add_roles(role8)
    role9 = ctx.guild.get_role(898263877874229299)
    await ctx.add_roles(role9)


extensions = ["cogs.Moderation", "cogs.Poll","cogs.WelcomeLeave", "cogs.music.Music", "cogs.General", "cogs.Utility", "cogs.Settings"]
async def load_extensions():
    for extension in extensions:
        try:
            await client.load_extension(extension)
        except Exception as e:
            print(f"{extension} not Loaded\n{e}")
async def main():
    async with client:
        keep_alive()
        # Load the token from the JSON file
        with open(secrets_path, "r") as file:
            config = json.load(file)
            my_secret = config["DISCORD_TOKEN"]
        await load_extensions()
        await client.start(my_secret)

asyncio.run(main())