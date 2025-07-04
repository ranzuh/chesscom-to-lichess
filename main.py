from fasthtml.common import *
import httpx
from dotenv import load_dotenv
import os
from datetime import datetime
import parse


load_dotenv()

app = FastHTML(hdrs=(picolink, StyleX("styles.css")))


@app.get("/")
def home():
    inp = Input(
        id="user", name="chessuser", placeholder="Enter your Chess.com username"
    )
    form = Form(Group(inp, Button("Fetch")), hx_post="/games", target_id="games-list")
    info = P("Fetch your latest Chess.com games and analyse them easily in Lichess.")
    return Titled("Chess.com to Lichess", info, form, Ul(id="games-list"))


def fetch_latest_games(username: str) -> list[dict]:
    date = datetime.now()
    year_and_month = date.strftime("%Y/%m")
    url = f"https://api.chess.com/pub/player/{username}/games/{year_and_month}"
    res = httpx.get(url)
    res_dict = res.json()
    games: list[dict] = res_dict["games"]
    games.reverse()
    return games


def get_title(game: dict) -> str:
    headers = parse.findall('[{} "{}"]', game["pgn"])
    headers = {r[0]: r[1] for r in headers}
    date = headers["Date"]
    dt = datetime.strptime(date, "%Y.%m.%d")
    new_date = dt.strftime("%b %-d %Y")
    title = f"{new_date}, {headers["White"]} vs {headers["Black"]}, {headers["Result"]}"
    return title


@app.post("/games")
def get_list(chessuser: str):
    games = fetch_latest_games(chessuser)
    list_items = []
    for game in games:
        title = get_title(game)
        # send a POST request to /lichess with pgn as request parameter
        link = A("Analyse in Lichess", hx_post="/lichess", hx_vals={"pgn": game["pgn"]})
        list_items.append(Li(Span(title, cls="title"), link))
    return list_items


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
