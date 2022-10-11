import sqlite3
import databases
import toml
from quart import Quart, g, request, abort

# Variable to work with the quart object
app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

# Database connection
dbConn = Database('sqlite+aiosqlite:/var/wordle.db')
# SQLite needs a cursor to execute commands
cursor = dbConn.cursor()

async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database

def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db

# User authentication endpoint
@app.route("/user-auth", methods=["GET"])
async def userAuth( username, password ):
    # Selection query with placeholders
    # Best practice to avoid SQL injections
    select_query = "SELECT * FROM user WHERE username=%s AND passwrd=%s;"

    # Run the command
    results = cursor.execute( selection_query, ( username, password ) )

    # Is the user registered?
    if results.fetch_all():
        return { "authenticated": true }, 200
    else:
        # Return 401 and www-authenticate
        return 401, { "WWW-Authenticate": "Fake Realm" }
