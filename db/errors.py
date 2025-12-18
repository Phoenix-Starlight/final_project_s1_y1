class DatabaseError(Exception):
    pass

class UniqueError(DatabaseError):
    pass

class SchemaError(DatabaseError):
    pass
