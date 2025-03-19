from fastapi import FatAPI

app = FastAPI()


@app.get('/')

def index():
	return 'hevy'
