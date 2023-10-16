import discord
from discord.ext import commands
import asyncio
import aiofiles
from datetime import datetime
import pytz

def utc_to_ist(utc_datetime):
    utc_timezone = pytz.timezone('UTC')
    ist_timezone = pytz.timezone('Asia/Kolkata')
    utc_time = utc_timezone.localize(utc_datetime)
    ist_time = utc_time.astimezone(ist_timezone)
    return ist_time


def current():
    current_date = int(utc_to_ist(datetime.utcnow()).strftime("%#d"))
    current_month = int(utc_to_ist(datetime.utcnow()).strftime("%m"))
    current_year = int(utc_to_ist(datetime.utcnow()).strftime("%Y"))
    current_time = utc_to_ist(datetime.utcnow()).strftime("%I:%M %p")
    date = utc_to_ist(datetime.utcnow()).strftime("%#d/%m/%Y")
    date_list = [current_date, current_month, current_year, current_time, date]
    return date_list


class WelcomeLeave(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.welcome_channel_id = 877889271653097526
        self.leave_channel_id = 877889271653097526

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 877889271653097526:
            channel1 = self.client.get_channel(877889271653097526)
            embed = discord.Embed(title = "Member joined", description = f"Welcome {member.mention} to the server!", color = discord.Color.blue())
            date = int(member.created_at.strftime("%#d"))
            month = int(member.created_at.strftime("%m"))
            year = int(member.created_at.strftime("%Y"))
            list1 = current()
            d_date =  list1[0] - date
            d_month =  list1[1] - month
            d_year =  list1[2] - year
            # Adjust for negative months or days
            if d_date < 0:
                d_month -= 1
                d_date += 30  # Assuming an average month length of 30 days
            if d_month < 0:
                d_year -= 1
                d_month += 12
            embed.add_field(name = "Account age", value = f"{d_year} years, {d_month} months, {d_date} days")
            embed.set_footer(text = f"ID: {member.id} • {list1[0]}/{list1[1]}/{list1[2]} {list1[3]}")
            # embed.set_thumbnail(url = member.avatar_url)
            await channel1.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id == 877889271653097524:
            channel2 = self.client.get_channel(878191679759323147)
            list2 = current()
            embed = discord.Embed(title = "Member left", description = f"{member.mention} has left the server!", color = discord.Color.orange())
            embed.set_footer(text = f"ID: {member.id} • {list2[4]} {list2[3]}")
            # embed.set_thumbnail(url = member.avatar_url)
            await channel2.send(embed = embed)


async def setup(client):
    await client.add_cog(WelcomeLeave(client))
    print("Welcomeleave is loading")
