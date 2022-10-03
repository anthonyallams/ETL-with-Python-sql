DROP TABLE IF EXISTS articles;

CREATE TABLE articles (
  id serial primary key,
  url varchar(500),
  date timestamp default current_timestamp,
  headline text,
  body text,
  source_name varchar(250),
  categories text,
  datepub varchar(250),
  authors varchar(250),
  description text,
  image text
);