from datetime import datetime, timedelta
import requests
from typing import Dict, Any

class TorahCalendar:
    def __init__(self):
        self.hebcal_base = "https://www.hebcal.com/hebcal"
    
    def get_current_parasha(self, location: str = "diaspora") -> Dict[str, Any]:
        """Get current Torah portion from Hebcal API"""
        try:
            # Use the converter API to get today's Hebrew date and events
            today = datetime.now()
            converter_url = "https://www.hebcal.com/converter/"
            params = {
                'cfg': 'json',
                'gy': today.year,
                'gm': today.month,
                'gd': today.day,
                'g2h': 1
            }
            
            response = requests.get(converter_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Look for Torah portion in events
            events = data.get('events', [])
            for event in events:
                if event.startswith('Parashat '):
                    parasha_name = event.replace('Parashat ', '')
                    
                    # Get more detailed reading info from sedrot API
                    sedrot_url = f"https://www.hebcal.com/sedrot/{parasha_name.lower()}"
                    
                    return {
                        'name': parasha_name,  # Hebrew name same as English for now
                        'name_english': parasha_name,
                        'date': today.date(),
                        'torah_reading': {'torah': f'{parasha_name}'},  # Simplified
                        'url': sedrot_url
                    }
            
            # If no Torah portion found today, try to get weekly reading schedule
            # Get broader range to find next/current Shabbat
            params_weekly = {
                'v': 1,
                'cfg': 'json',
                'year': today.year,
                'month': today.month,
                'ss': 'on',
                'sed': 'on',  # Torah readings
                'i': 'off' if location == "diaspora" else 'on'
            }
            
            response = requests.get(self.hebcal_base, params=params_weekly, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find current/next Torah reading
            today_date = today.date()
            for item in data.get('items', []):
                if 'Parashat' in item.get('title', ''):
                    item_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
                    # Get current week's Torah portion (within 7 days)
                    if abs((item_date - today_date).days) <= 7:
                        parasha_name = item['title'].replace('Parashat ', '')
                        return {
                            'name': item.get('hebrew', parasha_name),
                            'name_english': parasha_name,
                            'date': item_date,
                            'torah_reading': item.get('leyning', {'torah': parasha_name}),
                            'url': item.get('url', '')
                        }
            
            return None
        except Exception as e:
            print(f"Error fetching parasha: {e}")
            return None