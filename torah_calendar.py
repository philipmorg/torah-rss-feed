from datetime import datetime, timedelta
import requests
from typing import Dict, Any, List

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
    
    def get_upcoming_parashot(self, location: str = "diaspora", count: int = 10) -> List[Dict[str, Any]]:
        """Get multiple upcoming Torah portions using Torah cycle logic"""
        try:
            # Standard Torah cycle (54 portions in a regular year)
            torah_cycle = [
                "Bereishit", "Noach", "Lech-Lecha", "Vayera", "Chayei Sara", "Toldot",
                "Vayetzei", "Vayishlach", "Vayeshev", "Miketz", "Vayigash", "Vayechi",
                "Shemot", "Vaera", "Bo", "Beshalach", "Yitro", "Mishpatim", "Terumah",
                "Tetzaveh", "Ki Tisa", "Vayakhel", "Pekudei", "Vayikra", "Tzav", "Shmini",
                "Tazria", "Metzora", "Achrei Mot", "Kedoshim", "Emor", "Behar", "Bechukotai",
                "Bamidbar", "Nasso", "Beha'alotcha", "Sh'lach", "Korach", "Chukat", "Balak",
                "Pinchas", "Matot", "Masei", "Devarim", "Vaetchanan", "Eikev", "Re'eh",
                "Shoftim", "Ki Teitzei", "Ki Tavo", "Nitzavim", "Vayeilech", "Ha'Azinu",
                "V'Zot HaBerachah"
            ]
            
            # Get current parasha to find our position in the cycle
            current_parasha = self.get_current_parasha(location)
            today = datetime.now().date()
            
            if not current_parasha:
                print("Could not get current parasha, using Re'eh as current (August 2025)")
                current_index = torah_cycle.index("Re'eh")  # Hard-code for now since we know it's Re'eh
            else:
                current_name = current_parasha['name_english']
                # Normalize apostrophes to handle Unicode differences
                current_name_normalized = current_name.replace(''', "'").replace(''', "'")
                try:
                    current_index = torah_cycle.index(current_name_normalized)
                except ValueError:
                    print(f"Current parasha '{current_name}' not found in cycle, using Re'eh as fallback")
                    current_index = torah_cycle.index("Re'eh")  # Use Re'eh as fallback for August 2025
            
            # Calculate the next Saturday (start of upcoming Torah portions)
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0:
                # Today is Saturday - start with current parasha
                next_saturday = today
                start_offset = 0  # Start with current parasha
            else:
                # Check if we should include this week's Saturday or next week's
                this_saturday = today + timedelta(days=days_until_saturday)
                # If this Saturday hasn't passed yet, include it
                next_saturday = this_saturday
                start_offset = 0  # Start with current parasha (this week's)
            
            parashot = []
            
            # Generate upcoming parashot starting from this or next Saturday
            for i in range(count):
                # Calculate parasha index (wrap around for next year)
                parasha_index = (current_index + i + start_offset) % len(torah_cycle)
                parasha_name = torah_cycle[parasha_index]
                
                # Calculate the date (each parasha is one week apart from next Saturday)
                parasha_date = next_saturday + timedelta(weeks=i)
                
                parasha_data = {
                    'name': parasha_name,
                    'name_english': parasha_name,
                    'date': parasha_date,
                    'torah_reading': {'torah': parasha_name},
                    'url': f"https://www.hebcal.com/sedrot/{parasha_name.lower()}"
                }
                parashot.append(parasha_data)
            
            return parashot
            
        except Exception as e:
            print(f"Error generating upcoming parashot: {e}")
            return []