from api.lib.settings import SINGLE_URL, BATCH_URL
import pandas as pd
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import requests


TABLE = 'articles'
ATTRIBUTES = ['url','headline','body','source_name','categories','authors','datepub','description','image']


def values(dict)->list[str]:
    """
    Get values from the feed dictionary
    """   
    return [value for key,value in dict.items() if key in ATTRIBUTES]


def keys(dict)->str:
    """
    Get keys from the feed dictionary
    """   
    selected = [key for key in dict.keys() if key in ATTRIBUTES]
    return ', '.join(selected)


def find_all(conn)->list[tuple]:
    """
    Get all records from DB
    """   
    cursor = conn.cursor()
    sql_str = f"SELECT * FROM {TABLE}"
    cursor.execute(sql_str)
    records = cursor.fetchall()
    return records


def find_uploaded(list, conn)->list[tuple]:
    """
    Get all uploaded feeds based on URL
    """   
    urls = list[0]
    cursor = conn.cursor()
    sql_str = f"SELECT * FROM {TABLE} WHERE url IN %s"
    cursor.execute(sql_str, (urls))
    records = cursor.fetchall()
    return records


def find(id, conn)->tuple:
    """
    Find individual records from DB
    """   
    cursor = conn.cursor()
    
    sql_str = f"SELECT * FROM {TABLE} WHERE id = %s"
    
    cursor.execute(sql_str, (id,))
    record = cursor.fetchone()

    return record


def url_exists(dict, conn)->tuple:
    """
    Check if url is unique before inserting into DB
    """   
    cursor = conn.cursor()
    url = dict.get('url', None)
    sql_str = f"SELECT url FROM {TABLE} WHERE url = %s"
    
    cursor.execute(sql_str, (url,))
    url_record = cursor.fetchone()

    return url_record


def save(dict, conn, cursor)->list[dict]:
    """
    Function to insert feed records into DB
    """   
    if not url_exists(dict,conn):
        insert_values = ', '.join(len(values(dict)) * ['%s'])
        insert_query = f"""INSERT INTO {TABLE} ({keys(dict)})  VALUES ({insert_values});"""
        cursor.execute(insert_query, list(values(dict)))
        conn.commit()

    return list(values(dict))


def build_from_record(Class, record)->dict:
    """
    Display a single record based on class attributes
    """
    if not record: return None
    attr = dict(zip(Class.columns, record))
    obj = Class()
    obj.__dict__ = attr
    return obj


def build_from_records(Class, records)->list[dict]:
    """
    Display database records based on class attributes
    """
    return [build_from_record(Class, record) for record in records]


def drop_records(cursor, conn):
    """
    drop DB Table records Statement
    """   
    cursor.execute(f"DELETE FROM {TABLE};")
    conn.commit()


def drop_tables(table_names, cursor, conn):
    """
    Function to drop records from table
    """
    for table_name in table_names:
        drop_records(cursor, conn, table_name)


def drop_all_tables(conn, cursor):
    """
    Function to drop all table records specified in the table_names list below
    """
    table_names = ['articles']
    drop_tables(table_names, cursor, conn)


def extract_content_text(data)->str:
    """
    Function to parse html tags and extract text from p tags in the article body
    """   
    soup = BeautifulSoup(data, "html.parser")
    list_p_tags = soup.find_all('p')

    p_tag_text = []
    for p_tag in list_p_tags:
        p_text = p_tag.get_text(strip=True)
        text_encode = p_text.encode(encoding="UTF-8", errors="ignore")
        p_tag_text.append(text_encode.decode())

    return "\n".join([x for x in p_tag_text])


def extract_url_from_csv(path)->list:
    """
    Function to get the feed url names from source CSV
    """   
    with open(path, 'r') as file:
      contents = file.read().splitlines()
      file_title = [content.split(',')[0] for content in contents]
      url = [content.split(',')[1] for content in contents]
    return list(zip(file_title, url))


def convert_to_csv(entry, file_name)->str:
    """
    Function to convert individual feeds to CSV format
    """   
    data_folder = Path('csv_files')
    csv_filename = f'{file_name}_{datetime.now()}.csv'

    df = pd.DataFrame(data=entry, columns=ATTRIBUTES)
    df = df.to_csv(f'{data_folder}/{csv_filename}', index=False)
    return f'{file_name}.csv'


def get_key(dict, key)->str:
  """
  Get the values for keys with one parameters
  """   
  result = dict.get(key, None)
  if not result:
    return None

  return result


def get_longkey(dict, root,key)->str:
    """
    Get the values for keys with long parameters
    """   
    if dict.get(root):
        result = dict[root][0][key]
    else:
        result = None

    return result


def concatenate_keys(dict, root, key)->str:
    """
    Concatenate feed/dictionary keys that have more than one value
    """
    return ', '.join([value[key].capitalize() for value in dict[root]])


def get_sourcename(dict, root, key)->str:
    """
    Get the source name for the article
    """
    return dict[root][key]


def parse_date(date_str)->datetime:
    """
    Convert the datetime from API into the right format before loading to Database/data warehouse
    """
    if date_str:
        date_obj = datetime.strptime(date_str,"%a, %d %b %Y %H:%M:%S %Z")
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date


def single_article(key, text)->dict:
    """
    Generate the score and confidence for single article
    """
    params = {'key':key, 'body':text}
    response = requests.post(SINGLE_URL, params=params)

    return response.json()


def single_url(key, url)->dict:
    """
    Generate the score and confidence for single url
    """
    params = {'key':key, 'url':url}
    response = requests.post(SINGLE_URL, params=params)

    return response.json()


def generate_batch_data(key, url=None, bodies=None)->dict:
    """
    Generate the json data parameters for batch API model scoring
    """
    if url and bodies:
        return {"key":key, "url": url, "bodies": bodies}
    elif bodies:
        return {"key":key, "bodies": bodies}
    else:
        return {"key":key, "url": url}


def batch_article(key, urls, texts)->dict:
    """
    Generate the score, confidence, item_id and session_id for a batch of articles
    """
    headers = {'content-type':'application/json', 'charset':'utf-8'}
    json_data = generate_batch_data(key, urls=urls, texts=texts)
    response = requests.post(BATCH_URL, json=json_data, headers=headers)

    return response.json()