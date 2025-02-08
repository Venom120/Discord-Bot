import discord
from discord.ext import commands
import random
import os
import asyncio
from keep_alive import keep_alive
import time
import aiofiles
import requests
import shutil

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx = self.context
        em = discord.Embed(
            title="**All commands will be shown here**",
            description="To see more about a command use vhelp <command_name>",
            color=discord.Color.red()
        )
        em.set_author(name="HELP COMMANDS")
        em.add_field(
            name="**MISC COMMANDS**",
            value="1.timer \n2.hi \n3.emb \n4.ping \n5.textspam \n6.poll \n7.roll"
        )
        em.add_field(
            name="**MODERATION COMMANDS**",
            value="1.kick \n2.ban \n3.unban \n4.purge \n5.mute \n6.unmute \n7.lock \n8.unlock \n9.warn \n10.warnings"
        )
        await self.get_destination().send(embed=em)

    async def send_command_help(self, command):
        if command.qualified_name.lower() == "timer":
            embed=discord.Embed(
            title="**TIMER**",
            description=" it is a command to run countdowns",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value="vtimer <seconds> \nvtimer 20"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "hi" or command.qualified_name.lower() == "hello" or command.qualified_name.lower() == "hey" or command.qualified_name.lower() == "heyy":
            embed=discord.Embed(
            title="**HI**",
            description="It says HELLO! to you",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value="vhi \nvhello \nvHI \nvHello"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "emb" or command.qualified_name.lower() == "embed":
            embed=discord.Embed(
            title="**emb**",
            description="It send you a embed message",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value="vemb hi \nvemb hello \nvemb HI \nvemb bye"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "ping":
            embed=discord.Embed(
            title="**ping**",
            description="It gives the Latency of your ip",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value="vping"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "textspam" or command.qualified_name.lower() == "ts":
            embed=discord.Embed(
            title="**TEXTSPAM**",
            description=" it is a command in which bot spam a text",
            color=discord.Color.red()
            ) 
            embed.add_field(name="Aliases", value="vts")
            embed.add_field(
            name="Examples->", value="vtextspam <number of times> <text> , \nvtextspam 10 hi \nvtextspam 2 hello \nvts 6 hi"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "kick" or command.qualified_name.lower() == "k":
            embed=discord.Embed(
            title="**kick**",
            description=" it is a command used to kick user",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vk")
            embed.add_field(
            name="Examples->", value="vkick <mention user> <reason>, \nvkick @venom#1234 idk \nvk @venom#1111 idk")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "ban" or command.qualified_name.lower() == "b":
            embed=discord.Embed(
            title="**ban**",
            description=" it is a command used to ban user ",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="v!b")
            embed.add_field(
            name="Examples->", value="vban <mention user> <reason>, \nvban @venom#1234 idk \nvb @venom#1111 idk")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "unban" or command.qualified_name.lower() == "ub":
            embed=discord.Embed(
            title="**unban**",
            description=" it is a command used to unban user ",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vub")
            embed.add_field(
            name="Examples->", value="vunban <mention user> , \nv!unban venom#1234 \nvub venom#1111")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "purge" or command.qualified_name.lower() == "p":
            embed=discord.Embed(
            title="**purge**",
            description=" it is a command used to purge messages",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vp")
            embed.add_field(
            name="Examples->", value="vpurge <number of messages> , \nvpurge 5 \nvp 10")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "mute" or command.qualified_name.lower() == "m":
            embed=discord.Embed(
            title="**MUTE**",
            description="it mutes the member",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vm")
            embed.add_field(
            name="Examples->", value="vmute <user> <reason> \nvmute @venom#2341 idk \nvmute @venom120#1234 idk\nvm @venom#9876 idk"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "unmute" or command.qualified_name.lower() == "um":
            embed=discord.Embed(
            title="**UNMUTE**",
            description="it unmutes the member",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vum")
            embed.add_field(
            name="Examples->", value="v!unmute <user> \nvmute @venom#2341 idk \nvunmute @venom120#1234 idk\nvum @venom#9876 idk"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "lock" or command.qualified_name.lower() == "l":
            embed=discord.Embed(
            title="**LOCK CHANNEL**",
            description="it locks the current channel",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vl")
            embed.add_field(
            name="Examples->", value="vlock \nvl"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "unlock" or command.qualified_name.lower() == "ul":
            embed=discord.Embed(
            title="**UNLOCK CHANNEL**",
            description="it unlocks the current channel",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vun")
            embed.add_field(
            name="Examples->", value="vunlock \nvul "
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "warn":
            embed=discord.Embed(
            title="**WARN**",
            description="it warn the respective user",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value="vwarn <mention user> <reason>,\nvwarn @venom120#8673 idk \nvwarn @venom129#2832 idk"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "warnings" or command.qualified_name.lower() == "warns":
            embed=discord.Embed(
            title="**WARNINGS**",
            description="it shows the number of warns user has!",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="vwarning \nvwarns")
            embed.add_field(
            name="Examples->", value="vwarnings @venom120#8673 \nvwarning @carnage#2832 \nvwarns @spiderman#4926"
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "poll":
            embed=discord.Embed(
            title="**POLL**",
            description="it helps you to create poll",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value='vpoll <time in minutes> <number of option> <title in " "> <every option names with spaces> \nvpoll 1 2 "example" yes no \nvpoll 2 2 "is server good" yes no \nvpoll 15 1 "is venom op?" yes'
            )
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "roll":
            embed=discord.Embed(
            title="**ROLL**",
            description="It will generate a random rumber between 1 and number inputted.",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value='vroll <number> \nvroll 1000 \nvroll 50'
            )
            await self.get_destination().send(embed=embed)
        else:
                await self.get_destination().send("command not found!")


intents = discord.Intents.all()
client = commands.Bot(
    command_prefix=commands.when_mentioned_or('v','V','v ','V '),
    help_command=CustomHelpCommand(),
    insensitive=True,
    intents=intents
)
commands.warnings = {}

@client.event
async def on_ready():
    try:
        for guild in client.guilds:
            commands.warnings[guild.id] = {}
            async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
                pass
            async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
                lines = await file.readlines()
                for line in lines:
                    data = line.split(" ")
                    member_id = int(data[0])
                    admin_id = int(data[1])
                    warnings_id = int(data[2])
                    reason = " ".join(data[3:]).strip("\n")
                    try:
                        commands.warnings[guild.id][member_id][0] += 1
                        commands.warnings[guild.id][member_id][1].append((admin_id, warnings_id, reason))
                    except KeyError:
                        commands.warnings[guild.id][member_id] = [1, [(admin_id, warnings_id, reason)]]
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


@client.command()
async def timer(ctx, seconds: int):
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


@client.command(aliases=["hola", "heloo", "hello", "Hello", "HELLO"])
async def hi(ctx):
    await ctx.send("HELLO there!!!!")


@client.command(pass_context=True)
async def ping(ctx):
    before = time.monotonic()
    message = await ctx.send("pong!")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f"pong! {int(ping)}ms")


@client.command()
async def emb(ctx, *, msg):
    message_text = msg
    embed = discord.Embed(
        title=f"{ctx.author} says:",
        description=f"***{message_text}***",
        color=discord.Color.red(),
    )
    await ctx.channel.purge(limit=1)
    await ctx.send(embed=embed)


@client.command()
async def roll(ctx, number1: int, number2=-2):
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
async def roll_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("**```Please specify number to roll.```**")


@client.command(aliases=["ts", "TS", "Ts", "tS"])
async def textspam(ctx, repeat: int, *, text: str):
    if (
        ctx.channel.id == 898443548054126623
        or ctx.channel.id == 893884496296935445
        or ctx.channel.id == 893884430668693584
        or ctx.channel.id == 882471280039829515
    ):
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
                time.sleep(0.7)
        elif repeat < 0:
            await ctx.send("you dumbo i can't send number of text in negatives")
        elif repeat > 10:
            await ctx.send("not allowed to spam more than 10 text")
        else:
            await ctx.send("error!")
    else:
        await ctx.send("not allowed to use this command here!")
@textspam.error
async def textspam_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("please specify text/number to spam.")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")


@client.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member = None, *, reason=None):
    if member is None:
        return await ctx.send(
            "The provided member could not be found or you forgot to provide one."
        )
    if reason is None:
        return await ctx.send("Please provide a reason for warning this user.")
    try:
        first_warning = False
        warn_id = commands.warnings[ctx.guild.id][member.id][1][-1][1] + 1 
        commands.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, warn_id, reason))
        commands.warnings[ctx.guild.id][member.id][0] += 1
    except KeyError:
        first_warning = True
        warn_id = 1
        commands.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, warn_id, reason)]]
    try:
        count = commands.warnings[ctx.guild.id][member.id][0]
        async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
            await file.write(f"{member.id} {ctx.author.id} {warn_id} {reason}\n")
        await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")
    except Exception as e:
        await ctx.send(f"{e}\nContact Venom_120")
@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
    if isinstance(error, commands.BadArgument):
        await ctx.send("User not found!!")


@client.command(aliases=["warning", "warns"])
@commands.has_permissions(kick_members=True)
async def warnings(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send(
            "The provided member could not be found or you forgot to provide one.")
    embed = discord.Embed(
        title=f"Displaying Warnings for {member}",
        description="",
        colour=discord.Colour.red(),
    )
    try:
        for admin_id, warning_id, reason in commands.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warning {warning_id}** given by: {admin}, for: **'{reason}'**\n"
        embed.description += f"Total {len(commands.warnings[ctx.guild.id][member.id][1])} Warnings"
        await ctx.send(embed=embed)
    except IndexError:
        return await ctx.send("No warnings on this user!")
    except KeyError:  # no warnings
        await ctx.send("This user has no warnings.")
    except Exception as e:
        await ctx.send(f"{e}\nCOntact Venom_120")
@warnings.error
async def warnings_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
    if isinstance(error, commands.BadArgument):
        await ctx.send("User not found!!")


@client.command(aliases=["delwarn","delwarns","dwarn","dwarns","dw"])
@commands.has_permissions(kick_members=True)
async def deletewarn(ctx, member: discord.Member = None, id = None):
    if member is None:
        return await ctx.send("The provided member could not be found or you forgot to provide one.")
    if id is None:
        return await ctx.send("Please provide a warning id to delete.")
    if str(id) == "all":
        commands.warnings[ctx.guild.id][member.id] = []
        async with aiofiles.open(f"{ctx.guild.id}.txt", mode="w") as file:
            await file.write("")
        return await ctx.send(f"Deleted all warnings from {member}.")
    try:
        async with aiofiles.open(f"{ctx.guild.id}.txt", mode="w") as file:
            for x in commands.warnings[ctx.guild.id][member.id][1]:
                if str(x[1]) == str(id):                
                    commands.warnings[ctx.guild.id][member.id][0] -= 1
                    for y in commands.warnings[ctx.guild.id][member.id][1]:
                        if str(y[1]) == str(id):
                            commands.warnings[ctx.guild.id][member.id][1].remove((y))
                    return await ctx.send(f"Deleted warning id - {int(id)} from {member}.")
                else:
                    await file.write(f"{member.id} {x[0]} {x[1]} {x[2]}\n")
            await ctx.send("Entered id not found")
    except IndexError:
        return await ctx.send("No warnings on this user!")
    except KeyError:
        return await ctx.send("No warnings on this user!")
    except Exception as e:
        return await ctx.send(f"{e}\nContact Venom_120")
@deletewarn.error
async def deletewarn_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
    if isinstance(error, commands.BadArgument):
        await ctx.send("User not found!!")


def download_image(url, name, id, times):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36'}
    extension = url[-3:]
    response = requests.get(url, stream=True, headers=headers)
    directory = str(id)
    if (times == 1):
        os.makedirs(f"./emojis/{directory}")
    with open(f"emojis/{directory}/{name}.{extension}", 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
@client.command()
@commands.has_permissions(administrator=True)
async def downloademoji(ctx):
    print(f"Started downloading by {ctx.author}")
    await ctx.send("Started downloading emojis in local server of the bot")
    i = 1
    for guild_s in client.guilds:
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
async def downloademoji_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")


@client.command()
@commands.has_permissions(administrator=True)
async def uploademoji(ctx, g_id: int, number: int):
    guild = discord.utils.get(client.guilds, id=int(g_id))
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
async def uploademoji_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("please specify guild_id/number to download emojis from.")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!!.")






extensions = ["cogs.Moderation", "cogs.Poll","cogs.WelcomeLeave"]
async def load_extensions():
    for extension in extensions:
        try:
            await client.load_extension(extension)
        except Exception as e:
            print(f"{extension} not Loaded\n{e}")
async def main():
    async with client:
        keep_alive()
        my_secret = os.environ["TOKEN"]
        # my_secret = ""
        await load_extensions()
        await client.start(my_secret)



asyncio.run(main())