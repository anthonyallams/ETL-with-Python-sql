from api.lib.helper import extract_url_from_csv, convert_to_csv, find_uploaded
from api.adapter.rss import load,valid_data
from api import create_app

if __name__ == '__main__':
    path = extract_url_from_csv('data/Example RSS Feeds.csv')
    feed_urls = []
    for file_name, url in path:
        if not valid_data(url):
            articles = load(url)
            feed_urls.append([item[0] for item in articles])
            convert_to_csv(articles, file_name)
    app = create_app()

    app.run(debug = True, port=5001)