class DatabaseError(Exception):
    pass

class UniqueError(DatabaseError):
    def __init__(self, message, index, record):
        super().__init__(message)
        self.index = index
        self.record = record

class SchemaError(DatabaseError):
    pass
