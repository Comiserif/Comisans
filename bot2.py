from os import environ
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import tasks
import googleapiclient.discovery

guilds = [409325808864460800]
bot = discord.Bot(debug_guilds=guilds)

offset = 5 # 5 = CDT, 6 = CST
centraltime = timezone(timedelta(hours=-offset))
fifteen = timedelta(minutes=15)

master = []
search_terms = ["Ch. hololive-EN", "【NIJISANJI EN】", "Ch. HOLOSTARS-EN"]
select_options = []
placeholder = []

date_format = "%A, %B %d, %Y"
time_format = "%H:%M"
last_updated = "?"

def stream_info():
	# Disable OAuthlib's HTTPS verification when running locally.
	# *DO NOT* leave this option enabled in production.
	environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

	api_service_name = "youtube"
	api_version = "v3"
	# Use API key when testing and environ["api_key"] for heroku
	DEVELOPER_KEY = environ["api_key"]

	youtube = googleapiclient.discovery.build(
		api_service_name, api_version, developerKey = DEVELOPER_KEY)

	global last_updated
	master.clear()
	to_remove = []
	video_ids = []

	request = youtube.search().list(
		part="snippet",
		eventType="upcoming",
		maxResults=50,
		q=f'"{search_terms[0]}" | "{search_terms[1]}" | "{search_terms[2]}"',
		type="video"
	)
	response = request.execute()

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
		master.append([datetime.strptime(i["liveStreamingDetails"]["scheduledStartTime"], "%Y-%m-%dT%H:%M:%SZ").astimezone(centraltime), i["snippet"]["title"], i["snippet"]["channelTitle"], f"https://youtu.be/{i['id']}", i["snippet"]["liveBroadcastContent"]])
	master.sort()
	last_updated = datetime.now(centraltime)

	dates = []
	for i in master:
		for j in search_terms:
			if j in i[2]:
				i[2] = i[2][:i[2].index(j)]
			last_char = len(i[2])-1
			if i[2][last_char] == " ":
				i[2] = i[2][:last_char]
		test_date = datetime(i[0].year, i[0].month, i[0].day)
		if test_date not in dates:
			dates.append(test_date)
	select_options.clear()
	for i in dates:
		select_options.append(discord.SelectOption(label=date_str(i)))

def date_str(dt):
	return dt.strftime(date_format)

def time_str(dt):
	return dt.strftime(time_format)

def update_placeholder(dt):
	placeholder.clear()
	placeholder.append(date_str(dt))

def emb_init(now, loop=False):
	emb = discord.Embed(title = f"Schedule — {date_str(now)}" + (f" {time_str(now)}-{time_str(now + fifteen)}" if loop else ""))
	emb.set_footer(text=f"All times in CT\nLast updated: {last_updated}")
	for i in master:
		if (not loop and [i[0].year, i[0].month, i[0].day] == [now.year, now.month, now.day]) or (loop and now <= i[0] <= now + fifteen) or (loop and i[4] == "live"):
			match i[4]:
				case "upcoming":
					emoji = "🔵"
				case "live":
					emoji = "🔴"
				case _:
					emoji = "⚫"
			emb.add_field(name=f"{emoji} {i[2]} — {time_str(i[0])}", value=f"{i[1]}\n__[{i[3]}]({i[3]})__", inline=False)
	return emb

class ui_view(discord.ui.View):
	@discord.ui.select(
		row=0,
		placeholder=placeholder[0],
		min_values=1,
		max_values=1,
		options=select_options
	)
	async def select_callback(self, selection, interaction):
		await interaction.response.edit_message(embed=emb_init(datetime.strptime(selection.values[0], date_format)), view=ui_view())

	@discord.ui.button(label="Close Schedule", row=1, style=discord.ButtonStyle.danger)
	async def button_callback(self, button, interaction):
		await interaction.response.edit_message(content="<:kronii:904569631094767626>", embed=None, view=None)



@tasks.loop(minutes=15)
async def update_loop():
	stream_info()
	emb = emb_init(datetime.now(centraltime), True)
	if emb.fields:
		channel = bot.get_channel(738399795491635220)
		await channel.send(embed=emb)



@bot.event
async def on_ready():
	print(datetime.now(centraltime))
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="everyone"))

	update_loop.start()

	channel = discord.utils.get(bot.get_all_channels(), name="dank-memer")
#	await channel.send(content="come on, do something")

@bot.slash_command(description="Update master list of videos")
async def update(ctx):
	await ctx.defer(ephemeral=True)
	stream_info()
	await ctx.respond(content="Updated!")

@bot.slash_command(description="Gives the schedule")
async def schedule(ctx):
	await ctx.respond(embed=emb_init(datetime.now(centraltime)), view=ui_view())





# Use token when testing and environ["token"] for heroku
bot.run(environ["token"])