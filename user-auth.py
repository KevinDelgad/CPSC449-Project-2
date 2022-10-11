import sqlite3
import databases
import toml
from quart import Quart, g, request, abort

# Variable to work with the quart object
app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

# Database connection
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
    db = _get_db()
    # Selection query with placeholders
    # Best practice to avoid SQL injections
    select_query = "SELECT * FROM user WHERE username=%s AND passwrd=%s;"

    # Run the command
    results = db.execute( selection_query, ( username, password ) )

    # Is the user registered?
    if results.fetch_all():
        return { "authenticated": true }, 200
    else:
        return 401, { "WWW-Authenticate": "Fake Realm" }
