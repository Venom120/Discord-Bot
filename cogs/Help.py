import discord
from discord.ext import commands

class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        ctx = self.context
        em = discord.Embed(
            title="**All commands will be shown here**",
            description="To see more about a command use vhelp <command_name>",
            color=discord.Color.blue() # Changed color to blue
        )
        em.set_author(name="HELP COMMANDS", icon_url=self.context.bot.user.avatar.url)
        em.add_field(
            name="__**MISC COMMANDS**__",
            value="`1.timer` \n`2.hi` \n`3.emb` \n`4.ping` \n`5.textspam` \n`6.poll` \n`7.roll` \n`8.music`",
            inline=False # Ensure field takes full width
        )
        em.add_field(
            name="__**MODERATION COMMANDS**__",
            value="`1.kick` \n`2.ban` \n`3.unban` \n`4.purge` \n`5.mute` \n`6.unmute` \n`7.lock` \n`8.unlock` \n`9.warn` \n`10.warnings`",
            inline=False # Ensure field takes full width
        )
        em.add_field(
            name="__**SETTINGS COMMANDS**__",
            value="`1.settings`",
            inline=False # Ensure field takes full width
        )
        em.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
        em.timestamp = discord.utils.utcnow() # Add timestamp
        await self.get_destination().send(embed=em)

    async def send_group_help(self, group):
        """Handle help for group commands like 'settings'"""

        if group.qualified_name.lower() == "settings":
            embed = discord.Embed(
                title="**SETTINGS**",
                description="Base command for bot settings. Use `vhelp settings <subcommand>` for more details.",
                color=discord.Color.dark_purple()
            )
            subcommands_list = []
            for sub_cmd in group.commands:
                brief_description = (sub_cmd.help.splitlines()[0] if sub_cmd.help else "No description provided.")
                subcommands_list.append(f"`{sub_cmd.name}` - {brief_description}")
            
            if subcommands_list:
                embed.add_field(name="Subcommands:", value="\n".join(subcommands_list), inline=False)
            else:
                embed.add_field(name="Subcommands:", value="No subcommands available.", inline=False)
            
            embed.set_footer(text="Category: SETTINGS COMMANDS")
            await self.get_destination().send(embed=embed)
        else:
            # Fallback for other group commands
            await super().send_group_help(group)

    async def send_command_help(self, command):
        # Use a consistent color for all command help embeds
        base_color = discord.Color.green()
        if command.qualified_name.lower() == "timer":
            embed=discord.Embed(
            title="**TIMER**",
            description="it is a command to run countdowns",
            color=base_color
            )
            embed.add_field(
            name="Examples->", value="`vtimer <seconds>` \n`vtimer 20`"
            )
            embed.set_footer(text="Category: MISC COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "hi" or command.qualified_name.lower() == "hello" or command.qualified_name.lower() == "hey" or command.qualified_name.lower() == "heyy":
            embed=discord.Embed(
            title="**HI**",
            description="It says HELLO! to you",
            color=base_color
            )
            embed.add_field(
            name="Examples->", value="`vhi` \n`vhello` \n`vHI` \n`vHello`"
            )
            embed.set_footer(text="Category: MISC COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "emb" or command.qualified_name.lower() == "embed":
            embed=discord.Embed(
            title="**emb**",
            description="It send you a embed message",
            color=base_color
            )
            embed.add_field(
            name="Examples->", value="`vemb hi` \n`vemb hello` \n`vemb HI` \n`vemb bye`"
            )
            embed.set_footer(text="Category: MISC COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "ping":
            embed=discord.Embed(
            title="**ping**",
            description="It gives the Latency of your ip",
            color=base_color
            )
            embed.add_field(
            name="Examples->", value="`vping`"
            )
            embed.set_footer(text="Category: MISC COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "settings textspam" or command.qualified_name.lower() == "settings ts":
            embed=discord.Embed(
            title="**SETTINGS TEXTSPAM**",
            description="Allows or disallows the `textspam` command in a specific channel.",
            color=discord.Color.dark_purple()
            )
            embed.add_field(name="Examples->", value="`vsettings textspam add #general` \n`vsettings textspam remove #spam`")
            embed.set_footer(text="Category: SETTINGS COMMANDS")
            await self.get_destination().send(embed=embed)
            
        elif command.qualified_name.lower() == "music":
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
            
            embed.set_footer(text="Use vmusic to see this message again")
            await self.get_destination().send(embed=embed)
        
        elif command.qualified_name.lower() == "kick" or command.qualified_name.lower() == "k":
            embed=discord.Embed(
            title="**kick**",
            description="it is a command used to kick user",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vk`")
            embed.add_field(
            name="Examples->", value="`vkick <mention user> <reason>` , \n`vkick @venom#1234 idk` \n`vk @venom#1111 idk`")
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "ban" or command.qualified_name.lower() == "b":
            embed=discord.Embed(
            title="**ban**",
            description="it is a command used to ban user ",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`v!b`")
            embed.add_field(
            name="Examples->", value="`vban <mention user> <reason>` , \n`vban @venom#1234 idk` \n`vb @venom#1111 idk`")
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "unban" or command.qualified_name.lower() == "ub":
            embed=discord.Embed(
            title="**unban**",
            description="it is a command used to unban user ",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vub`")
            embed.add_field(
            name="Examples->", value="`vunban <mention user>` , \n`v!unban venom#1234` \n`vub venom#1111`")
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "purge" or command.qualified_name.lower() == "p":
            embed=discord.Embed(
            title="**purge**",
            description="it is a command used to purge messages",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vp`")
            embed.add_field(
            name="Examples->", value="`vpurge <number of messages>` , \n`vpurge 5` \n`vp 10`")
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "mute" or command.qualified_name.lower() == "m":
            embed=discord.Embed(
            title="**MUTE**",
            description="it mutes the member",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vm`")
            embed.add_field(
            name="Examples->", value="`vmute <user> <reason>` \n`vmute @venom#2341 idk` \n`vmute @venom120#1234 idk`\n`vm @venom#9876 idk`"
            )
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "unmute" or command.qualified_name.lower() == "um":
            embed=discord.Embed(
            title="**UNMUTE**",
            description="it unmutes the member",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vum`")
            embed.add_field(
            name="Examples->", value="`v!unmute <user>` \n`vmute @venom#2341 idk` \n`vunmute @venom120#1234 idk`\n`vum @venom#9876 idk`"
            )
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "lock" or command.qualified_name.lower() == "l":
            embed=discord.Embed(
            title="**LOCK CHANNEL**",
            description="it locks the current channel",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vl`")
            embed.add_field(
            name="Examples->", value="`vlock` \n`vl`"
            )
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "unlock" or command.qualified_name.lower() == "ul":
            embed=discord.Embed(
            title="**UNLOCK CHANNEL**",
            description="it unlocks the current channel",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vun`")
            embed.add_field(
            name="Examples->", value="`vunlock` \n`vul` "
            )
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "warn":
            embed=discord.Embed(
            title="**WARN**",
            description="it warn the respective user",
            color=discord.Color.red()
            )
            embed.add_field(
            name="Examples->", value="`vwarn <mention user> <reason>` ,\n`vwarn @venom120#8673 idk` \n`vwarn @venom129#2832 idk`"
            )
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "warnings" or command.qualified_name.lower() == "warns":
            embed=discord.Embed(
            title="**WARNINGS**",
            description="it shows the number of warns user has!",
            color=discord.Color.red()
            )
            embed.add_field(name="Aliases", value="`vwarning` \n`vwarns`")
            embed.add_field(
            name="Examples->", value="`vwarnings @venom120#8673` \n`vwarning @carnage#2832` \n`vwarns @spiderman#4926`"
            )
            embed.set_footer(text="Category: MODERATION COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "poll":
            embed=discord.Embed(
            title="**POLL**",
            description="it helps you to create poll",
            color=discord.Color.orange() # Different color for Polls
            )
            embed.add_field(
            name="Examples->", value='vpoll <time in minutes> <number of option> <title in " "> <every option names with spaces> \n`vpoll 1 2 "example" yes no` \n`vpoll 2 2 "is server good" yes no` \n`vpoll 15 1 "is venom op?" yes`'
            )
            embed.set_footer(text="Category: MISC COMMANDS")
            await self.get_destination().send(embed=embed)

        elif command.qualified_name.lower() == "roll":
            embed=discord.Embed(
            title="**ROLL**",
            description="It will generate a random rumber between 1 and number inputted.",
            color=base_color
            )
            embed.add_field(
            name="Examples->", value='`vroll <number>` \n`vroll 1000` \n`vroll 50`'
            )
            embed.set_footer(text="Category: MISC COMMANDS")
            await self.get_destination().send(embed=embed)
        else:
            await self.get_destination().send("command not found!")
