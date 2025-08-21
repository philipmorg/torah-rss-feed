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
        <li><a href="/feeds/weekly">/feeds/weekly</a> - Upcoming Weekly Torah Portions (next 8 weeks)</li>
        <li><a href="/feeds/daily">/feeds/daily</a> - Upcoming Daily Torah Portions (next 4 weeks, divided by 7)</li>
        <li><a href="/feeds/weekly/diaspora">/feeds/weekly/diaspora</a> - Diaspora schedule</li>
        <li><a href="/feeds/weekly/israel">/feeds/weekly/israel</a> - Israel schedule</li>
    </ul>
    <p>All feeds include full JPS English text from upcoming Torah portions.</p>
    <p><strong>Note:</strong> Feeds are updated every 6 hours (weekly) or 2 hours (daily) and contain future Torah portions relative to when the feed is generated.</p>
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
    
    # Get upcoming Torah portions (next 8 weeks)
    upcoming_parashot = calendar.get_upcoming_parashot(location, count=8)
    
    # Generate RSS with upcoming portions
    rss_content = await rss_gen.generate_upcoming_weekly_feed(upcoming_parashot, location, sefaria)
    
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
    
    # Get upcoming Torah portions for daily division
    upcoming_parashot = calendar.get_upcoming_parashot(location, count=4)  # Next 4 weeks
    
    # Generate RSS with daily portions from upcoming parashot
    rss_content = await rss_gen.generate_upcoming_daily_feed(upcoming_parashot, location, sefaria)
    
    # Cache result
    cache.set(cache_key, rss_content)
    
    return Response(content=rss_content, media_type="application/rss+xml")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)