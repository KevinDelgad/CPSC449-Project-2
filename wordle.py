from cmath import exp
from pydoc import doc
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
    first_name: str
    last_name: str
    user_name: str
    password: str


@dataclasses.dataclass
class Game:
    username: str

@dataclasses.dataclass
class Guess:
    gameid: int
    word: str


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


@app.route("/", methods=["GET"])
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
        #Attempt to create new user in database
        id = await db.execute(
            """
            INSERT INTO user(fname, lname, username, passwrd)
            VALUES(:first_name, :last_name, :user_name, :password)
            """,
            user,
        )
    #Return 409 error if username is already in table
    except sqlite3.IntegrityError as e:
        abort(409, e)

    user["id"] = id
    return user, 201

# User authentication endpoint
@app.route("/user-auth", methods=["GET"])
async def userAuth( username, password ):
    db = await _get_db()
    # Selection query with placeholders
    # Best practice to avoid SQL injections
    select_query = "SELECT * FROM user WHERE username=%s AND passwrd=%s;"

    # Run the command
    results = db.execute(select_query, ( username, password ) )
    
    # Is the user registered?
    if results.fetch_all():
        return { "authenticated": True }, 200
    else:
        return 401, { "WWW-Authenticate": "Fake Realm" }


@app.route("/games/", methods=["POST"])
@validate_request(Game)
async def create_game(data):
    db = await _get_db()
    username = dataclasses.asdict(data)
    # Check if username is in the database
    valid_user = await db.fetch_one(
        "SELECT username FROM user WHERE username = :username", username
    )
    if valid_user:
        # Retrieve User Id from their username
        userid = await db.fetch_one(
            "SELECT userid FROM user WHERE username = :username", username
        )

        # Retrive random ID from the answers table
        word = await db.fetch_one(
            "SELECT answerid FROM answer ORDER BY RANDOM() LIMIT 1"
        )
        # Check if the retrived word is a repeat for the user, and if so grab a new word
        while await db.fetch_one(
            "SELECT answerid FROM games WHERE userid = :userid AND answerid = :answerid",
            values={"userid": userid[0], "answerid": word[0]},
        ):
            word = await db.fetch_one(
                "SELECT answerid FROM answer ORDER BY RANDOM() LIMIT 1"
            )

        # Create new game with 0 guesses
        query = "INSERT INTO game(guesses, gstate) VALUES(:guesses, :gstate)"
        values = {"guesses": 0, "gstate": "In-progress"}
        cur = await db.execute(query=query, values=values)

        # Create new row into Games table which connect with the recently connected game
        query = "INSERT INTO games(userid, answerid, gameid) VALUES(:userid, :answerid, :gameid)"
        values = {"userid": userid[0], "answerid": word[0], "gameid": cur}
        cur = await db.execute(query=query, values=values)

        return values, 201

    else:
        abort(404)


#Should validate to check if guess is in valid_word table
#if it is then insert into guess table 
#update game table by decrementing guess variable
#if word is not valid throw 404 exception
@app.route("/guess/",methods=["POST"])
@validate_request(Guess)
async def add_guess(data):
    db = await _get_db() 

    currGame = dataclasses.asdict(data)
    #checks whether guessed word is the answer for that game
    isAnswer= await db.fetch_one(
        "SELECT * FROM answer as a where (select count(*) from games where gameid = :gameid and answerid = a.answerid)>=1 and a.answord = :word;", currGame
        )
    print(isAnswer)
    #is guessed word the answer
    if isAnswer is not None and len(isAnswer) >= 1: #cigar is answer
        #update game status
        try:
            id_games = await db.execute(
                """
                UPDATE game set gstate = :status where gameid = :gameid
                """,values={"status":"Finished","gameid":currGame['gameid']}
            )
        except sqlite3.IntegrityError as e:
            abort(404, e)
        return currGame,201 #should return correct answer? 
    #if 1 then word is valid otherwise it isn't valid
    isValidGuess = await db.fetch_one("SELECT * from valid_word where valword = :word;", values={"word":currGame["word"]})
    print(isValidGuess)
    if(isValidGuess is not None and len(isValidGuess) >= 1):
        try: 
            #insert guess word into guess table
            print("Goes here")
            id_guess = await db.execute("INSERT INTO guess(gameid,guessedword, accuracy) VALUES(:gameid, :guessedword, :accuracy)",values={"guessedword":currGame["word"],"gameid":currGame["gameid"],"accuracy":"None"})
            #get current game number of guesses
            print("id_guess",id_guess)
            guessNum = await db.fetch_one("SELECT guesses from game where gameid = :gameid",values={"gameid":currGame["gameid"]})
            print("guessNum",guessNum[0])
            #update game table's guess variable by decrementing it
            id_games = await db.execute(
                """
                UPDATE game set guesses = :guessNum where gameid = :gameid
                """,values={"guessNum":(guessNum[0]+1),"gameid":currGame['gameid']}
            )
            print("id_game",id_games)
            #if after updating game number of guesses reaches max guesses then mark game as finished 
            if(guessNum[0]+1 == 6):
                #update game status as finished
                return currGame,202
        except sqlite3.IntegrityError as e:
            abort(404, e)
    else:
        #should return msg saying invalid word?
        abort(404)
    return currGame, 202
@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409
