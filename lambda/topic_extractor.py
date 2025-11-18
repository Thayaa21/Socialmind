import spacy
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv('config/.env')

from shared.database import Database

class TopicExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.db = Database()
        
        # Known tech companies and products (helps catch what spaCy misses)
        self.known_entities = {
            'Apple', 'Google', 'Microsoft', 'Amazon', 'Meta', 'Tesla',
            'OpenAI', 'Anthropic', 'NVIDIA', 'AMD', 'Intel', 'Qualcomm',
            'Netflix', 'Spotify', 'Uber', 'Airbnb', 'SpaceX', 'Blue Origin',
            'ChatGPT', 'GPT-5', 'GPT-4', 'Gemini', 'Claude', 'Copilot',
            'iPhone', 'iPad', 'MacBook', 'Galaxy', 'Pixel',
            'TikTok', 'Instagram', 'Facebook', 'Twitter', 'LinkedIn',
            'YouTube', 'WhatsApp', 'Snapchat', 'Reddit', 'Discord',
            'AWS', 'Azure', 'Oracle', 'Salesforce', 'Adobe', 'Cisco',
            'Samsung', 'Sony', 'LG', 'Huawei', 'Xiaomi', 'OnePlus',
            'Ford', 'GM', 'Toyota', 'Volkswagen', 'BMW', 'Mercedes',
            'Stripe', 'PayPal', 'Square', 'Coinbase', 'Robinhood',
            'Zoom', 'Slack', 'Notion', 'Figma', 'Canva', 'Dropbox'
        }
        
        # False positives to exclude
        self.exclude_terms = {
            'AI', 'GPU', 'SEO', 'EV', 'CLI', 'API', 'CEO', 'CTO', 'CFO',
            'IPO', 'VC', 'AR', 'VR', 'IoT', 'SaaS', 'B2B', 'B2C',
            'US', 'EU', 'UK', 'SEC', 'FTC', 'FDA'
        }
    
    def extract_topics_from_article(self, article):
        """
        Extract topics (companies, products) from article
        Uses both spaCy NER and keyword matching
        """
        text = article['title'] + "\n" + article["content"]
        doc = self.nlp(text)
        
        # Get organizations from spaCy
        orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        
        # Add known entities found in text (keyword matching)
        text_lower = text.lower()
        for entity in self.known_entities:
            if entity.lower() in text_lower:
                orgs.append(entity)
        
        # Clean up results
        orgs = list(set(orgs))  # Remove duplicates
        orgs = [org for org in orgs if org not in self.exclude_terms]  # Remove false positives
        orgs = [org.strip() for org in orgs if len(org.strip()) > 1]  # Remove empty/single char
        
        return sorted(orgs)  # Sort for consistency
    
    def process_all_articles(self):
        """Get articles from DB and extract topics"""
        articles = self.db.get_all_articles()
        
        print("="*60)
        print(f"Processing {len(articles)} articles...")
        print("="*60)
        
        updated_count = 0
        
        for article in articles:
            topics = self.extract_topics_from_article(article)
            
            # Print what we found
            print(f"\n{article['source']}: {article['title'][:60]}")
            print(f"  Topics: {topics}")
            
            if topics:  # Only update if we found topics
                self.update_article_topics(article['id'], topics)
                updated_count += 1
        
        print("\n" + "="*60)
        print(f"✅ Updated {updated_count}/{len(articles)} articles with topics")
        print("="*60)

    def update_article_topics(self, article_id, topics):
        """Update article in database with extracted topics"""
        if self.db._use_supabase and self.db.client is not None:
            try:
                result = self.db.client.table('articles')\
                    .update({'topics_extracted': topics})\
                    .eq('id', article_id)\
                    .execute()
                print(f"  ✅ Updated article ID {article_id}")
            except Exception as e:
                print(f"  ❌ Error updating article ID {article_id}: {e}")


if __name__ == "__main__":
    extractor = TopicExtractor()
    extractor.process_all_articles()