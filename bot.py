from os import environ
from datetime import datetime, timezone, timedelta
from random import randrange
from PIL import Image, ImageFont, ImageDraw, ImageColor
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
#wait_for_component, create_select, create_select_option
from discord_slash.model import ButtonStyle
from discord_slash.context import ComponentContext

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=";", case_insensitive=True, owner_id=409205134028046346, intents=intents)
bot.remove_command("help")
slash = SlashCommand(bot, sync_commands=True)

font = ImageFont.truetype("comicsansms3.ttf", 48)
letters = "abcdefghijklmnopqrstuvwxyz"
numbers = "0123456789"
current = datetime.now(timezone(timedelta(hours=-5))) # 5 = CDT; 6 = CST

logs = []
mods =	[715327315974029333, 268849207039754241]
pokemon = [["Wigglytuff"], [], ["Groudon", "Jirachi"], ["Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Darkrai", "Shaymin", "Arceus"], ["Whimsicott", "Cobalion", "Terrakion", "Tornadus", "Thundurus", "Reshiram", "Landorus", "Kyurem"], ["Xerneas", "Diancie"], ["Type: Null", "Tapu Lele", "Tapu Bulu", "Cosmog", "Cosmoem", "Solgaleo", "Buzzwole", "Pheromosa", "Magearna", "Marshadow", "Poipole", "Stakataka", "Blacephalon"], ["Rillaboom", "Orbeetle", "Thievul", "Dubwool", "Drednaw", "Flapple", "Sandaconda", "Cramorant", "Toxel", "Grapploct", "Grimmsnarl", "Obstagoon", "Perrserker", "Cursola", "Sirfetch'd", "Mr. Rime", "Runerigus", "Stonjourner", "Arctozolt", "Arctovish", "Dragapult", "Zacian", "Zamazenta", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex"]]
shiny = [["Gastly", 715327315974029333], ["Beldum", 409205134028046346], ["Riolu", 345659592736243714], ["Sneasel", 441046114792243215], ["Rowlet", 542542697488187403], ["Cubchoo", 268849207039754241], ["Porygon", 263440201118908418], ["Mudkip", 821456684462637127]]
shiny.sort()
colors = {"main" : 0x5865f2, "poke" : 0xfe9ac9}
symbols = {"hedgehog" : "\U0001f994", "present" : "\ufe0f"}

def randomColor():
	return discord.Colour(randrange(0, 16777215))

@tasks.loop(seconds=5)
async def check():
	if current.day == 6:
		channel = discord.utils.get(bot.get_all_channels(), name="question-of-the-day")
		await channel.send(content="Come up with a different name for American (referring to those that live in the United States).", file=None)

@bot.event
async def on_connect():
	print(current)



@bot.event
async def on_ready():
	global poketwo
	print("Hello World!")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Hololive Council | ;h"))
	poketwo = await bot.fetch_user(716390085896962058)
	poketwo = poketwo.avatar_url

#	dm = await discord.utils.get(bot.get_all_members(), name="Comiserif").create_dm()
#	await dm.send("what")

#	check.start()

	channel = discord.utils.get(bot.get_all_channels(), name="local-retards")
#	msg = await channel.send(content="test", file=None)
#	msg = await channel.fetch_message(894412905204826112)
#	await msg.delete()

guild_ids = [645111346274500614, 409325808864460800]



@bot.event
async def on_message(msg):
	await bot.process_commands(msg)

	if msg.author.id == bot.user.id:
		return

	content = msg.content.lower()
	if ("clara " in content or content.endswith("clara")) and msg.author.id not in mods:
		await msg.channel.send(f"<{msg.author.name}> {msg.content}")

	for i in msg.embeds:
		if i.author.name != discord.Embed.Empty and "has been warned" in i.author.name:
			await msg.delete()
		if msg.author.id == 484792553057550336 and i.title != discord.Embed.Empty and i.title == "Creating poll...":
			await msg.add_reaction(symbols["hedgehog"])

	brazil = False
	if isinstance(msg.author, discord.Member):
		for i in msg.author.roles:
			if i.id == 745166782477893664:
				brazil = True
	if brazil:
		await msg.reply("https://media.discordapp.net/attachments/690665832350613545/831319542151118858/image0.gif")
	if msg.channel.id == 745167500701990982:
		with open("brazil.txt", "a") as f:
			f.write(f"{msg.author.name}\n\t{msg.clean_content}\n")



@slash.slash(description="Send a message in Comic Sans.", guild_ids=guild_ids, options=[create_option(name="message", description="The message you want to send.", option_type=3, required=True), create_option(name="color", description="The color of the text.", option_type=3, required=False)])
async def sendComic(ctx, message:str, color:str="#f0f"):
	count = 0
	lineLen = 36
	msgList = []
	breaks = []
	try:
		clr = ImageColor.getrgb(color)
	except:
		await ctx.send(f"\"{color}\" is not a color I recognize.", hidden=True)
		return
		
	for i in message:
		msgList.append(i)
	for i in range(len(msgList)):
		if msgList[i] == "\n":
			count = -1
		if count == lineLen:
			if msgList[i] == " ":
				msgList[i] = "\n"
				count = -1
			else:
				breaks.append(i)
				count = 0
		count += 1
	for i in breaks:
		msgList.insert(i, "\n")
	message = "".join(msgList)
	
	base = Image.open("base.png")
	size = ImageDraw.Draw(base).multiline_textbbox((0, 0), message, font)
	base = base.resize((size[2], size[3]))
	with base as im:
		draw = ImageDraw.Draw(im)
		draw.text((0, 0), message, clr, font)
		im.save("final.png")
	await ctx.send(file=discord.File("final.png"))



@slash.slash(description="Make a poll.", guild_ids=guild_ids, options=[create_option(name="title", description="The title of the poll.", option_type=3, required=True), create_option(name="choice1", description="The poll's first choice.", option_type=3, required=True), create_option(name="choice2", description="The poll's second choice.", option_type=3, required=True)])
async def poll(ctx, title:str, choice1:str, choice2:str):
	numbers = [symbols["hedgehog"], "\U0001f7e9", "\U0001f7ea"]
	emb = discord.Embed(title=f"{ctx.author.name}'s poll", color=ctx.author.color)
	emb.set_thumbnail(url=str(ctx.author.avatar_url))
	emb.add_field(name=title, value=f"{numbers[1]}: {choice1}\n{numbers[2]}: {choice2}")
	msg = await ctx.send(embed=emb)
	for i in numbers:
		await msg.add_reaction(i)



@slash.slash(description="List what people are shiny hunting in Pokétwo.", guild_ids=guild_ids)
async def shinyList(ctx):
	description = ""
	for i in shiny:
		description += f"```{i[0]}:``` {bot.get_user(i[1])}\n\n"
	emb = discord.Embed(title="Pokétwo Shiny Hunt List", description=description, color=colors["poke"])
	emb.set_thumbnail(url=poketwo)
	await ctx.send(embed=emb)



@slash.slash(description="List all Pokémon that people haven't caught in Pokétwo.", guild_ids=guild_ids)
async def uncaughtList(ctx):
	count = 0
	for i in pokemon:
		for j in i:
			count += 1
	emb = discord.Embed(title=f"Comiserif's Uncaughts: {str(count)} left", description="Ping me if you want to be a good person.", color=colors["poke"])
	emb.set_thumbnail(url=poketwo)
	for i in range(len(pokemon)):
		val = "```"
		for j in range(len(pokemon[i])):
			val += f"{pokemon[i][j]}, "
		val = f"{val[:len(val) - 2]}```"
		emb.add_field(name=f"Generation {str(i+1)}", value=val, inline=False)
	emb.set_footer(text="If you send me a list of all your uncaught Pokémon, I can add it to this command.")
	await ctx.send(embed=emb)



@slash.slash(description="Find the most recent 10 images sent in a channel.", guild_ids=guild_ids, options=[create_option(name="channel", description="The channel to get the images from.", option_type=7, required=True)])
async def lastImages(ctx, channel:discord.abc.GuildChannel):
	if not isinstance(channel, discord.TextChannel):
		await ctx.send(f"{channel} is not a text channel.", hidden=True)
		return
	msg_list = []
	att_ct = 0
	async for i in channel.history(limit=500):
		if i.attachments != []:
			i.attachments.reverse()
			for j in i.attachments:
				if att_ct < 10:
					att_ct += 1
					msg_list.append([i.jump_url, j.url, att_ct])
	if msg_list == []:
		await ctx.send(f"Could not find any images in the most recent 500 messages.")
		return
	emb = discord.Embed(title=f"Last Sent Images in #{channel}", description="If an image is not shown here, it is a video.", color=colors["main"])
	emb.set_image(url=msg_list[0][1])
	emb.set_footer(text=f"1/{len(msg_list)}")

	def init_buttons():
		return create_actionrow(create_button(style=ButtonStyle.blue, emoji="\u2b05" + symbols["present"], custom_id="l"), create_button(style=ButtonStyle.blue, emoji="\u27a1" + symbols["present"], custom_id="r"), create_button(style=ButtonStyle.URL, label="Go to Message", url=msg_list[0][0]), create_button(style=ButtonStyle.URL, label="Image Link", url=msg_list[0][1]))

	act_row = init_buttons()
	await ctx.send(embed=emb, components=[act_row])

	@bot.event
	async def on_component(comctx:ComponentContext):
		if ctx.author_id != comctx.author_id:
			await comctx.send("You cannot change pages because you did not run the command.", hidden=True)
			return

		if comctx.custom_id == "l":
			msg_list.insert(0, msg_list[len(msg_list)-1])
			msg_list.pop()
		else:
			msg_list.append(msg_list[0])
			msg_list.pop(0)

		emb.set_image(url=msg_list[0][1])
		emb.set_footer(text=f"{msg_list[0][2]}/{len(msg_list)}")

		await comctx.edit_origin(embed=emb, components=[init_buttons()])



@slash.slash(description="React with letters and numbers to a message.", guild_ids=guild_ids, options=[create_option(name="message_id", description="The ID of the message you want to react to.", option_type=3, required=True), create_option(name="text", description="The text to react to the message with", option_type=3, required=True)])
async def react(ctx, message_id:str, text:str):
	length = len(text)
	init = []
	description = ""
	for i in text:
		init.append(i)
	text = "".join(dict.fromkeys(init)).lower()
	if length > len(text):
		description += "— A message cannot have duplicate reactions.\n"
	if len(text) > 20:
		description += "— Your message was cut off because a message can only have 20 reactions.\n"
	banned = []
	for i in text:
		if not i.isalnum():
			banned.append(i)
	for i in banned:
		text = text.replace(i, "")
	if length > len(text):
		description += "— This command only supports letters and numbers.\n"

	in_server = False
	for i in ctx.guild.text_channels:
		try:
			msg = await i.fetch_message(int(message_id))
			in_server = True
		except:
			continue
	if not in_server:
		await ctx.send("message_id needs to be an ID of a message in this server.", hidden=True)
		return
	emojis = []
	for i in text:
		for j in range(len(letters)):
			if letters[j] == i:
				emojis.append(chr(127462+j))
		for j in range(len(numbers)):
			if numbers[j] == i:
				emojis.append(chr(48+j) + symbols["present"] + "\u20e3")
	for i in emojis:
		await msg.add_reaction(i)
	act_row = create_actionrow(create_button(style=ButtonStyle.URL, label="Go to Message", url=msg.jump_url))
	if description != "":
		emb = discord.Embed(description=description, color=colors["main"])
	await ctx.send(embed=emb, components=[act_row])



@bot.command()
async def r(ctx, *para):
	if para == ():
		await ctx.reply("You need to input something.", mention_author=False)
		return

	text = "".join(para)
	length = len(text)
	init = []
	description = ""
	for i in text:
		init.append(i)
	text = "".join(dict.fromkeys(init)).lower()
	if length > len(text):
		description += "— A message cannot have duplicate reactions.\n"
	if len(text) > 20:
		description += "— Your message was cut off because a message can only have 20 reactions.\n"
	banned = []
	for i in text:
		if not i.isalnum():
			banned.append(i)
	for i in banned:
		text = text.replace(i, "")
	if length > len(text):
		description += "— This command only supports letters and numbers.\n"
	
	if ctx.message.reference != None:
		in_server = False
		for i in ctx.guild.text_channels:
			try:
				msg = await i.fetch_message(ctx.message.reference.message_id)
				in_server = True
			except:
				continue
		if not in_server:
			await ctx.reply("[message_id] needs to be an ID of a message in this server.")
			return
		emojis = []
		for i in text:
			for j in range(len(letters)):
				if letters[j] == i:
					emojis.append(chr(127462+j))
			for j in range(len(numbers)):
				if numbers[j] == i:
					emojis.append(chr(48+j) + symbols["present"] + "\u20e3")
		for i in emojis:
			await msg.add_reaction(i)
		act_row = create_actionrow(create_button(style=ButtonStyle.URL, label="Go to Message", url=msg.jump_url))
		if description != "":
			emb = discord.Embed(description=description, color=colors["main"])
		await ctx.reply(embed=emb, components=[act_row])
	else:
		await ctx.reply("You need to reply to a message.")



@bot.command(name="h")
async def listCommands(ctx):
	await ctx.trigger_typing()
	emb = discord.Embed(title="Commands", color=colors["main"])
	pre = bot.command_prefix
	commands = [["r", "Adds reactions to the message replied to."], ["h", "Displays this message."]]
	for i in commands:
		emb.add_field(name=pre + i[0], value=f"{i[1]}\n")
	emb.set_footer(text="All commands are case insensitive.")
	await ctx.send(embed=emb)

bot.run(environ["token"])
