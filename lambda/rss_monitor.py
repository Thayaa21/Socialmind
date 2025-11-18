"""
RSS Monitor - Scrapes tech news feeds
"""
import os
import feedparser
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add parent directory to path so we can import shared modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import Database

class RSSMonitor:
    def __init__(self):
        # Load environment variables
        load_dotenv('config/.env')
        
        self.db = Database()
        
        # RSS feed sources
        self.feeds = [
            {
                'name': 'TechCrunch',
                'url': os.getenv('TECHCRUNCH_FEED')
            },
            {
                'name': 'The Verge', 
                'url': os.getenv('VERGE_FEED')
            },
            {
                'name': 'Ars Technica',
                'url': os.getenv('ARSTECHNICA_FEED')
            },
            {
                'name': 'Hacker News',
                'url': os.getenv('HACKERNEWS_FEED')
            }
        ]
    
    def scrape_all(self):
        """Scrape all RSS feeds"""
        print("\n" + "="*60)
        print("🚀 Starting RSS scraping...")
        print("="*60 + "\n")
        
        total_new = 0
        total_duplicate = 0
        
        for feed in self.feeds:
            new, duplicate = self.scrape_feed(feed)
            total_new += new
            total_duplicate += duplicate
        
        print("\n" + "="*60)
        print(f"✅ Scraping complete!")
        print(f"   New articles: {total_new}")
        print(f"   Duplicates skipped: {total_duplicate}")
        print("="*60 + "\n")
    
    def scrape_feed(self, feed_config):
        """Scrape a single RSS feed"""
        name = feed_config['name']
        url = feed_config['url']
        
        print(f"\n📡 Scraping {name}...")
        print(f"   URL: {url}")
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(url)
            
            if feed.bozo:
                print(f"⚠️  Warning: Feed has errors")
            
            new_count = 0
            duplicate_count = 0
            
            # Process each entry
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                article = self.parse_entry(entry, name)
                
                if article:
                    inserted = self.db.insert_article(article)
                    if inserted:
                        new_count += 1
                    else:
                        duplicate_count += 1
            
            print(f"✅ {name}: {new_count} new, {duplicate_count} duplicates")
            return new_count, duplicate_count
            
        except Exception as e:
            print(f"❌ Error scraping {name}: {e}")
            return 0, 0
    
    def parse_entry(self, entry, source):
        """Parse RSS entry into article dict"""
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                return None
            
            # Extract URL
            url = entry.get('link', '')
            if not url:
                return None
            
            # Extract content (summary or description)
            content = entry.get('summary', entry.get('description', '')).strip()
            
            # Parse published date
            published = self.parse_date(entry)
            
            article = {
                'source': source,
                'title': title,
                'url': url,
                'content': content,
                'published_date': published,
                'topics_extracted': []  # Will extract topics later
            }
            
            return article
            
        except Exception as e:
            print(f"⚠️  Failed to parse entry: {e}")
            return None
    
    def parse_date(self, entry):
        """Parse published date from entry"""
        # Try different date fields
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            time_tuple = entry.published_parsed
            return datetime(*time_tuple[:6]).isoformat()
        
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            time_tuple = entry.updated_parsed
            return datetime(*time_tuple[:6]).isoformat()
        
        # Fallback to now
        return datetime.now().isoformat()


# For local testing
if __name__ == "__main__":
    monitor = RSSMonitor()
    monitor.scrape_all()
    
    # Show stats
    print("\n📊 Database Stats:")
    print(f"   Total articles: {monitor.db.count_articles()}")