class DatabaseError(Exception):
    pass

class BadIndex(DatabaseError):
    pass

class SchemaError(DatabaseError):
    pass
