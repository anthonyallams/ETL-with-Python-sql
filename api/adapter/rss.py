from api.lib.helper import *
from api.lib.db import conn, cursor
import feedparser
import logging
logging.basicConfig(filename='rss_feed.log',level=logging.DEBUG, format='%(asctime)s:%(process)s:%(levelname)s:%(message)s')

attributes = ['url', 'headline', 'body', 'source_name', 'categories', 'datepub', 'authors', 'description', 'image']

path = 'data/Example RSS Feeds.csv'


def extract_data(url):
    """
    Extraction Layer:Feedparser library is used to fetch the feeds from the urls
    """
    list_of_articles = feedparser.parse(url)
    return list_of_articles


def valid_data(url):
  """
  Validate each feed to ensure it has the right xml format and parameters
  """
  feeds = extract_data(url)
  if not bool(feeds['bozo']) or feeds['bozo'] == 1:
    return

def transform_data(url):
  """
  Transformation layer: Keys and values are extracted from each feed and transformed
                        to the appropriate format for saving into the database and CSV
  """
  feeds = extract_data(url)
  
  entries = feeds['entries']

  selected_entries = []
  for entry in entries:

    attributes = ['url','headline','body','source_name','categories','authors','datepub','description','image']

    selected_entry_values = [get_key(entry, 'link'), get_key(entry,'title'), extract_content_text(get_longkey(entry, 'content', 'value')),get_sourcename(feeds, 'feed', 'title'), concatenate_keys(entry, 'tags','term'), concatenate_keys(entry, 'authors','name'),get_key(entry, 'published'), 
    get_key(entry,'summary'), get_longkey(entry, 'media_thumbnail','url')]

    selected_entry = dict(zip(attributes, selected_entry_values))
    selected_entries.append(selected_entry)
    
  return selected_entries


def load(url):
  """
  Save/Load Layer: Save the feeds to DB and convert each url feed to CSV format
  """
  articles = []
  selected_entries = transform_data(url)

  for selected_entry in selected_entries[:10]:
    try:
        article = save(selected_entry, conn, cursor)
        logging.info(f"{selected_entry['url']}")    
    except:
        logging.exception(f"{selected_entry['url']} Saving to DB Failed failed")
    articles.append(article)
  return articles