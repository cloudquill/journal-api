from fastapi import FastAPI

from controllers import journal_router

app = FastAPI()
app.include_router(journal_router.router)