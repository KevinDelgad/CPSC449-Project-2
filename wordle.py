from quart import Quart, request

app = Quart(__name__)

@app.route('/')
async def hello():
    return  'hello'

app.run() 