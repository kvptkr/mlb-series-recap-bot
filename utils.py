from datetime import date, timedelta


def find_last_monday():
    today = date.today()
    # Calculate the difference in days between today and the last Monday
    days_to_last_monday = today.weekday() - 0  # 0 represents Monday
    if days_to_last_monday < 0:
        days_to_last_monday += 7  # If today is Monday, go back a week
    # Subtract the difference in days from today's date to get the last Monday
    last_monday = today - timedelta(days=days_to_last_monday)
    return last_monday


def find_last_friday():
    today = date.today()
    # Calculate the difference in days between today and the last Friday
    days_to_last_friday = today.weekday() - 4  # 4 represents Friday
    if days_to_last_friday < 0:
        days_to_last_friday += 7  # If today is Friday, go back a week
    # Subtract the difference in days from today's date to get the last Friday
    last_friday = today - timedelta(days=days_to_last_friday)
    return last_friday


# TODO: change this to just return the correct datastructure
def set_league_results(teams_data, series, league_results):
    for key, games in series.items():
        # sort all the games based on the game['game_datetime']
        home_runs = []
        away_runs = []
        home_wins = 0
        away_wins = 0
        for game in games:
            home_runs.append(
                {
                    "runs": game["home_score"],
                    "won": game["home_score"] > game["away_score"],
                }
            )
            away_runs.append(
                {
                    "runs": game["away_score"],
                    "won": game["away_score"] > game["home_score"],
                }
            )
            if game["home_score"] > game["away_score"]:
                home_wins += 1
            else:
                away_wins += 1
        league_results.append(
            {
                "home_team": teams_data[key[0]]["name"],
                "away_team": teams_data[key[1]]["name"],
                "home_team_won": home_wins >= away_wins,
                "away_team_won": away_wins >= home_wins,
                "home_team_swept": home_wins > 1 and away_wins == 0,
                "away_team_swept": away_wins > 1 and home_wins == 0,
                "home_runs": home_runs,
                "away_runs": away_runs,
            }
        )
