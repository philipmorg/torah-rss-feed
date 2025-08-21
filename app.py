from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime, timedelta
import os

from torah_calendar import TorahCalendar
from sefaria_client import SefariaClient
from rss_generator import RSSGenerator
from cache import FileCache

app = FastAPI(title="Torah RSS Feed", description="Daily and Weekly Torah Portions")
cache = FileCache()
sefaria = SefariaClient()
calendar = TorahCalendar()
rss_gen = RSSGenerator()

@app.get("/")
async def root():
    return HTMLResponse("""
    <html><body>
    <h1>Torah RSS Feeds</h1>
    <ul>
        <li><a href="/feeds/weekly">/feeds/weekly</a> - Weekly Torah Portions</li>
        <li><a href="/feeds/daily">/feeds/daily</a> - Daily Torah Portions (weekly divided by 7)</li>
        <li><a href="/feeds/weekly/diaspora">/feeds/weekly/diaspora</a> - Diaspora schedule</li>
        <li><a href="/feeds/weekly/israel">/feeds/weekly/israel</a> - Israel schedule</li>
    </ul>
    <p>All feeds include full JPS English text.</p>
    </body></html>
    """)

@app.get("/feeds/weekly")
@app.get("/feeds/weekly/{location}")
async def weekly_feed(location: str = "diaspora"):
    cache_key = f"weekly_{location}"
    
    # Check cache (refresh every 6 hours)
    cached = cache.get(cache_key, max_age_hours=6)
    if cached:
        return Response(content=cached, media_type="application/rss+xml")
    
    # Get current Torah portion
    parasha = calendar.get_current_parasha(location)
    torah_text = await sefaria.get_torah_portion(parasha)
    
    # Generate RSS
    rss_content = rss_gen.generate_weekly_feed(parasha, torah_text, location)
    
    # Cache result
    cache.set(cache_key, rss_content)
    
    return Response(content=rss_content, media_type="application/rss+xml")

@app.get("/feeds/daily")
@app.get("/feeds/daily/{location}")
async def daily_feed(location: str = "diaspora"):
    cache_key = f"daily_{location}"
    
    # Check cache (refresh every 2 hours)
    cached = cache.get(cache_key, max_age_hours=2)
    if cached:
        return Response(content=cached, media_type="application/rss+xml")
    
    # Get current week's Torah portion and divide by days
    parasha = calendar.get_current_parasha(location)
    daily_portions = await sefaria.get_daily_portions(parasha)
    
    # Generate RSS
    rss_content = rss_gen.generate_daily_feed(daily_portions, location)
    
    # Cache result
    cache.set(cache_key, rss_content)
    
    return Response(content=rss_content, media_type="application/rss+xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)