class Article:
    __table__ = 'articles'
    columns = ['url','date','headline','body','source_name','datepub','authors','description', 'datepub']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise ValueError(f'{key} not in columns: {self.columns}')
        for k, v in kwargs.items():
            setattr(self, k, v)