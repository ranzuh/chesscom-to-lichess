from fasthtml.common import *
import httpx
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = FastHTML(hdrs=(picolink, StyleX("styles.css")))


def fetch_latest_games(username: str):
    date = datetime.now()
    year_and_month = date.strftime("%Y/%m")
    url = f"https://api.chess.com/pub/player/{username}/games/{year_and_month}"
    res = httpx.get(url)
    res_dict = res.json()
    games: list = res_dict["games"]
    games.reverse()
    return games


@app.get("/")
def home():
    games = fetch_latest_games("ranzuh")
    list_items = []
    for game in games:
        title = f"{game["white"]["username"]} vs. {game["black"]["username"]}"
        # send a POST request to /lichess with pgn as request parameter
        link = A("Analyse in Lichess", hx_post="/lichess", hx_vals={"pgn": game["pgn"]})
        list_items.append(Li(Span(title, cls="title"), link))
    return Titled("Chess.com to Lichess", H2("Games this month"), Ul(*list_items))


@app.post("/lichess")
def paste_to_lichess(pgn: str):
    url = "https://lichess.org/api/import"
    lichess_token = os.getenv("LICHESS_API_TOKEN")
    headers = {"Authorization": f"Bearer {lichess_token}"}
    data = {"pgn": pgn}
    res = httpx.post(url, headers=headers, json=data)
    res_dict = res.json()
    url = res_dict["url"]
    return Redirect(url)


serve()
