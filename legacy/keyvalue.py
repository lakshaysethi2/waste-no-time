from peewee import SqliteDatabase, CharField, Model


db = SqliteDatabase('keyval.db')


class KeyValuePair(Model):
    key = CharField()
    value = CharField()

    def __str__(self):
        return self.key + "-" + self.value

    class Meta:
        database = db
