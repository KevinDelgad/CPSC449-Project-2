import sqlite3
from quart import Quart, g, request, abort

# Variable to work with the quart object
app = Quart(__name__)

# Database connection
dbConn = sqlite3.connect("wordle.db")
# SQLite needs a cursor to execute commands
cursor = dbConn.cursor()

# User authentication endpoint
@app.route("/user-auth", methods=["GET"])
async def userAuth( username, password ):
    # Selection query with placeholders
    # Best practice to avoid SQL injections
    select_query = "SELECT * FROM user WHERE username=%s AND passwrd=%s"

    # Run the command
    results = cursor.execute( selection_query, ( username, password ) )

    # Is the user registered
    if results.fetchall():
        return { "authenticated": true }, 200
    else:
        # Return 401 and www-authenticate
        return 401, { "WWW-Authenticate": "Fake Realm" }
