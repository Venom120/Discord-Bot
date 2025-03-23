import discord
from discord.ext import commands
import asyncio, time
import python_aternos
cookie_id='4RPROsfsLKL5vgPvBUG8pwRSLIg6yPqFbtsbdnCtZTBlE09qOxmHxEqlXseDa0Lygd6oQ90ym7BHAoWZrCtOKPHB0pJxZjWSYd4j'

global atclient, aternos
atclient = python_aternos.Client()
aternos = atclient.account
def server_setup():
    atclient.login_with_session(cookie_id)
    serv = aternos.list_servers()[0]
    return serv

def logout():
    atclient.logout()

def server_status():
    list1=[]
    s = server_setup().status
    while(True):
        if s == 'online':
            t = 'online'
            break
    atclient.logout()
    return t
class Server(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def servstart(self, ctx):
        try:
            serv = server_setup()
            serv.start()
            time.sleep(40)
            st = server_status()
            em = discord.Embed(title=":octagonal_sign: **Server has started**")
            await ctx.send(embed = em)
            logout()
                
        except Exception as e:
            em = discord.Embed(title="**:x: Error**",description=f"{e}")
            await ctx.send(embed = em)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def servstatus(self, ctx):
        try:
            serv = server_setup()
            await ctx.send(serv.status)
            logout()
        except Exception as e:
            em = discord.Embed(title="**:x: Error**",description=f"{e}")
            await ctx.send(embed = em)
            
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def servstop(self, ctx):
        serv = server_setup()
        serv.stop()
        em = discord.Embed(title=":octagonal_sign: **Server has stopped**")
        await ctx.send(embed = em)
        logout()


async def setup(client):
    await client.add_cog(Server(client))
    print("Server is loading")