import discord
from discord.ext import commands
import asyncio
import random

class General(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def timer(self, ctx, seconds: int):
        """
        It is a command to run countdowns
        Examples->
        vtimer <seconds> 
        vtimer 20
        """
        try:
            secondint = int(seconds)
            if secondint <= 0:
                await ctx.send("I don't think I can do negatives")
            message = await ctx.send(f"Timer: {seconds}")
            while True:
                secondint -= 1
                if secondint == 0:
                    await message.edit(content="ended!")
                    break
                await message.edit(content=f"Timer: {secondint}")
                await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention}, Your countdown has been ended!")
        except ValueError:
            await ctx.send("You must enter a number!")

    @commands.command(aliases=["hola", "heloo", "hello", "Hello", "HELLO"])
    async def hi(self, ctx):
        await ctx.send("HELLO there!!!!")

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        before = discord.utils.utcnow().timestamp()
        message = await ctx.send("pong!")
        ping = (discord.utils.utcnow().timestamp() - before) * 1000
        await message.edit(content=f"pong! {int(ping)}ms")

    @commands.command()
    async def emb(self, ctx, *, msg):
        message_text = msg
        embed = discord.Embed(
            title=f"{ctx.author} says:",
            description=f"***{message_text}***",
            color=discord.Color.red(),
        )
        await ctx.channel.purge(limit=1)
        await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, number1: int, number2=-2):
        if number2 == -2:
            if number1 > 0:
                total = []
                for i in range(1, number1 + 1):
                    total.append(i)
                await ctx.send(total[random.randint(0, number1)])
            elif number1 == 0:
                await ctx.send("0")
            else:
                await ctx.send("Can't do negatives")
        elif number1 > number2:
            total = []
            for i in range(number2, number1 + 1):
                total.append(i)
            await ctx.send(total[random.randint(0, number1 - number2)])
        elif number1 == 0:
            total = [
                0,
            ]
            for i in range(number2 + 1):
                total.append(i)
            await ctx.send(total[random.randint(0, number2 + 1)])
        else:
            total = []
            for i in range(number1, number2 + 1):
                total.append(i)
            await ctx.send(total[random.randint(0, number2 - number1)])
    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("**```Please specify number to roll.```**")

    @commands.command(aliases=["ts", "TS", "Ts", "tS"])
    async def textspam(self, ctx, repeat: int, *, text: str):
        # Access allowed channels from the Setting cog
        setting_cog = self.client.get_cog('Settings')
        if setting_cog and ctx.guild and ctx.channel.id not in setting_cog.allowed_channels_per_guild.get(ctx.guild.id, []):
            return await ctx.send(f"This command can only be used in allowed channels. Please use `vsetting textspam <#channel> <add|remove>` to manage them.")

        z = ""
        skip1c = 0
        for i in text:
            if i == "<":
                skip1c += 1
            elif i == ">":
                skip1c -= 1
            elif skip1c == 0:
                z += i
        if repeat > 0 and repeat <= 10:
            for i in range(1, repeat + 1):
                await ctx.send(z)
                await asyncio.sleep(0.7)
        elif repeat < 0:
            await ctx.send("you dumbo i can't send number of text in negatives")
        elif repeat > 10:
            await ctx.send("not allowed to spam more than 10 text")
        else:
            await ctx.send("error!")
    @textspam.error
    async def textspam_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify text/number to spam.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")

async def setup(client):
    await client.add_cog(General(client))
