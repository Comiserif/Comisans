from os import environ
from datetime import datetime, timezone, timedelta
from random import randrange, choice, sample
from PIL import Image, ImageFont, ImageDraw, ImageColor
from asyncio import sleep
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

guild = ""
channel = ""
author = ""
font = ImageFont.truetype("comicsansms3.ttf", 48)
letters = "abcdefghijklmnopqrstuvwxyz"
numbers = "0123456789"
offset = 6 # 5 = CDT, 6 = CST
current = datetime.now(timezone(timedelta(hours=-offset)))

colors = {"blurple" : 0x5865f2, "poke" : 0xfe9ac9}
symbols = {"hedgehog" : "\U0001f994", "present" : "\ufe0f"}
logs = {}
mods =	[715327315974029333, 268849207039754241]
pokemon = [[], [], [], ["Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Darkrai", "Shaymin"], ["Whimsicott", "Cobalion", "Terrakion", "Tornadus", "Thundurus", "Reshiram", "Landorus", "Kyurem"], ["Xerneas", "Diancie"], ["Type: Null", "Tapu Lele", "Cosmog", "Cosmoem", "Solgaleo", "Buzzwole", "Pheromosa", "Magearna", "Marshadow", "Poipole", "Stakataka", "Blacephalon"], ["Rillaboom", "Orbeetle", "Dubwool", "Drednaw", "Flapple", "Sandaconda", "Cramorant", "Grapploct", "Grimmsnarl", "Obstagoon", "Perrserker", "Cursola", "Sirfetch'd", "Mr. Rime", "Runerigus", "Arctozolt", "Dragapult", "Zacian", "Zamazenta", "Kubfu", "Urshifu", "Zarude", "Regieleki", "Regidrago", "Glastrier", "Spectrier", "Calyrex"]]
shapes = [["\u2764" + symbols["present"], "\U0001f499", "\U0001f49a"], ["\U0001f534", "\U0001f535", "\U0001f7e2"], ["\U0001f7e5", "\U0001f7e6", "\U0001f7e9"]] # red blue green heart circle square
shiny = [["Gastly", 715327315974029333], ["Beldum", 409205134028046346], ["Riolu", 345659592736243714], ["Sneasel", 441046114792243215], ["Dreepy", 542542697488187403], ["Cubchoo", 268849207039754241], ["Porygon", 263440201118908418], ["Snorlax", 821456684462637127], ["Ralts", 776134910548639828]]
shiny.sort()

def randomColor():
	return discord.Colour(randrange(0, 16777215))

async def wait(x):
	await sleep(x)

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
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="VShojo | ;h"))
	poketwo = await bot.fetch_user(716390085896962058)
	poketwo = poketwo.avatar_url

#	dm = await discord.utils.get(bot.get_all_members(), name="Comiserif").create_dm()
#	await dm.send("what")

#	check.start()

	channel = discord.utils.get(bot.get_all_channels(), name="local-retards")
#	msg = await channel.send(content="i logged onto github ", file=discord.File("a.png"))
#	for i in [904582203734888520]:
#		msg = await channel.fetch_message(i)
#		await msg.reply("i logged onto github and updated comisans' code just to say what the fuck")

	channel = discord.utils.get(bot.get_all_channels(), name="local-retards")
	emb = discord.Embed(title="Countdowns", color=0xff0000)
	dates = [datetime(2021, 12, 1, offset), datetime(2022, 1, 9, offset)]
	for i in range(len(dates)):
		dates[i] = (dates[i] - datetime.utcnow()).days
	emb.add_field(name="Stone Ocean", value=f"{dates[0]} days")
	emb.add_field(name="AOT Season 4 Part 2", value=f"{dates[1]} days")
	await channel.send(embed=emb)

guild_ids = [645111346274500614, 409325808864460800]



@bot.event
async def on_message(msg):
	await bot.process_commands(msg)

	try:
		temp = logs[f"{msg.channel.id}"]
		newLogs = True
	except:
		newLogs = False

	if newLogs:
		if len(temp) > 9:
			temp.pop(0)
		attach = ""
		for i in msg.attachments:
			attach += f"{i.url}\n"
		temp.append(f"__{msg.author}__\n{msg.clean_content if msg.clean_content != '' else '`No message content`'}\n{attach if attach != '' else '`No attachments`'}")
	else:
		logs[f"{msg.channel.id}"] = []

	if msg.author.id == bot.user.id:
		return

	content = msg.content.lower()
	if ("clara " in content or content.endswith("clara")) and msg.author.id not in mods:
		await msg.channel.send(f"<{msg.author.name}> {msg.content}")
	if "ruined it at" in content and msg.author.id == 510016054391734273:
		await msg.channel.send("__***good job stinky***__")

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



