from fastapi import FastAPI

app = FastAPI(title="Atlas AI Financial Assistant")


@app.get("/")
def home():
    return {
        "message": "Atlas AI Financial Assistant is running 🚀"
    }