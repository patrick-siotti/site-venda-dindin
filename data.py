from peewee import * # type: ignore

db = SqliteDatabase('database.db')

class Dindin(Model):
  nome = TextField(unique=True)
  info = TextField(default=None)
  ingredientes = TextField(default=None)
  estoque = IntegerField()
  valor = FloatField()

  class Meta:
    database = db

db.connect()
db.create_tables([Dindin])
db.close()
