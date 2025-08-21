from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

class RSSGenerator:
    def __init__(self):
        self.base_url = "https://torah-rss-feed-production.up.railway.app"
    
    def generate_weekly_feed(self, parasha: Dict[str, Any], torah_text: Dict[str, Any], location: str) -> str:
        """Generate RSS feed for weekly Torah portions"""
        
        rss = ET.Element("rss", version="2.0")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
        
        channel = ET.SubElement(rss, "channel")
        
        # Channel metadata
        ET.SubElement(channel, "title").text = f"Weekly Torah Portions - JPS Translation ({location.title()})"
        ET.SubElement(channel, "description").text = "Complete weekly Torah portions with full JPS English text"
        ET.SubElement(channel, "link").text = f"{self.base_url}/feeds/weekly/{location}"
        ET.SubElement(channel, "language").text = "en-us"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        
        if torah_text:
            # Create item for current Torah portion
            item = ET.SubElement(channel, "item")
            
            title = f"Parashat {parasha['name_english']}"
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = f"{self.base_url}/portion/{parasha['name_english']}"
            ET.SubElement(item, "guid").text = f"{parasha['name_english']}-{parasha['date']}"
            ET.SubElement(item, "pubDate").text = parasha['date'].strftime("%a, %d %b %Y 00:00:00 %z")
            
            # Description with summary
            description = f"Torah Portion: {title}\nReference: {torah_text.get('reference', '')}\n"
            description += f"Translation: {torah_text.get('version', 'JPS')}"
            ET.SubElement(item, "description").text = description
            
            # Full content
            content = self._format_torah_content(torah_text)
            content_elem = ET.SubElement(item, "content:encoded")
            content_elem.text = f"<![CDATA[{content}]]>"
        
        return self._prettify_xml(rss)
    
    def generate_daily_feed(self, daily_portions: List[Dict[str, Any]], location: str) -> str:
        """Generate RSS feed for daily Torah portions"""
        
        rss = ET.Element("rss", version="2.0")
        rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
        
        channel = ET.SubElement(rss, "channel")
        
        # Channel metadata
        ET.SubElement(channel, "title").text = f"Daily Torah Portions - JPS Translation ({location.title()})"
        ET.SubElement(channel, "description").text = "Daily Torah study portions with full JPS English text"
        ET.SubElement(channel, "link").text = f"{self.base_url}/feeds/daily/{location}"
        ET.SubElement(channel, "language").text = "en-us"
        ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        
        # Create items for each day's portion
        for portion in daily_portions[-7:]:  # Last 7 days
            item = ET.SubElement(channel, "item")
            
            title = f"{portion['day_name']} - Parashat {portion['parasha']} (Day {portion['day']})"
            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = f"{self.base_url}/daily/{portion['parasha']}/{portion['day']}"
            ET.SubElement(item, "guid").text = f"{portion['parasha']}-day-{portion['day']}"
            
            # Calculate date for this day (assuming Sunday = start of Torah week)
            base_date = datetime.now().date()
            days_back = base_date.weekday() + 1  # Monday = 0, so Sunday = 6
            sunday = base_date - timedelta(days=days_back)
            portion_date = sunday + timedelta(days=portion['day'] - 1)
            
            ET.SubElement(item, "pubDate").text = portion_date.strftime("%a, %d %b %Y 06:00:00 %z")
            
            # Description
            description = f"Daily Torah study for {portion['day_name']}\n"
            description += f"Parashat {portion['parasha']} - {portion['verse_range']}"
            ET.SubElement(item, "description").text = description
            
            # Full content
            content = self._format_daily_content(portion)
            content_elem = ET.SubElement(item, "content:encoded")
            content_elem.text = f"<![CDATA[{content}]]>"
        
        return self._prettify_xml(rss)
    
    def _format_torah_content(self, torah_text: Dict[str, Any]) -> str:
        """Format Torah text as HTML"""
        html = f"<h2>Parashat {torah_text['parasha']}</h2>\n"
        html += f"<p><strong>Reference:</strong> {torah_text.get('reference', '')}</p>\n"
        html += f"<p><strong>Translation:</strong> {torah_text.get('version', 'JPS')}</p>\n"
        
        if torah_text.get('source'):
            html += f"<p><strong>Source:</strong> <a href=\"{torah_text['source']}\">{torah_text['source']}</a></p>\n"
        
        html += "<div class='torah-text'>\n"
        
        text = torah_text.get('text', [])
        if text and len(text) > 0 and isinstance(text[0], list):
            # Handle nested structure (chapters/verses)
            for chapter_idx, chapter in enumerate(text, 1):
                html += f"<h3>Chapter {chapter_idx}</h3>\n"
                for verse_idx, verse in enumerate(chapter, 1):
                    html += f"<p><sup>{verse_idx}</sup> {verse}</p>\n"
        else:
            # Handle flat verse list
            for verse_idx, verse in enumerate(text, 1):
                html += f"<p><sup>{verse_idx}</sup> {verse}</p>\n"
        
        html += "</div>\n"
        return html
    
    def _format_daily_content(self, portion: Dict[str, Any]) -> str:
        """Format daily portion as HTML"""
        html = f"<h2>{portion['day_name']} Study - Parashat {portion['parasha']}</h2>\n"
        html += f"<p><strong>Day {portion['day']} of 7</strong> | {portion['verse_range']}</p>\n"
        
        html += "<div class='daily-torah-text'>\n"
        for verse_idx, verse in enumerate(portion['text'], 1):
            html += f"<p><sup>{verse_idx}</sup> {verse}</p>\n"
        html += "</div>\n"
        
        return html
    
    def _prettify_xml(self, elem) -> str:
        """Return a pretty-printed XML string"""
        from xml.dom import minidom
        rough_string = ET.tostring(elem, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")