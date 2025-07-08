# chesscom-to-lichess

A simple FastHTML app that fetches your latest games from Chess.com and provides easy one click access to analyse them in Lichess.

## Installation

```bash
pip install fasthtml python-dotenv parse
```

Add .env file to project root and write your Lichess API key there:

```bash
LICHESS_API_TOKEN=your_api_key_here
```

## Usage

```bash
python main.py
````

## To Do

- [ ] Add infinite scroll or load more rows functionality to the games table
- [ ] Add filters for eg. time control, dates?
