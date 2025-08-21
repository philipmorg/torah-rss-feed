# Torah RSS Feed App

A self-hosted Torah RSS feed service using Sefaria API for JPS translations.

## Features

- **Weekly Torah Portions**: Complete weekly Torah portions with full JPS English text
- **Daily Torah Portions**: Weekly portions divided into 7 daily readings
- **Multiple Locations**: Support for both Diaspora and Israel schedules
- **RSS Feeds**: Standard RSS 2.0 feeds with full content
- **Caching**: Smart caching to minimize API calls and hosting costs
- **Free Hosting**: Designed to run on free tiers of Railway, Render, or Vercel

## API Endpoints

- `/` - Main page with feed links
- `/feeds/weekly` - Weekly Torah portions (Diaspora schedule)
- `/feeds/weekly/diaspora` - Weekly Torah portions (Diaspora schedule)
- `/feeds/weekly/israel` - Weekly Torah portions (Israel schedule)
- `/feeds/daily` - Daily Torah portions (Diaspora schedule)
- `/feeds/daily/diaspora` - Daily Torah portions (Diaspora schedule)
- `/feeds/daily/israel` - Daily Torah portions (Israel schedule)

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Visit http://localhost:8000

## Deployment

### Railway (Recommended)
1. Push code to GitHub
2. Connect GitHub repo to Railway
3. Railway auto-detects Python and deploys
4. Update `base_url` in `rss_generator.py` with your Railway domain

### Render
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `python app.py`

### Vercel
1. Use the Dockerfile for containerized deployment
2. Set environment variables as needed

## Configuration

Update the `base_url` in `rss_generator.py` with your deployment domain:
```python
self.base_url = "https://your-app-domain.railway.app"
```

## Architecture

- **FastAPI**: Web framework for RSS endpoints
- **Hebcal API**: Hebrew calendar for Torah portion scheduling
- **Sefaria API**: Source for JPS Torah translations
- **File Cache**: Simple caching to minimize API calls
- **RSS 2.0**: Standard RSS feeds with full content support

## Cost Optimization

- Aggressive caching (6+ hours for weekly, 2+ hours for daily)
- Lazy loading (only fetch when cache expires)
- Minimal dependencies
- Designed for free hosting tier limits