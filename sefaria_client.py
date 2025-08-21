import aiohttp
import asyncio
from typing import Dict, List, Any
import re

class SefariaClient:
    def __init__(self):
        self.base_url = "https://www.sefaria.org/api"
        self.session = None
    
    async def _get_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_torah_portion(self, parasha: Dict[str, Any]) -> Dict[str, Any]:
        """Get full Torah portion text from Sefaria"""
        if not parasha:
            return None
            
        session = await self._get_session()
        
        try:
            # Extract Torah reading references
            torah_reading = parasha.get('torah_reading', {})
            if not torah_reading:
                return None
            
            # Get the main Torah reading (usually the first one)
            main_reading = None
            for reading in torah_reading.values():
                if isinstance(reading, str) and 'Torah' not in reading:
                    main_reading = reading
                    break
            
            if not main_reading:
                return None
            
            # Clean the reference (e.g., "Genesis 1:1-6:8" -> "Genesis.1.1-6.8")
            ref = self._clean_reference(main_reading)
            
            # Fetch from Sefaria
            url = f"{self.base_url}/texts/{ref}"
            params = {
                'lang': 'en',
                'version': 'The Contemporary Torah, Jewish Publication Society, 2006'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'parasha': parasha['name_english'],
                        'reference': main_reading,
                        'text': data.get('text', []),
                        'hebrew': data.get('he', []),
                        'version': data.get('versionTitle', ''),
                        'source': data.get('versionSource', '')
                    }
                else:
                    print(f"Sefaria API error: {response.status}")
                    return None
                    
        except Exception as e:
            print(f"Error fetching Torah text: {e}")
            return None
    
    async def get_daily_portions(self, parasha: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Divide weekly Torah portion into daily readings"""
        torah_text = await self.get_torah_portion(parasha)
        if not torah_text or not torah_text.get('text'):
            return []
        
        # Simple division: split text into 7 parts
        full_text = torah_text['text']
        if isinstance(full_text[0], list):
            # Flatten nested arrays (chapters/verses)
            flattened = []
            for chapter in full_text:
                flattened.extend(chapter)
            full_text = flattened
        
        total_verses = len(full_text)
        verses_per_day = max(1, total_verses // 7)
        
        daily_portions = []
        for day in range(7):
            start_idx = day * verses_per_day
            end_idx = start_idx + verses_per_day if day < 6 else total_verses
            
            daily_text = full_text[start_idx:end_idx]
            
            daily_portions.append({
                'day': day + 1,
                'day_name': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][day],
                'parasha': parasha['name_english'],
                'text': daily_text,
                'verse_range': f"Verses {start_idx + 1}-{end_idx}"
            })
        
        return daily_portions
    
    def _clean_reference(self, ref: str) -> str:
        """Convert human-readable reference to Sefaria API format"""
        # Replace spaces with dots, handle ranges
        ref = re.sub(r'(\d+):(\d+)', r'\1.\2', ref)  # "1:1" -> "1.1"
        ref = ref.replace(' ', '.')
        return ref
    
    async def close(self):
        if self.session:
            await self.session.close()