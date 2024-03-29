from os import environ, remove
from datetime import datetime, timezone, timedelta
from random import randrange, choice
from math import ceil
from PIL import Image, ImageFont, ImageDraw, ImageColor
from asyncio import sleep
import discord
from discord.ext import commands

from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
#, wait_for_component, create_select, create_select_option
from discord_slash.model import ButtonStyle, ContextMenuType
from discord_slash.context import ComponentContext, MenuContext

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

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
offset = 5 # 5 = CDT, 6 = CST
centraltz = timezone(timedelta(hours=-offset))

colors = {"blurple" : 0x5865f2, "poke" : 0xfe9ac9}
symbols = {"hedgehog" : "\U0001f994", "present" : "\ufe0f", "newline" : "\u000a"}
logs = {}
mods =	[715327315974029333, 268849207039754241]
pokemon = [[], [], [], [], [], [], [], []]
shapes = [["\u2764" + symbols["present"], "\U0001f499", "\U0001f49a"], ["\U0001f534", "\U0001f535", "\U0001f7e2"], ["\U0001f7e5", "\U0001f7e6", "\U0001f7e9"]] # red blue green heart circle square
shiny = [["Gastly", 715327315974029333], ["Beldum", 409205134028046346], ["Riolu", 345659592736243714], ["Sneasel", 441046114792243215], ["Dreepy", 542542697488187403], ["Cubchoo", 268849207039754241], ["Porygon", 263440201118908418], ["Snorlax", 821456684462637127], ["Ralts", 776134910548639828]]
shiny.sort()
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def ytCheck():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_301225460056-7ee1kljjt97a7el110jr0a5j132sgn4r.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.search().list(
        part="snippet",
        channelId="UCIM92Ok_spNKLVB5TsgwseQ",
        eventType="upcoming",
        maxResults=25,
        type="video"
    )
    response = request.execute()

    print(response)

def randomColor():
	return discord.Colour(randrange(0, 16777215))



@bot.event
async def on_connect():
	print(datetime.now(centraltz))

@bot.event
async def on_ready():
	global poketwo
	print("Hello World!")
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone | ;h"))
	poketwo = await bot.fetch_user(716390085896962058)
	poketwo = poketwo.avatar_url

#	dm = await discord.utils.get(bot.get_all_members(), name="Comiserif").create_dm()
#	await dm.send("what")

	channel = discord.utils.get(bot.get_all_channels(), name="dank-memer")
#	msg = await channel.send(content="", file=None)
#	for i in []:
#		msg = await channel.fetch_message(i)
#		await msg.delete()

guild_ids = [645111346274500614, 409325808864460800]



@bot.event
async def on_message(msg):

	await bot.process_commands(msg)

	try:
		logs[f"{msg.channel.id}"]
	except:
		logs[f"{msg.channel.id}"] = []
	attach = ""
	for i in msg.attachments:
		attach += f"{i.url}\n"
	embeds = ""
	for i in msg.embeds:
		embeds += f"{i.to_dict()}\n"
	
	logs[f"{msg.channel.id}"].insert(0, (f"——{msg.author}{' -> ' + (await msg.channel.fetch_message(msg.reference.message_id)).author.name if msg.reference != None else ''} {msg.created_at} Message ID: {msg.id}——\n{msg.clean_content + symbols['newline'] if msg.clean_content != '' else ''}{attach + symbols['newline'] if attach != '' else ''}{embeds if embeds != '' else ''}\n\n"))
	
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
async def sendcomic(ctx, text:str, color:str="#f0f"):
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
		if pokemon[i] != []:
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
	await sleep(6)
	await msg.edit(embed=discord.Embed(title=question, colors=colors["blurple"]), components=[create_actionrow(*buttons)])

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



@slash.subcommand(base="logs", name="channel", description="Retrieve a channel's messages.", guild_ids=guild_ids, options=[create_option(name="channel", description="The channel to get the messages from.", option_type=7, required=True)])
async def logs_channel(ctx, channel:discord.abc.GuildChannel):
	if not isinstance(channel, discord.TextChannel):
		await ctx.send(f"{channel} is not a text channel.", hidden=True)
		return

	name = f"{channel.name}.txt"
	try:
		temp = logs[f"{channel.id}"]
	except:
		await ctx.send(f"I do not have messages logged for {channel}.", hidden=True)
		return

	with open(name, "x") as f:
		for i in temp:
			f.write(i)

	await ctx.send(file=discord.File(name))
	remove(name)



@slash.subcommand(base="logs", name="channel_id", description="Retrieve a channel's messages.", guild_ids=guild_ids, options=[create_option(name="channel_id", description="The ID of the channel to get the messages from.", option_type=3, required=True)])
async def logs_id(ctx, channel_id:str):
	channel = bot.get_channel(int(channel_id))
	if channel == None or channel.guild.id != ctx.guild_id:
		await ctx.send("channel_id needs to be the ID of a channel in this server.")
		return

	name = f"{channel.name}.txt"
	try:
		temp = logs[f"{channel.id}"]
	except:
		await ctx.send(f"I do not have messages logged for {channel}.", hidden=True)
		return

	with open(name, "x") as f:
		for i in temp:
			f.write(i)

	await ctx.send(file=discord.File(name))
	remove(name)



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
					if att_ct < 10:
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
	emb = discord.Embed(title=f"Last Sent Images in #{channel}", description="If nothing is showing here, it is probably a video.", color=colors["blurple"])
	emb.set_image(url=msg_list[0][1])
	emb.set_footer(text=f"1/{len(msg_list)}")

	def init_buttons():
		return create_actionrow(create_button(style=ButtonStyle.blue, emoji="\u2b05" + symbols["present"], custom_id="l"), create_button(style=ButtonStyle.blue, emoji="\u27a1" + symbols["present"], custom_id="r"), create_button(style=ButtonStyle.URL, label="Go to Message", url=msg_list[0][0]), create_button(style=ButtonStyle.URL, label="Image Link", url=msg_list[0][1]))

	act_row = init_buttons()
	await msg.edit(content=None, embed=emb, components=[act_row])

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



# Use when context menus come to mobile
# Remove react(), ;r, and ;h
eventually = '''@slash.context_menu(target=ContextMenuType.MESSAGE, name="React With Letters", guild_ids=guild_ids)
async def react(ctx: MenuContext):
	await ctx.send("Enter the text to react to the message with in chat.", hidden=True)
	def check(m):
		return ctx.author_id == m.author.id
	msg = await bot.wait_for('message', check=check)
	text = msg.content
	await msg.delete()

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

	emojis = []
	for i in text:
		for j in range(len(letters)):
			if letters[j] == i:
				emojis.append(chr(127462+j))
		for j in range(len(numbers)):
			if numbers[j] == i:
				emojis.append(chr(48+j) + symbols["present"] + "\u20e3")
	for i in emojis:
		await ctx.target_message.add_reaction(i)
	act_row = create_actionrow(create_button(style=ButtonStyle.URL, label="Go to Message", url=ctx.target_message.jump_url))
	emb = discord.Embed(title="Reactions added!", description=description, color=colors["blurple"])
	await ctx.target_message.channel.send(embed=emb, components=[act_row])'''



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
	await sleep(1)
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
		for i in ctx.guild.text_channels:
			try:
				msg = await i.fetch_message(ctx.message.reference.message_id)
			except:
				continue
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