@slash.slash(description="Send a message in Comic Sans.", guild_ids=guild_ids, options=[create_option(name="text", description="The text you want to send.", option_type=3, required=True), create_option(name="color", description="The color of the text.", option_type=3, required=False)])
async def sendComic(ctx, text:str, color:str="#f0f"):
	count = 0
	lineLen = 36
	msgList = []
	breaks = []
	try:
		clr = ImageColor.getrgb(color)
	except:
		await ctx.send(f"\"{color}\" is not a color I recognize.", hidden=True)
		return
		
	for i in text:
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
	breaks.reverse()
	for i in breaks:
		msgList.insert(i, "\n")
	text = "".join(msgList)
	
	base = Image.open("base.png")
	size = ImageDraw.Draw(base).multiline_textbbox((0, 0), text, font)
	base = base.resize((size[2], size[3]))
	with base as im:
		draw = ImageDraw.Draw(im)
		draw.text((0, 0), text, clr, font)
		im.save("final.png")
	await ctx.send(file=discord.File("final.png"))



@slash.slash(description="Make a poll.", guild_ids=guild_ids, options=[create_option(name="title", description="The title of the poll.", option_type=3, required=True), create_option(name="choice1", description="The poll's first choice.", option_type=3, required=True), create_option(name="choice2", description="The poll's second choice.", option_type=3, required=True)])
async def poll(ctx, title:str, choice1:str, choice2:str):
	numbers = [symbols["hedgehog"], "\U0001f7e9", "\U0001f7ea"]
	emb = discord.Embed(color=ctx.author.color)
	emb.set_author(name=f"{ctx.author.name}'s Poll", icon_url=str(ctx.author.avatar_url))
	emb.add_field(name=title, value=f"{numbers[1]} {choice1}\n{numbers[2]} {choice2}")
	msg = await ctx.send(embed=emb)
	for i in numbers:
		await msg.add_reaction(i)



@slash.slash(description="List what people are shiny hunting in Pokétwo.", guild_ids=guild_ids)
async def shinyList(ctx):
	description = ""
	for i in shiny:
		description += f"`{i[0]}:` {bot.get_user(i[1])}\n"
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



@slash.slash(description="Make small text.", guild_ids=guild_ids, options=[create_option(name="text", description="The text you want to send.", option_type=3, required=True)])
async def smallText(ctx, text:str):
	banned = []
	for i in text:
		if not i.isalpha() and i != " ":
			banned.append(i)
	for i in banned:
		text = text.replace(i, "")
	small = "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᑫʳˢᵗᵘᵛʷˣʸᶻ"
	for i in range(len(small)):
		text = text.replace(letters[i], small[i])
	await ctx.send(text)



@slash.slash(description="Randomly choose between a number of options.", guild_ids=guild_ids, options=[create_option(name="one", description="The first option to choose from.", option_type=3, required=True), create_option(name="two", description="The second option to choose from.", option_type=3, required=True), create_option(name="three", description="A third option to choose from.", option_type=3, required=False), create_option(name="four", description="A fourth option to choose from.", option_type=3, required=False), create_option(name="five", description="A fifth option to choose from.", option_type=3, required=False), create_option(name="six", description="A sixth option to choose from.", option_type=3, required=False), create_option(name="seven", description="A seventh option to choose from.", option_type=3, required=False), create_option(name="eight", description="An eighth option to choose from.", option_type=3, required=False), create_option(name="nine", description="A ninth option to choose from.", option_type=3, required=False), create_option(name="ten", description="A tenth option to choose from.", option_type=3, required=False)])
async def randomChoice(ctx, one:str, two:str, three:str="", four:str="", five:str="", six:str="", seven:str="", eight:str="", nine:str="", ten:str=""):
	choices = []
	for i in [one, two, three, four, five, six, seven, eight, nine, ten]:
		if i != "":
			choices.append(i)
	await ctx.send(embed=discord.Embed(title=choice(choices), color=colors["blurple"]))



