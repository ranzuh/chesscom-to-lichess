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
    inp = Input(id="user", name="chessuser", placeholder="Enter your Chess.com username")
    form = Form(Group(inp, Button("Fetch")), hx_post="/games", target_id="table-body")
    info = P("Fetch your latest Chess.com games and analyse them easily in Lichess.")
    table = Table(Thead(id="table-head"), Tbody(id="table-body"))
    return Titled("Chess.com to Lichess", info, form, table)

def fetch_latest_games(username: str) -> list[dict]:
    year_and_month = datetime.now().strftime("%Y/%m")
    url = f"https://api.chess.com/pub/player/{username}/games/{year_and_month}"
    res = httpx.get(url).json()
    games: list[dict] = res["games"]
    # reverse to have latest games first
    games.reverse()
    return games

def get_columns(game: dict):
    headers = parse.findall('[{} "{}"]', game["pgn"])
    headers = {r[0]: r[1] for r in headers}
    date = headers["Date"]
    dt = datetime.strptime(date, "%Y.%m.%d")
    new_date = dt.strftime("%b %-d %Y")
    columns = [
        Td(new_date),
        Td(f"{headers["White"]} vs {headers["Black"]}"),
        Td(headers["Result"]),
    ]
    return columns

@app.post("/games")
def update_table(chessuser: str):
    games = fetch_latest_games(chessuser)
    rows = []
    for game in games:
        columns = get_columns(game)
        # send a POST request to /lichess with pgn as request parameter
        link = A("Analyse in Lichess", hx_post="/lichess", hx_vals={"pgn": game["pgn"]})
        rows.append(Tr(*columns, Td(link)))
    # htmx requires to use <template> here as <thead> "can’t stand on their own in the DOM"
    header = Template(
        Thead(
            Tr(Th("Date"), Th("Players"), Th("Result"), Th("")),
            id="table-head",
            hx_swap_oob="true",  # swap <thead> with this element
        )
    )
    clear_input = Input(
        id="user",
        name="chessuser",
        placeholder="Enter your Chess.com username",
        hx_swap_oob="true",  # replaces the <input> with this element
    )
    return rows, header, clear_input

@app.post("/lichess")
def paste_to_lichess(pgn: str):
    url = "https://lichess.org/api/import"
    lichess_token = os.getenv("LICHESS_API_TOKEN")
    headers = {"Authorization": f"Bearer {lichess_token}"}
    data = {"pgn": pgn}
    res = httpx.post(url, headers=headers, json=data).json()
    return Redirect(res["url"])

serve()
