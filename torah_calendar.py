from datetime import datetime, timedelta
import requests
from typing import Dict, Any

class TorahCalendar:
    def __init__(self):
        self.hebcal_base = "https://www.hebcal.com/hebcal"
    
    def get_current_parasha(self, location: str = "diaspora") -> Dict[str, Any]:
        """Get current Torah portion from Hebcal API"""
        params = {
            'v': 1,
            'cfg': 'json',
            'maj': 'on',  # Major holidays
            'min': 'on',  # Minor holidays  
            'mod': 'on',  # Modern holidays
            'nx': 'on',   # Rosh Chodesh
            'year': datetime.now().year,
            'month': datetime.now().month,
            'ss': 'on',   # Shabbat times
            'mf': 'on',   # Minor fasts
            'c': 'on',    # Candle lighting
            'geo': 'geoname' if location == "israel" else 'none',
            'geonameid': '281184' if location == "israel" else None,  # Jerusalem
            'i': 'off' if location == "diaspora" else 'on'  # Israel vs Diaspora
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = requests.get(self.hebcal_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find current/next Torah reading
            today = datetime.now().date()
            for item in data.get('items', []):
                if item.get('category') == 'parashat':
                    item_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
                    if item_date >= today:
                        return {
                            'name': item['hebrew'],
                            'name_english': item['title'].replace('Parashat ', ''),
                            'date': item_date,
                            'torah_reading': item.get('leyning', {}),
                            'url': item.get('url', '')
                        }
            
            return None
        except Exception as e:
            print(f"Error fetching parasha: {e}")
            return None