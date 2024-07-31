#Global imports
import datetime
import os

#Discord imports
import discord
from discord.ext import commands
from discord.commands import Option

#PyRya Imports
from PyRya.logger import logger
from PyRya.jsonStorage import jsonstorage
from PyRya.configParser import cfg

#Local imports
from updateloop import MainLoop


#Variable setup
storagePath = str(os.path.dirname(os.path.abspath(__file__))) + "\storage"
bot = discord.Bot(command_prefix="/", intents=discord.Intents.all())
Logger = logger.newLogger("bot")
Logger.info("Logging in...")
storage = jsonstorage.Storage(storagePath)
cfgPath = str(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Config import
cfgParser = cfg.Config(cfgPath)
configData = cfgParser.loadcfg("config.cfg")

if configData["token"] == "none":
    Logger.error("No discord token found, check config.cfg")
    exit()

#Bot startup logic
@bot.event
async def on_ready():
    try:
        #bot execution and loading
        bot.add_view(requestButtons())
        await bot.change_presence(activity=discord.Game(name="WIP | aUEC"))
        bot.add_cog(MainLoop(bot=bot))
        Logger.info("Conecting to Shards with Id: " + bot.shard_id if bot.shard_id is not None else "Connecting to shards with Id: None")
        Logger.info("Connecting to Session with Id: " + bot.ws.session_id +  " with User " + bot.user.name + " UID: " + str(bot.user.id))
        Logger.info("Ready " + str(int(bot.latency)) + "ms")
    except Exception as e:
        Logger.error(e)


#Bot shutdown logic
@bot.event
async def on_disconnect():
    for n in os.listdir(storagedir):
        data = storage.read(n)
        guild = bot.get_guild(data["guildId"])
        channel = guild.get_channel(data["bankChannelId"])
        ui = await channel.fetch_message(data["messageId"])
        upadtedUi = discord.Embed(title=f"Current Balance: {data['balance']} aUEC", description="Placeholder", color=discord.Color.default())
        upadtedUi.set_author(name="Organisation Bank", icon_url="https://robertsspaceindustries.com/media/ew6fp2638a0rnr/post/CS_SC_UEE_SEAL_ROUND_01A.jpg")
        upadtedUi.set_footer(text="Made by and for the Community", icon_url="https://support.robertsspaceindustries.com/hc/article_attachments/360022704853/MadeByTheCommunity_White.png")
        await ui.edit(embed=upadtedUi)


#setChannel command
@bot.slash_command(name="setchannel", description="Sets the channel for the bot to work in")
@commands.has_permissions(administrator=True)
async def setChannel(ctx: discord.ApplicationContext):

    #check if this server alredy has a registered chat.
    for n in os.listdir(os.path.dirname(os.path.abspath(__file__)) + "\storage"):
        if n == str(ctx.guild.id) + ".json":
            await ctx.respond("This channel is already set as the operating channel or another channel is already set.", ephemeral=True)
            return

    #send message and register channel.
    await ctx.respond("Channel has been registered sucessfully.", ephemeral=True)
    uiEmbed = discord.Embed(title="**Initializing...**", description=" ")
    uiEmbed.set_author(name="Organisation Bank", icon_url="https://robertsspaceindustries.com/media/ew6fp2638a0rnr/post/CS_SC_UEE_SEAL_ROUND_01A.jpg")
    uiEmbed.set_footer(text="Made by and for the Community", icon_url="https://support.robertsspaceindustries.com/hc/article_attachments/360022704853/MadeByTheCommunity_White.png")
    ui = await ctx.send(embed=uiEmbed)
    storage.write(str(ctx.guild.id) + ".json", {"guildId": ctx.guild.id, "bankChannelId": ctx.channel.id, "messageId": ui.id, "logChannelId": "none", "balance": 0, "requests": {}})


#Clearchannel command
@bot.slash_command(name="clearchannel", description="Removes the channel the bot works in")
@commands.has_permissions(administrator=True)
async def clearChannel(ctx: discord.ApplicationContext):

    #check for the file.
    storagePath = str(os.path.dirname(os.path.abspath(__file__))) + "\storage"
    for n in os.listdir(storagePath):
        if n == str(ctx.guild.id) + ".json":
            os.remove(storagePath + "\\" + n)
            Logger.info(f"Guild {n} has been removed.")
            await ctx.respond("channel has been removed.", ephemeral=True)
            return
    await ctx.respond("there is no channel set on this server.", ephemeral=True)


#setLogChannel command
@bot.slash_command(name="setlogchannel", description="sets the channel for logs and requests to work in.")
@commands.has_permissions(administrator=True)
async def setlogchannel(ctx: discord.ApplicationContext):

    #standart check
    for n in os.listdir(storagePath):
        if n == str(ctx.guild.id) + ".json":
            data = storage.read(n)

            #Error Check LCE-1
            if data["bankChannelId"] == ctx.channel.id:
                await  ctx.respond("Log Channel cannot be the bank channel.", ephemeral=True)
                return 1

            #Error Check LCE-2
            if data["logChannelId"] == ctx.channel.id:
                await  ctx.respond(f"Log Channel is already set to {ctx.channel.mention}", ephemeral=True)
                return 1

            #storage edit
            storage.edit(filename=n, key="logChannelId", value=ctx.channel.id)
            await  ctx.respond("Log Channel has been set.")

#Deposit command
@bot.slash_command(name="deposit", description="deposits aUEC")
async def deposit(ctx: discord.ApplicationContext, amount: Option(int, "amount")):

    #check and modify server.json
    for n in os.listdir(os.path.dirname(os.path.abspath(__file__)) + "\storage"):
        if n == str(ctx.guild.id) + ".json":
            data = storage.read(n)

            #Error Log Channel
            if data["logChannelId"] == "none":
                await ctx.respond(f"This server has no registered log Channel.", ephemeral=True)
                return 0

            #Pass logic
            storage.edit(n, "balance", data["balance"]+amount)
            Logger.info(f"User {ctx.user.id} added {amount} aUEC to server {ctx.guild.id}.")
            await ctx.respond(f"{amount}aUEC have been added to the Organisation Bank.", ephemeral=True)
            channel = ctx.guild.get_channel(data["logChannelId"])
            logEmbed = discord.Embed(color=discord.Color.green(), title=f"**User {ctx.user.name} added {amount} aUEC to the Organisation Bank.**", timestamp=datetime.datetime.now())
            await channel.send(embed=logEmbed)
            return 0

        await ctx.respond(f"Server has no Bank Channel.", ephemeral=True)

#withdraw command
@bot.slash_command(name="withdraw", description="Creates a request for aUEC withdrawl")
async def withdraw(ctx: discord.ApplicationContext, amount: Option(int, description="amount"), reason: Option(str, description="reason")):

    for n in os.listdir(storagePath):
        if n == str(ctx.guild.id) + ".json":
            data = storage.read(n)

            #Error Check logChannelId
            if data["logChannelId"] == "none":
                await ctx.respond(f"This server has no registered log Channel.", ephemeral=True)
                return 0

            #Error Check Balance
            if data["balance"] <= amount - 1:
                await ctx.respond(f"Not enough aUEC in the Organisation Bank.", ephemeral=True)
                return 0

            #Error Check User
            for k in data.get("requests", {}):
                print(k)
                if str(k) == str(ctx.user.id):
                    await ctx.respond(f"You Cannot have multiple requests at once", ephemeral=True)
                    return 0

            requestEmbed = discord.Embed(color=discord.Color.yellow(), title=f"User {ctx.user.name} requested {amount} aUEC from the Organisation Bank", description=str(reason), footer=discord.EmbedFooter(ctx.user.id))
            logChannel = ctx.guild.get_channel(data["logChannelId"])
            requestMessage = await logChannel.send(embed=requestEmbed, view=requestButtons())
            await ctx.respond(f"Request has been sent successfully.", ephemeral=True)

            storage.subEdit(n, key="requests", subKey=str(ctx.user.id), value={"amount": amount})

class requestButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green, custom_id="approve")
    async def approveCallback(self, button, interaction: discord.Interaction):
        for n in os.listdir(storagePath):
            if n == str(interaction.guild.id) + ".json":
                #Get Targeted user and send Approve DM
                requestEmbed = interaction.message.embeds[0]
                userId = requestEmbed.footer.text
                user = await bot.fetch_user(userId)
                request = storage.read(n)["requests"][str(userId)]
                data = storage.read(n)
                responseEmbed = discord.Embed(title=f"Your Organisation Bank request on {bot.get_guild(data['guildId']).name} got approved by {interaction.user.name}", color=discord.Color.green(), description=f"Amount: {request['amount']} \n")
                try:
                    await user.send(embed=responseEmbed)
                    await interaction.respond("Request has been approved successfully.", ephemeral=True)

                except discord.Forbidden:
                    await interaction.respond("User could not be DM'd", ephemeral=True)

                #Deactivate the embed and delete the entry
                denyEmbed = discord.Embed(title=f"Request from user {user.name} Approved. Please do not forget to send them the money ingame..", color=discord.Color.green(), description=requestEmbed.description)
                await interaction.message.edit(embed=denyEmbed, view=None)

                #Error Balance check
                if data["requests"][userId]["amount"] > data["balance"]:
                    await interaction.respond("Not enough money in the Organisation Bank.", ephemeral=True)
                    return 0

                storage.edit(n, "balance", data["balance"] - data["requests"][userId]["amount"])
                storage.subDelete(n, key="requests", subKey=(userId))

            else:
                await interaction.respond("Request could not be found.", ephemeral=True)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, custom_id="deny")
    async def denyCallback(self, button, interaction: discord.Interaction):
        for n in os.listdir(storagePath):
            if n == str(interaction.guild.id) + ".json":
                #Get Targeted user and send Deny DM
                requestEmbed = interaction.message.embeds[0]
                userId = requestEmbed.footer.text
                user = await bot.fetch_user(userId)
                request = storage.read(n)["requests"][str(userId)]
                data = storage.read(n)
                responseEmbed = discord.Embed(title=f"Your Organisation Bank request on {bot.get_guild(data['guildId']).name} got denied by {interaction.user.name}", color=discord.Color.red(), description=f"Amount: {request['amount']} \n")
                try:
                    await user.send(embed=responseEmbed)
                    await interaction.respond("Request has been denied successfully.", ephemeral=True)
                except discord.Forbidden:
                    await interaction.respond("User could not be DM'd", ephemeral=True)

                #Deactivate the embed and delete the entry
                denyEmbed = discord.Embed(title=f"Request from user {user.name} Denied.", color=discord.Color.red(), description=requestEmbed.description)
                await interaction.message.edit(embed=denyEmbed, view=None)
                storage.subDelete(n, key="requests", subKey=(userId))

            else:
                await interaction.respond("Request could not be found.", ephemeral=True)

bot.run(configData["token"])