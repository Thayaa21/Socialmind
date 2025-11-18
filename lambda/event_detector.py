import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

from shared.database import Database

class EventDetector:
    def __init__(self):
        self.db = Database()
        
        # Define event patterns
        self.event_patterns = {
            'launch': ['announces', 'launches', 'releases', 'unveils', 'introduces', 'debuts'],
            'acquisition': ['acquires', 'buys', 'acquisition', 'purchased', 'acquiring'],
            'controversy': ['lawsuit', 'scandal', 'investigation', 'accused', 'controversy'],
            'milestone': ['reaches', 'surpasses', 'hits', 'crosses', 'milestone', 'achievement']
        }
    
    def detect_event(self, article):
        """
        Detect if article describes an event
        
        YOUR TASK:
        1. Get article title (lowercase)
        2. Loop through event_patterns
        3. For each event type, check if ANY keyword appears in title
        4. Return event type if found, None if no event
        """
        text = article['title'].lower()
        for event_type, keywords in self.event_patterns.items():
            if any(keyword in text for keyword in keywords):
                return event_type
        return None
    
    def process_articles(self):
        articles = self.db.get_all_articles()
        
        for article in articles:
            event_type = self.detect_event(article)
            
            if event_type:
                print(f"\n🔥 {event_type.upper()}: {article['title']}")
                print(f"   Source: {article['source']}")
                print(f"   Topics: {article.get('topics_extracted', [])}")


if __name__ == "__main__":
    detector = EventDetector()
    detector.process_articles()