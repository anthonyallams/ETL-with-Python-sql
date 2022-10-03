import pandas as pd
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime


TABLE = 'articles'
ATTRIBUTES = ['url','headline','body','source_name','categories','authors','datepub','description','image']

def values(dict):
    """
    Get values from the feed dictionary
    """   
    return [value for key,value in dict.items() if key in ATTRIBUTES]


def keys(dict):
    """
    Get keys from the feed dictionary
    """   
    selected = [key for key in dict.keys() if key in ATTRIBUTES]
    return ', '.join(selected)


def find_all(conn):
    """
    Get all records from DB
    """   
    cursor = conn.cursor()
    sql_str = f"SELECT * FROM {TABLE}"
    cursor.execute(sql_str)
    records = cursor.fetchall()
    return records


def find_uploaded(list, conn):
    """
    Get all uploaded feeds based on URL
    """   
    urls = list[0]
    cursor = conn.cursor()
    sql_str = f"SELECT * FROM {TABLE} WHERE url IN %s"
    cursor.execute(sql_str, (urls))
    records = cursor.fetchall()
    return records


def find(id, conn):
    """
    Find individual records from DB
    """   
    cursor = conn.cursor()
    
    sql_str = f"SELECT * FROM {TABLE} WHERE id = %s"
    
    cursor.execute(sql_str, (id,))
    record = cursor.fetchone()
    return record

def url_exists(dict, conn):
    """
    Check if url is unique before inserting into DB
    """   
    cursor = conn.cursor()
    url = dict.get('url', None)
    sql_str = f"SELECT * FROM {TABLE} WHERE url = %s"
    
    cursor.execute(sql_str, (url,))
    url_record = cursor.fetchone()
    return url_record


def save(dict, conn, cursor):
    """
    Function to insert feed records into DB
    """   
    if not url_exists(dict,conn):
        insert_values = ', '.join(len(values(dict)) * ['%s'])
        insert_query = f"""INSERT INTO {TABLE} ({keys(dict)})  VALUES ({insert_values});"""
        cursor.execute(insert_query, list(values(dict)))
        conn.commit()
    return list(values(dict))


def drop_records(cursor, conn):
    """
    Function to drop DB records
    """   
    cursor.execute(f"DELETE FROM {TABLE};")
    conn.commit()


def extract_content_text(data):
    """
    Function to parse html tags in the body of the feed
    """   
    soup = BeautifulSoup(data, "html.parser")
    list_p_tags = soup.find_all('p')

    p_tag_text = []
    for p_tag in list_p_tags:
        p_tag_text.append(p_tag.get_text())

    return "\n".join([x for x in p_tag_text])


def extract_url_from_csv(path):
    """
    Function to get the feed url names from source CSV
    """   
    with open(path, 'r') as file:
      contents = file.read().splitlines()
      file_title = [content.split(',')[0] for content in contents]
      url = [content.split(',')[1] for content in contents]
    return list(zip(file_title, url))


def convert_to_csv(entry, file_name):
    """
    Function to convert individual feeds to CSV format
    """   
    data_folder = Path('csv_files')
    csv_filename = f'{file_name}_{datetime.now()}.csv'

    df = pd.DataFrame(data=entry, columns=ATTRIBUTES)
    df = df.to_csv(f'{data_folder}/{csv_filename}', index=False)
    return f'{file_name}.csv'


def get_key(dict, key):
  """
  Get the values for keys with one parameters
  """   
  result = dict.get(key, None)
  if not result:
    return None
  return result


def get_longkey(dict, root,key):
    """
    Get the values for keys with long parameters
    """   
    if dict.get(root):
        result = dict[root][0][key]
    else:
        result = None
    return result


def concatenate_keys(dict, root, key):
    """
    Concatenate feed/dictionary keys that have more than one value
    """
    return ', '.join([value[key].capitalize() for value in dict[root]])


def get_sourcename(dict, root, key):
    """
    Get the source name for the article
    """
    return dict[root][key]


def parse_date(date_str):
    if date_str:
        date_obj = datetime.strptime(date_str,"%a, %d %b %Y %H:%M:%S %Z")
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date