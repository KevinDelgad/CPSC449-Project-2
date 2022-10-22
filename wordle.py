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
def index():
    return textwrap.dedent(
        """
        <h1>Welcome to Wordle 2.0!!!</h1>
        """
    )


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
@app.route("/user-auth/<string:username>/<string:password>", methods=["GET"])
async def userAuth( username, password ):
    db = await _get_db()
    # Selection query with raw queries
    select_query = "SELECT * FROM user WHERE username= :username AND passwrd= :password"
    values = {"username": username, "password": password}

    # Run the command
    result = await db.fetch_one( select_query, values )

    # Is the user registered?
    if result:
        return { "authenticated": "true" }, 200

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
    #is guessed word the answer
    if isAnswer is not None and len(isAnswer) >= 1:
        #update game status
        try:
            id_games = await db.execute(
                """
                UPDATE game set gstate = :status where gameid = :gameid
                """,values={"status":"Finished","gameid":currGame['gameid']}
            )
        except sqlite3.IntegrityError as e:
            abort(404, e)
        return {"guessedWord":currGame["word"], "Accuracy":u'\u2713'*5},201 #should return correct answer? 
    #if 1 then word is valid otherwise it isn't valid and also check if they exceed guess limit
    isValidGuess = await db.fetch_one("SELECT * from valid_word where valword = :word;", values={"word":currGame["word"]})
    guessNum = await db.fetch_one("SELECT guesses from game where gameid = :gameid",values={"gameid":currGame["gameid"]})
    accuracy = ""
    if(isValidGuess is not None and len(isValidGuess) >= 1 and guessNum[0] < 6):
        try: 
            #make a dict mapping each character and its position from the answer
            answord = await db.fetch_one("SELECT answord FROM answer as a, games as g  where g.gameid = :gameid and g.answerid = a.answerid",values={"gameid":currGame["gameid"]})
            ansDict = {}
            for i in range(len(answord[0])):
                ansDict[answord[0][i]] = i
            #compare location of guessed word with answer
            guess_word = currGame["word"]
            for i in range(len(guess_word)):
                if guess_word[i] in ansDict:
                    # print(ansDict.get(guess_word[i]))
                    if ansDict.get(guess_word[i]) == i:
                        accuracy += u'\u2713'
                    else:
                        accuracy += 'O'
                else:
                    accuracy += 'X'
            #insert guess word into guess table with accruracy
            id_guess = await db.execute("INSERT INTO guess(gameid,guessedword, accuracy) VALUES(:gameid, :guessedword, :accuracy)",values={"guessedword":currGame["word"],"gameid":currGame["gameid"],"accuracy":accuracy})
            #update game table's guess variable by decrementing it
            id_games = await db.execute(
                """
                UPDATE game set guesses = :guessNum where gameid = :gameid
                """,values={"guessNum":(guessNum[0]+1),"gameid":currGame['gameid']}
            )
            #if after updating game number of guesses reaches max guesses then mark game as finished 
            if(guessNum[0]+1 >= 6):
                #update game status as finished
                id_games = await db.execute(
                    """
                    UPDATE game set gstate = :status where gameid = :gameid
                    """,values={"status":"Finished","gameid":currGame['gameid']}
                )
                return currGame,202
        except sqlite3.IntegrityError as e:
            abort(404, e)
    else:
        #should return msg saying invalid word?
        return{"Error":"Invalid Word"}
    return {"guessedWord":currGame["word"], "Accuracy":accuracy},201

@app.route("/games/<string:username>/all", methods=["GET"])
async def all_games(username):
    db = await _get_db()

    userid = await db.fetch_one(
            "SELECT userid FROM user WHERE username = :username", values={"username":username})
    if userid:

        games_val = await db.fetch_all( "SELECT * FROM game as a where gameid IN (select gameid from games where userid = :userid) and a.gstate = :gstate;", values = {"userid":userid[0],"gstate":"In-progress"})
        
        if games_val is None or len(games_val) == 0:
            return { "Message": "No Active Games" },406

        return list(map(dict,games_val))

    else:
        abort(404)

@app.route("/games/<string:username>/<int:gameid>", methods=["GET"])
async def my_game(username,gameid):
    db = await _get_db()

    userid = await db.fetch_one(
            "SELECT userid FROM user WHERE username = :username", values={"username":username})
    if userid:

        guess_val = await db.fetch_all( "SELECT a.*, b.guesses, b.gstate FROM guess as a, game as b WHERE a.gameid = b.gameid and a.gameid = :gameid", values={"gameid":gameid})

        if guess_val is None or len(guess_val) == 0:
            
            return { "Message": "Not An Active Game" },406
        
        return list(map(dict,guess_val))

    else:
        abort(404)

@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409
