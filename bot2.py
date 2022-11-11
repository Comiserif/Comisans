from os import environ
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import tasks
import googleapiclient.discovery

guilds = [409325808864460800]
bot = discord.Bot(debug_guilds=guilds)

offset = 6 # 5 = CDT, 6 = CST
centraltime = timezone(timedelta(hours=-offset))
fifteen = timedelta(minutes=15)

master = []
search_terms = ["Ch. hololive-EN", "【NIJISANJI EN】", "Ch. HOLOSTARS-EN"]
oshi_marks = {"Mori Calliope":"skull", "Takanashi Kiara":"chicken", "Ninomae Ina'nis":"octopus", "Gawr Gura":"trident", "Watson Amelia":"mag_right", "IRyS":"gem"}
select_options = []

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
			i[2] = i[2].replace(j, "")
		last_char = len(i[2])-1
		if i[2][last_char] == " ":
			i[2] = i[2][:last_char]
		i.append(oshi_marks[i[2]])
		test_date = datetime(i[0].year, i[0].month, i[0].day)
		if test_date not in dates:
			dates.append(test_date)
	select_options.clear()
	for i in dates:
		select_options.append(discord.SelectOption(label=to_str(i, date_format)))

def to_str(dt, format):
	return dt.strftime(format)

def emb_init(dt, loop=False):
	emb = discord.Embed(title = f"Schedule — {to_str(dt, date_format)}" + (f" {to_str(dt, time_format)}-{to_str(dt + fifteen, time_format)}" if loop else ""))
	emb.set_footer(text=f"All times in CST\nLast updated: {last_updated}")
	for i in master:
		if (not loop and [i[0].year, i[0].month, i[0].day] == [dt.year, dt.month, dt.day]) or (loop and dt <= i[0] <= dt + fifteen):
			match i[4]:
				case "upcoming":
					emoji = "blue"
				case "live":
					emoji = "red"
				case _:
					emoji = "black"
			emb.add_field(name=f":{emoji}_circle: :{i[5]}: {i[2]} — {to_str(i[0], time_format)}", value=f"{i[1]}\n__[{i[3]}]({i[3]})__", inline=False)
	for i in range(len(select_options)):
		select_options[i].label = select_options[i].label.replace("\u25b6 ", "")
		if select_options[i].label == to_str(dt, date_format):
			select_options[i].label = "\u25b6 " + select_options[i].label
	return emb

class ui_view(discord.ui.View):
	@discord.ui.select(
		row=0,
		placeholder="Select day...",
		min_values=1,
		max_values=1,
		options=select_options
	)
	async def select_callback(self, selection, interaction):
		emb = emb_init(datetime.strptime(selection.values[0], date_format))
		await interaction.response.edit_message(embed=emb, view=ui_view())

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
	emb = emb_init(datetime.now(centraltime))
	await ctx.respond(embed=emb, view=ui_view())





# Use token when testing and environ["token"] for heroku
bot.run(environ["token"])