from collections import defaultdict
import jinja2
from datetime import date, timedelta
import calendar
import statsapi
from constants import teams_data
from utils import find_last_friday, find_last_monday, set_league_results
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image

# Load the Jinja2 template
template_loader = jinja2.FileSystemLoader("templates")
template_env = jinja2.Environment(loader=template_loader)
template = template_env.get_template("./template.html")

end_date = date.today() - timedelta(days=1)
start_date = None


if (
    end_date.weekday() == calendar.FRIDAY
):  # makes the assumption that we always run this on a Friday for mid-week, this is wrong but fine for now
    start_date = find_last_monday()
    title = "Midweek Series Recap"
    tweet_text = f"Midweek Recap - {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"
else:
    start_date = find_last_friday()
    title = "Weekend Series Recap"
    tweet_text = f"Weekend Recap - {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"


try:
    games = statsapi.schedule(
        date=None,
        start_date=start_date,
        end_date=end_date,
    )
except:
    breakpoint()


al_series = defaultdict(list)
nl_series = defaultdict(list)
il_series = defaultdict(list)

for game in games:
    home_team_id = game["home_id"]
    away_team_id = game["away_id"]
    if teams_data[home_team_id]["al"] and teams_data[away_team_id]["al"]:
        al_series[(home_team_id, away_team_id)].append(game)
    elif teams_data[home_team_id]["al"] and not teams_data[away_team_id]["al"]:
        il_series[(home_team_id, away_team_id)].append(game)
    elif not teams_data[home_team_id]["al"] and teams_data[away_team_id]["al"]:
        il_series[(home_team_id, away_team_id)].append(game)
    else:
        nl_series[(home_team_id, away_team_id)].append(game)


american_league_results = []
national_league_results = []
interleague_results = []


set_league_results(teams_data, al_series, american_league_results)
set_league_results(teams_data, nl_series, national_league_results)
set_league_results(teams_data, il_series, interleague_results)


# Render the template with the data
template_vars = {
    "american_league": american_league_results,
    "national_league": national_league_results,
    "interleague": interleague_results,
    "title": title,
}
html_content = template.render(template_vars)
# write html to file called table.html

with open("table.html", "w") as f:
    f.write(html_content)


options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=800,1000")
driver = webdriver.Chrome(options=options)


path = f'file://{os.path.abspath("./table.html")}'
driver.get(path)
driver.maximize_window()
screenshot_obj = driver.save_screenshot("screenshot.png")

# Crop the screenshot based on the table size
# from PIL import Image

num_games = max(
    len(american_league_results), len(national_league_results), len(interleague_results)
)

img = Image.open("screenshot.png")
width = img.width
height = (num_games * 66.6) + 200
crop_area = (0, 0, width, height)
cropped_img = img.crop(crop_area)
cropped_img.save("screenshot.png")

driver.quit()


import tweepy


bearer = os.environ.get("BEARER_TOKEN")
api_key = os.environ.get("API_KEY")
api_secret = os.environ.get("API_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")
access_token = os.environ.get("ACCESS_TOKEN")
access_secret = os.environ.get("ACCESS_SECRET")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")


auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)
media_id = api.media_upload(filename="screenshot.png").media_id
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_secret,
)
client.create_tweet(text=tweet_text, media_ids=[media_id])
