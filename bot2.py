from os import environ
from datetime import datetime, timezone, timedelta
import discord
from discord.ext import tasks
import googleapiclient.discovery
from urllib.request import urlopen

guilds = [409325808864460800]
bot = discord.Bot(debug_guilds=guilds)

offset = 5 # 5 = CDT, 6 = CST
centraltime = timezone(timedelta(hours=-offset))
fifteen = timedelta(minutes=15)

master = []
search_terms = ["Ch. hololive-EN", "【NIJISANJI EN】", "Ch. HOLOSTARS-EN"]
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
	video_ids = []

	request = youtube.search().list(
		part="snippet",
		eventType="upcoming",
		maxResults=50,
		q=f'"{search_terms[0]}" | "{search_terms[1]}" | "{search_terms[2]}"',
		type="video"
	)
	response = request.execute()
	last_updated = datetime.now(centraltime)

	for i in response["items"]:	
		if not (search_terms[0] in i["snippet"]["channelTitle"] or search_terms[1] in i["snippet"]["channelTitle"] or search_terms[2] in i["snippet"]["channelTitle"]):
			response["items"].remove(i)
		video_ids.append(i["id"]["videoId"])

	request = youtube.videos().list(
		part="snippet,liveStreamingDetails",
		id=",".join(video_ids)
	)
	response = request.execute()

	# With Visual Studio, times are in UTC | With Heroku, times are in CT
	for i in response["items"]:
		master.append({"time":datetime.strptime(i["liveStreamingDetails"]["scheduledStartTime"], "%Y-%m-%dT%H:%M:%SZ").astimezone(centraltime), "title":i["snippet"]["title"], "channelTitle":i["snippet"]["channelTitle"], "link":f"https://youtu.be/{i['id']}", "status":i["snippet"]["liveBroadcastContent"], "thumbnail":f"https://i.ytimg.com/vi/{i['id']}/maxresdefault.jpg"})
	master.sort(key=get_time)

	dates = []
	for i in master:
		for j in search_terms:
			i["channelTitle"] = i["channelTitle"].replace(j, "")
		last_char = len(i["channelTitle"])-1
		if i["channelTitle"][last_char] == " ":
			i["channelTitle"] = i["channelTitle"][:last_char]

		html = urlopen("https://virtualyoutuber.fandom.com/wiki/" + i["channelTitle"].replace(" ", "_")).read().decode("utf-8")
		html_index = html.find("Emoji")
		if html_index == -1:
			i["emojis"] == ""
		start_index = html_index + len('Emoji</h3>\n\n\n\t<div class="pi-data-value pi-font">')
		raw_str = html[start_index:start_index+7]
		i["emojis"] = raw_str[:raw_str.find("<")].replace(" ", "")

		test_date = datetime(*ymd(i["time"]))
		if test_date not in dates:
			dates.append(test_date)
	select_options.clear()
	for i in dates:
		select_options.append(discord.SelectOption(label=to_str(i, date_format)))

def get_time(i):
	return i["time"]

def ymd(dt):
	return [dt.year, dt.month, dt.day]

def to_str(dt, format):
	return dt.strftime(format)

def emb_init(dt, loop=False):
	emb = discord.Embed(title = to_str(dt, date_format) + (f" {to_str(dt, time_format)}-{to_str(dt + fifteen, time_format)}" if loop else ""))
	emb.set_footer(text=f"All times in CST\nLast updated: {last_updated}")
	image_set = False
	for i in master:
		if (not loop and ymd(i["time"]) == ymd(dt)) or (loop and dt <= i["time"] <= dt + fifteen):
			match i["status"]:
				case "upcoming":
					emoji = "blue"
				case "live":
					emoji = "red"
				case _:
					emoji = "black"
			emb.add_field(name=f"{'' if loop else f':{emoji}_circle: '}{i['emojis']} {i['channelTitle']} — {to_str(i['time'], time_format)}", value=f"{i['title']}\n__[{i['link']}]({i['link']})__", inline=False)
			if datetime.now(centraltime) < i["time"] and not image_set:
				emb.set_image(url=i["thumbnail"])
				image_set = True
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
