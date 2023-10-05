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
        await ctx.send(embed=embed)
        time.sleep(1)
        await ctx.channel.purge(limit=amount+2)
        embed=discord.Embed(title="MESSAGE DELETED", description =f"deleted {amount} messages")
        await ctx.send(embed=embed)
        time.sleep(2)
        await ctx.channel.purge(limit=1)

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
    @commands.has_permissions(manage_messages=True)
    async def spam(self, ctx, number:int, *, text:str):
        for i in range(0,number):
            await ctx.send(text)
            time.sleep(1)
    
    @spam.error
    async def spam_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("please specify text/number to spam.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("YOU DON'T HAVE PERMS TO DO IT, SIKE!.")








async def setup(client):
    await client.add_cog(Mod(client))
    print("Mod log is loading")