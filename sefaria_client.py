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
            parasha_name = parasha['name_english']
            
            # Map Torah portions to their Torah book references
            # This is a simplified mapping - in a real app you'd want a complete mapping
            torah_portion_map = {
                "Bereishit": "Genesis.1.1-6.8",
                "Noach": "Genesis.6.9-11.32", 
                "Lech-Lecha": "Genesis.12.1-17.27",
                "Vayera": "Genesis.18.1-22.24",
                "Chayei Sara": "Genesis.23.1-25.18",
                "Toldot": "Genesis.25.19-28.9",
                "Vayetzei": "Genesis.28.10-32.3",
                "Vayishlach": "Genesis.32.4-36.43",
                "Vayeshev": "Genesis.37.1-40.23",
                "Miketz": "Genesis.41.1-44.17",
                "Vayigash": "Genesis.44.18-47.27",
                "Vayechi": "Genesis.47.28-50.26",
                "Shemot": "Exodus.1.1-6.1",
                "Vaera": "Exodus.6.2-9.35",
                "Bo": "Exodus.10.1-13.16",
                "Beshalach": "Exodus.13.17-17.16",
                "Yitro": "Exodus.18.1-20.23",
                "Mishpatim": "Exodus.21.1-24.18",
                "Terumah": "Exodus.25.1-27.19",
                "Tetzaveh": "Exodus.27.20-30.10",
                "Ki Tisa": "Exodus.30.11-34.35",
                "Vayakhel": "Exodus.35.1-38.20",
                "Pekudei": "Exodus.38.21-40.38",
                "Vayikra": "Leviticus.1.1-5.26",
                "Tzav": "Leviticus.6.1-8.36",
                "Shmini": "Leviticus.9.1-11.47",
                "Tazria": "Leviticus.12.1-13.59",
                "Metzora": "Leviticus.14.1-15.33",
                "Achrei Mot": "Leviticus.16.1-18.30",
                "Kedoshim": "Leviticus.19.1-20.27",
                "Emor": "Leviticus.21.1-24.23",
                "Behar": "Leviticus.25.1-26.2",
                "Bechukotai": "Leviticus.26.3-27.34",
                "Bamidbar": "Numbers.1.1-4.20",
                "Nasso": "Numbers.4.21-7.89",
                "Beha'alotcha": "Numbers.8.1-12.16",
                "Sh'lach": "Numbers.13.1-15.41",
                "Korach": "Numbers.16.1-18.32",
                "Chukat": "Numbers.19.1-22.1",
                "Balak": "Numbers.22.2-25.9",
                "Pinchas": "Numbers.25.10-30.1",
                "Matot": "Numbers.30.2-32.42",
                "Masei": "Numbers.33.1-36.13",
                "Devarim": "Deuteronomy.1.1-3.22",
                "Vaetchanan": "Deuteronomy.3.23-7.11",
                "Eikev": "Deuteronomy.7.12-11.25",
                "Re'eh": "Deuteronomy.11.26-16.17",
                "Shoftim": "Deuteronomy.16.18-21.9",
                "Ki Teitzei": "Deuteronomy.21.10-25.19",
                "Ki Tavo": "Deuteronomy.26.1-29.8",
                "Nitzavim": "Deuteronomy.29.9-30.20",
                "Vayeilech": "Deuteronomy.31.1-31.30",
                "Ha'Azinu": "Deuteronomy.32.1-32.52",
                "V'Zot HaBerachah": "Deuteronomy.33.1-34.12"
            }
            
            # Try to find the Torah reference
            ref = torah_portion_map.get(parasha_name)
            
            if not ref:
                # If not in our map, try alternative names or just return a sample
                print(f"Torah portion {parasha_name} not found in mapping, using sample text")
                ref = "Genesis.1.1-1.31"  # Default to Genesis 1 as sample
            
            # Fetch from Sefaria
            url = f"{self.base_url}/texts/{ref}"
            params = {
                'lang': 'en',
                'version': 'The Contemporary Torah, Jewish Publication Society, 2006'
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    text = data.get('text', [])
                    
                    # Extract the correct verse range from the response
                    filtered_text = self._extract_verse_range(text, ref)
                    
                    return {
                        'parasha': parasha_name,
                        'reference': ref.replace('.', ' ').replace('-', '-'),
                        'text': filtered_text,
                        'hebrew': data.get('he', []),
                        'version': data.get('versionTitle', 'JPS Contemporary Torah 2006'),
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
    
    def _extract_verse_range(self, text, ref):
        """Extract the correct verse range from Sefaria response based on reference"""
        try:
            # Parse reference like "Deuteronomy.11.26-16.17"
            # Split on the book name and range
            parts = ref.split('.')
            if len(parts) < 3:
                return text  # If parsing fails, return full text
            
            # Extract start and end references
            range_part = '.'.join(parts[1:])  # "11.26-16.17"
            start_ref, end_ref = range_part.split('-')
            
            start_chapter, start_verse = map(int, start_ref.split('.'))
            end_chapter, end_verse = map(int, end_ref.split('.'))
            
            if not text or not isinstance(text[0], list):
                return text  # If not chapter/verse structure, return as is
            
            filtered_chapters = []
            
            # Process each chapter in the range
            for chapter_num in range(start_chapter, end_chapter + 1):
                chapter_index = chapter_num - start_chapter
                
                if chapter_index >= len(text):
                    break  # No more chapters available
                    
                chapter_verses = text[chapter_index]
                
                if chapter_num == start_chapter and chapter_num == end_chapter:
                    # Same chapter - extract verse range within chapter
                    filtered_verses = chapter_verses[start_verse-1:end_verse]
                elif chapter_num == start_chapter:
                    # First chapter - start from start_verse to end
                    filtered_verses = chapter_verses[start_verse-1:]
                elif chapter_num == end_chapter:
                    # Last chapter - from beginning to end_verse
                    filtered_verses = chapter_verses[:end_verse]
                else:
                    # Middle chapters - take all verses
                    filtered_verses = chapter_verses
                
                if filtered_verses:
                    filtered_chapters.append(filtered_verses)
            
            return filtered_chapters if filtered_chapters else text
            
        except Exception as e:
            print(f"Error extracting verse range from {ref}: {e}")
            return text  # Return original text if parsing fails

    async def close(self):
        if self.session:
            await self.session.close()