@slash.slash(description="Remember the sequence of shapes, then answer the question correctly.", guild_ids=guild_ids)
async def shapeStatus(ctx):
	seq = ""
	prop = {"red":0, "blue":0, "green":0, "hearts":0, "circles":0, "squares":0}
	for i in range(6):
		shape = randrange(3)
		color = randrange(3)
		seq += shapes[shape][color]
		prop["hearts" if shape == 0 else "squares" if shape % 2 == 0 else "circles"] += 1
		prop["red" if color == 0 else "green" if color % 2 == 0 else "blue"] += 1
	subject = choice(list(prop.keys()))
	question = f"How many shapes were {subject}?"
	answer = prop[subject]
	precede = [0, 1, 2, 3]
	for i in range(max(3 - answer, 0)):
		precede.pop()
	start = choice(precede)
	answers = []
	for i in range(4):
		answers.append(answer - start + i)
	buttons = []
	for i in range(len(answers)):
		buttons.append(create_button(style=ButtonStyle.gray, label=str(answers[i]), custom_id=str(answers[i])))
	msg = await ctx.send(embed=discord.Embed(title="Remember this sequence!", description=seq, color=colors["blurple"]))
	await wait(6)
	await msg.edit(content="Did you remember?", embed=None)
	await ctx.send(embed=discord.Embed(title=question, colors=colors["blurple"]), components=[create_actionrow(*buttons)])

	@bot.event
	async def on_component(comctx:ComponentContext):
		if ctx.author_id != comctx.author_id:
			await comctx.send("You cannot choose an option because you did not run the command.", hidden=True)
			return

		id = int(comctx.custom_id)
		buttons = []
		if id == answer:
			for i in answers:
				buttons.append(create_button(style=ButtonStyle.green if i == id else ButtonStyle.gray, label=str(i), disabled=True))
		else:
			for i in answers:
				buttons.append(create_button(style=ButtonStyle.red if i == id else ButtonStyle.gray if i != answer else ButtonStyle.green, label=str(i), disabled=True))

		await comctx.edit_origin(embed=discord.Embed(title=question, description="Correct!" if id == answer else "Sorry, that's incorrect!", color=0x57f287 if id == answer else 0xed4245), components=[create_actionrow(*buttons)])



@slash.slash(description="Retrieve the last 10 messages of a channel.", guild_ids=guild_ids, options=[create_option(name="channel", description="The channel to get the messages from.", option_type=7, required=True)])
async def snipe(ctx, channel:discord.abc.GuildChannel):
	if not isinstance(channel, discord.TextChannel):
		print(logs)
		await ctx.send(f"{channel} is not a text channel.", hidden=True)
		return

	try:
		temp = logs[f"{channel.id}"]
		logExists = True
	except:
		logExists = False

	if logExists:
		description = ""
		for i in temp:
			description += f"{i}\n\n"
	else:
		await ctx.send(f"I do not have messages logged for {channel}.", hidden=True)
		return

	await ctx.send(embed=discord.Embed(title=f"Last Sent Messages in #{channel}", description=description, color=colors["blurple"]))



@slash.slash(description="Find the most recent 10 images sent in a channel.", guild_ids=guild_ids, options=[create_option(name="channel", description="The channel to get the images from.", option_type=7, required=True)])
async def lastImages(ctx, channel:discord.abc.GuildChannel):
	if not isinstance(channel, discord.TextChannel):
		await ctx.send(f"{channel} is not a text channel.", hidden=True)
		return

	msg = await ctx.send("Searching for images...")

	msg_list = []
	timestamp = datetime.utcnow()
	msg_num = 200
	iters = 1
	max = 10
	att_ct = 0
	searching = True
	while searching:
		msg_ct = 0
		async for i in channel.history(limit=msg_num, before=timestamp):
			msg_ct += 1
			if msg_ct == msg_num:
				timestamp = i.created_at
			if i.attachments != []:
				i.attachments.reverse()
				for j in i.attachments:
					if "image" in j.content_type and att_ct < 10:
						att_ct += 1
						msg_list.append([i.jump_url, j.url, att_ct])
		if att_ct < 10:
			iters += 1
		else:
			searching = False
		if iters == max:
			searching = False
		await msg.edit(content=f"Searched through {msg_num*iters} messages...")
	if msg_list == []:
		await msg.edit(content=f"Could not find any images in the most recent {msg_num*max} messages.")
		return
	await msg.edit(content="Images found!")
	emb = discord.Embed(title=f"Last Sent Images in #{channel}", color=colors["blurple"])
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
	await ctx.defer()

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
		text = text[:20]
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
	emb = discord.Embed(title="Reactions added!", description=description, color=colors["blurple"])
	await wait(1)
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
		text = text[:20]
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
		emb = discord.Embed(title="Reactions added!", description=description, color=colors["blurple"])
		await ctx.reply(embed=emb, components=[act_row])
	else:
		await ctx.reply("You need to reply to a message.")



@bot.command(name="h")
async def listCommands(ctx):
	await ctx.trigger_typing()
	emb = discord.Embed(title="Commands", color=colors["blurple"])
	pre = bot.command_prefix
	commands = [["r", "Adds reactions to the message replied to."], ["h", "Displays this message."]]
	for i in commands:
		emb.add_field(name=pre + i[0], value=f"{i[1]}\n")
	emb.set_footer(text="All commands are case insensitive.")
	await ctx.send(embed=emb)

bot.run(environ["token"])
