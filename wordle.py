from cmath import exp
import databases
import collections
import dataclasses
import sqlite3
import textwrap

import databases
import toml

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

@dataclasses.dataclass
class User:
    first_name: str;
    last_name: str;
    user_name: str;
    password: str;

@dataclasses.dataclass
class Game:
    username: str;


async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()


@app.route("/", methods=['GET'])
async def test():
    db = await _get_db()
    all_answers = await db.fetch_all("SELECT * FROM answer;")
    return list(map(dict, all_answers))

@app.route("/users/", methods=["POST"])
@validate_request(User)
async def create_user(data):
    db = await _get_db()
    user = dataclasses.asdict(data)
    try:
        id = await db.execute(
            """
            INSERT INTO user(fname, lname, username, passwrd)
            VALUES(:first_name, :last_name, :user_name, :password)
            """,
            user
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    user["id"] = id
    return user, 201, {"Location": f"/users/{id}"}

@app.route("/games/", methods=["POST"])
@validate_request(Game)
async def create_game(data):
    db = await _get_db()
    username = dataclasses.asdict(data)
    valid_user = await db.fetch_one("SELECT username FROM user WHERE username = :username", username)
    if(valid_user):
        word = await db.fetch_one("SELECT * FROM answer ORDER BY RANDOM() LIMIT 1")
        userid = await db.fetch_one("SELECT userid FROM user WHERE username = :username", username)
        
        try:
            query = "INSERT INTO game(guesses, gstate) VALUES(:guesses, :gstate)"
            values={"guesses": 0, "gstate": "In-progress"}
            await db.execute(query=query, values=values)
        except sqlite3.IntegrityError as e:
            abort(409, e)
            
        return dict(userid)
    else:
        abort(404)    