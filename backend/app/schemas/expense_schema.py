# Este esquema permite transformar el objeto de base de datos (modelo)
# a un formato JSON que el frontend (tu app) puede entender fácilmente.
from marshmallow import Schema, fields

class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    amount = fields.Float(required=True)
    date = fields.Date(required=True)
    category = fields.Str()
    user_id = fields.Int()

# Instancia única para usar en los controladores
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)