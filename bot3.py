from os import environ
from datetime import datetime, timezone, timedelta
import googleapiclient.discovery

offset = 5 # 5 = CDT, 6 = CST
centraltime = timezone(timedelta(hours=-offset))

master = []
playlist = []
last_updated = "?"

def update():
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
	playlist.clear()

	playlist_req = youtube.playlists().list(
		part="snippet",
		channelId="UC3I5CqaiCU-rlrlr59CHQRg",
		maxResults=50
	)
	playlist_resp = playlist_req.execute()
	last_updated = datetime.now(centraltime)

	for i in playlist_resp["items"]:	
		video_req = youtube.playlistitems().list(
			part="snippet",
			playlistId=i["id"],
			maxResults=150
		)
		video_resp = video_req.execute()
		for j in video_resp["items"]:
			playlist.append({"title":j["snippet"]["title"], "video_id":j["resourceId"]["videoId"]})
		master.append(playlist)



