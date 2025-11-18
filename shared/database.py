"""
Supabase database client
"""
import os
from supabase import create_client, Client
from typing import List, Dict, Any

class Database:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        # Try to create a Supabase client. If the client initialization fails
        # (for example due to dependency incompatibilities during local dev),
        # fall back to a simple in-memory store so the rest of the app can run.
        if not url or not key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment")

        try:
            self.client: Client = create_client(url, key)
            self._use_supabase = True
        except Exception as e:
            print(f"⚠️  Supabase client init failed, using in-memory fallback: {e}")
            self.client = None
            self._use_supabase = False
            # simple in-memory articles list used as fallback
            self._articles: List[Dict[str, Any]] = []
    
    def insert_article(self, article: Dict[str, Any]) -> bool:
        """
        Insert article into database
        Returns True if inserted, False if duplicate
        """
        # If using Supabase, try to insert there
        if self._use_supabase and self.client is not None:
            try:
                result = self.client.table('articles').insert(article).execute()
                print(f"✅ Inserted: {article['title'][:50]}...")
                return True
            except Exception as e:
                if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                    print(f"⏭️  Already exists: {article['title'][:50]}...")
                    return False
                else:
                    print(f"❌ Error: {e}")
                    raise

        # Fallback: simple duplicate check by URL for in-memory store
        for a in self._articles:
            if a.get('url') == article.get('url'):
                print(f"⏭️  Already exists (in-memory): {article['title'][:50]}...")
                return False

        self._articles.append(article)
        print(f"✅ Inserted (in-memory): {article['title'][:50]}...")
        return True
    
    def get_articles_today(self) -> List[Dict]:
        """Get all articles from today"""
        from datetime import datetime
        today = datetime.now().date().isoformat()
        if self._use_supabase and self.client is not None:
            result = self.client.table('articles')\
                .select('*')\
                .gte('published_date', today)\
                .execute()

            return result.data

        # Fallback: filter in-memory articles
        return [a for a in self._articles if a.get('published_date', '') >= today]
    
    def get_all_articles(self) -> List[Dict]:
        """Get ALL articles from database"""
        if self._use_supabase and self.client is not None:
            result = self.client.table('articles').select('*').execute()
            return result.data
        return self._articles
        
    def count_articles(self) -> int:
        """Count total articles in database"""
        if self._use_supabase and self.client is not None:
            result = self.client.table('articles')\
                .select('id', count='exact')\
                .execute()

            return result.count

        return len(self._articles)