import feedparser
import time
from datetime import datetime, timedelta

# 1. Define our RSS feeds
FEED_URLS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "Wired": "https://www.wired.com/feed/rss"
}

# 2. Set our time limit (7 days ago)
# We get the current time, then subtract 7 days
one_week_ago = datetime.now() - timedelta(days=7)

# 3. This list will hold all our filtered articles
all_articles = []

# --- Main Fetching Loop ---
for site_name, url in FEED_URLS.items():
    
    print(f"\n--- 📰 Fetching articles from: {site_name} ---")
    feed = feedparser.parse(url)

    if feed.bozo:
        print(f"Error parsing feed from {site_name}: {feed.bozo_exception}\n")
        continue # Skip to the next site

    print(f"Found {len(feed.entries)} total entries. Filtering for last 7 days...")
    
    # 4. Loop through ALL entries (not just 5)
    for entry in feed.entries:
        
        # 5. Get the published date
        # We use .get() to avoid errors if the 'published_parsed' field is missing
        published_struct = entry.get('published_parsed')
        if not published_struct:
            continue # Skip this article if it has no date

        # 6. Convert the feed's time data into a standard Python 'datetime' object
        # time.mktime() converts the 9-part time struct into a timestamp
        # datetime.fromtimestamp() converts that timestamp into a 'datetime' object
        published_date = datetime.fromtimestamp(time.mktime(published_struct))

        # 7. The main filter!
        # If the article's date is *before* our 'one_week_ago' cutoff, skip it
        if published_date < one_week_ago:
            continue # This article is too old, move to the next one

        # 8. If the article is new enough, store it in our list!
        article_data = {
            "source": site_name,
            "title": entry.title,
            "link": entry.link,
            "published": published_date,
            "summary": entry.get('summary', '') # Get summary if it exists
        }
        all_articles.append(article_data)

# --- End of Loop ---

print("\n" + "="*50)
print(f"✅ Total articles fetched from the last week: {len(all_articles)}")
print("="*50)

# To check our work, let's print the 5 newest articles from our *combined* list
# We sort the list by the 'published' date, from newest to oldest
all_articles.sort(key=lambda x: x['published'], reverse=True)

print("\nTop 5 newest articles from all sources combined:\n")
for article in all_articles[:20]:
    print(f"Title: {article['title']}")
    print(f"Source: {article['source']}")
    print(f"Date: {article['published']}")
    print("-" * 30)