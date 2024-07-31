import discord
import os
from discord.ext import tasks, commands
from PyRya.jsonStorage import jsonstorage

class MainLoop(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.storagePath = str(os.path.dirname(os.path.abspath(__file__))) + "\storage"
        self.storage = jsonstorage.Storage(path=self.storagePath)

        self.updateCounter.start()

    @tasks.loop(seconds=20)
    async def updateCounter(self):
        for n in os.listdir(self.storagePath):
            data = self.storage.read(n)
            guild = self.bot.get_guild(data["guildId"])
            channel = guild.get_channel(data["bankChannelId"])
            ui =  await channel.fetch_message(data["messageId"])
            balance = "{:,}".format(data["balance"]).replace(',', "'")
            upadtedUi = discord.Embed(title=f"Current Balance: {balance} aUEC", description=" ", color=discord.Color.blue())
            upadtedUi.set_author(name="Organisation Bank", icon_url="https://robertsspaceindustries.com/media/ew6fp2638a0rnr/post/CS_SC_UEE_SEAL_ROUND_01A.jpg")
            upadtedUi.set_footer(text="Made by and for the Community", icon_url="https://support.robertsspaceindustries.com/hc/article_attachments/360022704853/MadeByTheCommunity_White.png")
            await ui.edit(embed=upadtedUi)

    @updateCounter.before_loop
    async def before_updateCounter(self):
        await self.bot.wait_until_ready()
