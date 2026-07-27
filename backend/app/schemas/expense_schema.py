from marshmallow import Schema, fields

class ExpenseSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    amount = fields.Float(required=True)
    expense_date = fields.Date(required=True)  # ¡Corregido! Antes decía 'date'
    category = fields.Str()
    workspace_id = fields.Int()  # ¡Corregido! Antes decía 'user_id'
    fixed_service_id = fields.Int(allow_none=True) # Para mapear los servicios fijos
    created_at = fields.DateTime(dump_only=True)

expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)