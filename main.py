from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import FileResponse
from pyppeteer import launch

app = FastAPI()

# Define a request model for the URL
class RenderRequest(BaseModel):
    url: str
    filename: str

async def fetch_rendered_html(url: str) -> str:
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url, {'waitUntil': 'domcontentloaded'})
    content = await page.content()
    await browser.close()
    return content

@app.post("/render/", response_class=HTMLResponse)
async def render_page(request: RenderRequest):
    try:
        rendered_html = await fetch_rendered_html(request.url)
        file_path = f"./{request.filename}"
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(rendered_html)

        return FileResponse(path=file_path, media_type='application/octet-stream', filename=request.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))