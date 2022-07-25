from os import environ
from datetime import datetime, timezone, timedelta
import discord
import googleapiclient.discovery

guilds = [409325808864460800]
bot = discord.Bot(debug_guilds=guilds)

master = []
search_terms = ["Ch. hololive-EN", "【NIJISANJI EN】", "Ch. HOLOSTARS-EN"]
options = []
offset = 5 # 5 = CDT, 6 = CST
centraltime = timezone(timedelta(hours=-offset))
last_updated = "?"

def stream_info():
	# Disable OAuthlib's HTTPS verification when running locally.
	# *DO NOT* leave this option enabled in production.
	environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

	api_service_name = "youtube"
	api_version = "v3"
	DEVELOPER_KEY = "AIzaSyClopzawTj8PCc-lzcDqI3yyUNokYpaGp4"

	youtube = googleapiclient.discovery.build(
		api_service_name, api_version, developerKey = DEVELOPER_KEY)

	global master; master = []
	video_ids = []

	request = youtube.search().list(
		part="snippet",
		eventType="upcoming",
		maxResults=50,
		q=f'"{search_terms[0]}" | "{search_terms[1]}" | "{search_terms[2]}"',
		type="video"
	)
	response = request.execute()

	to_remove = []
	for i in response["items"]:
		if (search_terms[0] not in i["snippet"]["channelTitle"]) and (search_terms[1] not in i["snippet"]["channelTitle"]) and (search_terms[2] not in i["snippet"]["channelTitle"]):
			to_remove.append(i)
	for i in to_remove:
		response["items"].remove(i)

	for i in response["items"]:
		video_ids.append(i["id"]["videoId"])

	request = youtube.videos().list(
		part="snippet,liveStreamingDetails",
		id=",".join(video_ids)
	)
	response = request.execute()

	# With Visual Studio, times are in UTC | With Heroku, times are in CT  
	for i in response["items"]:
		master.append([datetime.strptime(i["liveStreamingDetails"]["scheduledStartTime"], "%Y-%m-%dT%H:%M:%SZ").astimezone(timezone(timedelta(hours=-offset))), i["snippet"]["title"], i["snippet"]["channelTitle"], f"youtu.be/{i['id']}"])

def date_str(dt):
	return dt.strftime("%A, %B %d, %Y")

def str_date(string):
	return datetime.strptime(string, "%A, %B %d, %Y")

def time_str(dt):
	return dt.strftime("%H:%M")

class ui_view(discord.ui.View):
	@discord.ui.select( # the decorator that lets you specify the properties of the select menu
		placeholder = "Select day...", # the placeholder text that will be displayed if nothing is selected
		min_values = 1, # the minimum number of values that must be selected by the users
		max_values = 1, # the maxmimum number of values that can be selected by the users
		options = options
	)
	async def select_callback(self, select, interaction): # the function called when the user is done selecting options
		value = select.values[0]

		emb = discord.Embed(title=f"Schedule — {value}")
		emb.set_footer(text=f"All times in CT\nLast updated: {last_updated}")
		for i in master:
			if (i[0].year == str_date(value).year and i[0].month == str_date(value).month and i[0].day == str_date(value).day):
				emb.add_field(name=f"{i[2]} — {time_str(i[0])}", value=f"{i[1]}\n__{i[3]}__", inline=False)
		
		await interaction.response.edit_message(embed=emb, view=ui_view())



@bot.event
async def on_ready():
	print(datetime.now(centraltime))
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone"))

	channel = discord.utils.get(bot.get_all_channels(), name="dank-memer")
#	await channel.send(content="come on, do something")

@bot.slash_command(description="Update master list of videos")
async def update(ctx):
	await ctx.defer()
	stream_info()
	master.sort()
	global last_updated; last_updated = datetime.now(centraltime)
	await ctx.send_followup(content="Updated!", ephemeral=True)

@bot.slash_command(description="Gives the schedule")
async def schedule(ctx):
	now = datetime.now(centraltime)
	emb = discord.Embed(title=f"Schedule — {date_str(now)}")
	emb.set_footer(text=f"All times in CT\nLast updated: {last_updated}")
	dates = []
	for i in master:
		test_date = datetime(*[i[0].year, i[0].month, i[0].day])
		if test_date not in dates:
			dates.append(test_date)
		if (i[0].year == now.year and i[0].month == now.month and i[0].day == now.day):
			emb.add_field(name=f"{i[2]} — {time_str(i[0])}", value=f"{i[1]}\n__{i[3]}__", inline=False)
	for i in dates:
		options.append(discord.SelectOption(label=date_str(i)))
	
	await ctx.respond(embed=emb, view=ui_view())





# Use token when testing and environ["token"] for heroku
bot.run(environ["token"])