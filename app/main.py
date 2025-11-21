from fastapi import FastAPI

app = FastAPI(title="LifeAdmin AI")

@app.get("/")
def root():
    return {"message": "LifeAdmin AI backend is running"}
