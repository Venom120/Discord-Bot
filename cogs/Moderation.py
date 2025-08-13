import discord
from discord.ext import commands
import random
import json
import os 
import asyncio
import time
import sys
import aiofiles

class Mod(commands.Cog, name='Moderation'):
    def __init__(self, client):
        self.client = client
        self.warnings = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            self.warnings[guild.id] = {}
            try:
                async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
                    lines = await file.readlines()
                    for line in lines:
                        data = line.split(" ")
                        member_id = int(data[0])
                        admin_id = int(data[1])
                        warnings_id = int(data[2])
                        reason = " ".join(data[3:]).strip("\n")
                        try:
                            self.warnings[guild.id][member_id][0] += 1
                            self.warnings[guild.id][member_id][1].append((admin_id, warnings_id, reason))
                        except KeyError:
                            self.warnings[guild.id][member_id] = [1, [(admin_id, warnings_id, reason)]]
            except FileNotFoundError:
                # File doesn't exist, will be created on first warning
                pass
            except Exception as e:
                print(f"Error loading warnings for guild {guild.id}: {e}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.warnings[guild.id] = {}
        # Optionally create the file here if you want it to exist even with no warnings
        # async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp: pass

    @commands.command(aliases=['m'])
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, user: discord.Member, reason= "not provided"):
        role = ctx.guild.get_role(894863758390853653)
        await user.add_roles(role)
        embed=discord.Embed(title="MEMBER MUTED", description=f"{user} has been muted!")
        await ctx.send(embed=embed)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify a user to mute.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
  

    @commands.command(aliases=['um'])
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, user: discord.Member):
        role = ctx.guild.get_role(894863758390853653)
        await user.remove_roles(role)
        embed=discord.Embed(title="MEMBER UNMUTED", description=f"{user} has been unmuted!")
        await ctx.send(embed=embed)

    @unmute.error
    async def unmute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify a user to unmute.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")


    @commands.command(aliases=['k'])
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : discord.Member, *, reason = "Reason not provided"):
        serverName = ctx.message.guild.name
        await member.send("You have been kicked from the " + serverName + ". Reason: " + reason)
        await member.kick(reason=reason)
        embed=discord.Embed(title="MEMBER KICKED", description=f'{member}, has been kicked from {serverName}')
        await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify a user/reason to kick.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")


    @commands.command(aliases=['b'])
    @commands.has_permissions(ban_members=True)
    async def ban(self ,ctx, member: discord.Member, *,reason: None):
        await member.ban(reason=reason)
        embed = discord.Embed(title= "BANNED MEMBER", description = f'{member} has been banned!, Because:'+ reason)
        await ctx.send(embed=embed)
        await member.ban(reason=reason)
  
    @ban.error
    async def ban_error(self,ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify a user/reason to ban.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
  

    @commands.command(aliases=['ub'])
    @commands.has_permissions(ban_members=True)
    async def unban(self,ctx, *, member):
        banned_user = await ctx.guild.bans()     
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_user:
            user=ban_entry.user

        if (user.name, user.discriminator)==(member_name, member_discriminator):
            await ctx.guild.unban(user)
            embed=discord.Embed(title="UNBANNED MEMBER", description=f"{member_name},{member_discriminator}, has been unbanned")
            await ctx.send(embed=embed)
            return  

    @unban.error
    async def unban_error(self,ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify a user to unban.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
    

    @commands.command(aliases=['p','clear'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self,ctx, amount=1):
        embed=discord.Embed(title="DELETING MESSAGES....", description ="** **")
        await ctx.send(embed=embed, delete_after=0.5)
        time.sleep(0.5)
        await ctx.channel.purge(limit=amount+2)

    @purge.error
    async def purge_error(self,ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify a Number to clear")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DONT HAVE PERMS TO DO IT, SIKE!")


    @commands.command(aliases=['l','lockdown','L'])
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed=discord.Embed(title="CHANNEL LOCKED", description =f"{ctx.channel.mention} has been locked")
        await ctx.send(embed=embed)
    
    @lock.error
    async def lock_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DONT HAVE PERMS TO DO IT, SIKE!")

    @commands.command(aliases=['ul','unlockdown','UL'])
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed=discord.Embed(title="CHANNEL UNLOCKED", description =f"{ctx.channel.mention} has been unlocked")
        await ctx.send(embed=embed)

    @unlock.error
    async def unlock_error(self,ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DONT HAVE PERMS TO DO IT, SIKE!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def spam(self, ctx, number:int, *, text:str):
        for i in range(0,number):
            await ctx.send(text)
            await asyncio.sleep(1)
    
    @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify text/number to spam.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason=None):
        if member is None:
            return await ctx.send("The provided member could not be found or you forgot to provide one.")
        if reason is None:
            return await ctx.send("Please provide a reason for warning this user.")
        try:
            first_warning = False
            warn_id = self.warnings[ctx.guild.id][member.id][1][-1][1] + 1 
            self.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, warn_id, reason))
            self.warnings[ctx.guild.id][member.id][0] += 1
        except KeyError:
            first_warning = True
            warn_id = 1
            self.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, warn_id, reason)]]
        try:
            count = self.warnings[ctx.guild.id][member.id][0]
            async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
                await file.write(f"{member.id} {ctx.author.id} {warn_id} {reason}\n")
            await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")
        except Exception as e:
            await ctx.send(f"{e}\nContact Venom_120")

    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
        if isinstance(error, commands.BadArgument):
            await ctx.send("User not found!!")

    @commands.command(aliases=["warning", "warns"])
    @commands.has_permissions(kick_members=True)
    async def warnings(self, ctx, member: discord.Member = None):
        if member is None:
            return await ctx.send("The provided member could not be found or you forgot to provide one.")
        embed = discord.Embed(
            title=f"Displaying Warnings for {member}",
            description="",
            colour=discord.Colour.red(),
        )
        try:
            for admin_id, warning_id, reason in self.warnings[ctx.guild.id][member.id][1]:
                admin = ctx.guild.get_member(admin_id)
                embed.description += f"**Warning {warning_id}** given by: {admin}, for: **'{reason}'**\n"
            embed.description += f"Total {len(self.warnings[ctx.guild.id][member.id][1])} Warnings"
            await ctx.send(embed=embed)
        except IndexError:
            return await ctx.send("No warnings on this user!")
        except KeyError:  # no warnings
            await ctx.send("This user has no warnings.")
        except Exception as e:
            await ctx.send(f"{e}\nCOntact Venom_120")

    @warnings.error
    async def warnings_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
        if isinstance(error, commands.BadArgument):
            await ctx.send("User not found!!")

    @commands.command(aliases=["delwarn","delwarns","dwarn","dwarns","dw"])
    @commands.has_permissions(kick_members=True)
    async def deletewarn(self, ctx, member: discord.Member = None, id = None):
        if member is None:
            return await ctx.send("The provided member could not be found or you forgot to provide one.")
        if id is None:
            return await ctx.send("Please provide a warning id to delete.")
        if str(id) == "all":
            self.warnings[ctx.guild.id][member.id] = []
            async with aiofiles.open(f"{ctx.guild.id}.txt", mode="w") as file:
                await file.write("")
            return await ctx.send(f"Deleted all warnings from {member}.")
        try:
            async with aiofiles.open(f"{ctx.guild.id}.txt", mode="w") as file:
                for x in self.warnings[ctx.guild.id][member.id][1]:
                    if str(x[1]) == str(id):                
                        self.warnings[ctx.guild.id][member.id][0] -= 1
                        for y in self.warnings[ctx.guild.id][member.id][1]:
                            if str(y[1]) == str(id):
                                self.warnings[ctx.guild.id][member.id][1].remove((y))
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
    async def deletewarn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")
        if isinstance(error, commands.BadArgument):
            await ctx.send("User not found!!")

async def setup(client):
    await client.add_cog(Mod(client))
    print("Mod log is loading")