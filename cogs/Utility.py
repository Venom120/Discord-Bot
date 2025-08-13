import discord
from discord.ext import commands
import os
import shutil
import requests

def download_image(url, name, id, times):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
    extension = url[-3:]
    response = requests.get(url, stream=True, headers=headers)
    directory = str(id)
    if (times == 1):
        os.makedirs(f"./emojis/{directory}")
    with open(f"emojis/{directory}/{name}.{extension}", 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def downloademoji(self, ctx):
        print(f"Started downloading by {ctx.author}")
        await ctx.send("Started downloading emojis in local server of the client")
        i = 1
        for guild_s in self.client.guilds:
            if guild_s.id == ctx.guild.id:
                emojis = guild_s.emojis
                for each in emojis:
                    if each.animated:
                        if (i==1):
                            download_image(f"https://cdn.discordapp.com/emojis/{each.id}.gif", str(each.name), ctx.guild.id, 1)
                            i=5
                        else:
                            download_image(f"https://cdn.discordapp.com/emojis/{each.id}.gif", str(each.name), ctx.guild.id, 2)
                    else:
                        if (i==1):
                            download_image(f"https://cdn.discordapp.com/emojis/{each.id}.png", str(each.name), ctx.guild.id, 1)
                            i=5
                        else:
                            download_image(f"https://cdn.discordapp.com/emojis/{each.id}.png", str(each.name), ctx.guild.id, 2)
                print("Finished")
                await ctx.send("Finished downloading this servers emoji")
            else:
                continue
    @downloademoji.error
    async def downloademoji_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def uploademoji(self, ctx, g_id: int, number: int):
        guild = discord.utils.get(self.client.guilds, id=int(g_id))
        await ctx.send("Started uploading emojis to this server from entered server id")
        try:
            async with ctx.typing():
                path = "./emojis"
                image = os.listdir(path)
                if str(g_id) in image:
                    path = f"./emojis/{str(g_id)}"
                    images = os.listdir(path)
                    # length = len(images)
                    length = number-1
                    all = []
                    for i in range(length):
                        with open(f'{path}/{images[i]}', 'rb') as emoji_file:
                            emoji_bytes = emoji_file.read()
                        emoji = await ctx.guild.create_custom_emoji(name=images[i][:-4], image=emoji_bytes)
                        all.append(emoji.name)
                    await ctx.send(f'Emoji {all} uploaded!')
                    await ctx.send("Finished uploading emojis")
                else:
                    print("not found")
        except Exception as e:
            print(e)
            await ctx.send(f'Error: {e}')
    @uploademoji.error
    async def uploademoji_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify guild_id/number to download emojis from.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")

async def setup(client):
    await client.add_cog(Utility(client))
