from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.api import router as api_router  # Renaming to avoid confusion
from database import init_db  # Ensure this import path is correct
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI()

# Mount static files for serving CSS, JS, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize the database on startup
@app.on_event("startup")
async def on_startup():
    await init_db()

# Include authentication router
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Include the main API router
app.include_router(api_router, prefix="/api", tags=["api"])

# Set up the template directory
templates = Jinja2Templates(directory="templates")

# Root endpoint to render an HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/search")
async def search_page(request: Request):
    return templates.TemplateResponse("search_results.html", {"request": request})

# Test endpoint for API
@app.get("/api/test")
def api_test():
    return {"message": "Welcome to the ShopBot API!"}
