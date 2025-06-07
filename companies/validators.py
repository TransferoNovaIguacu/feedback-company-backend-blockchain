from validate_docbr import CNPJ
from django.core.exceptions import ValidationError

def validate_cnpj(value):
    
    cnpj = ''.join(filter(str.isdigit, value))
    validator = CNPJ()
    if not validator.validate(cnpj):
        raise ValidationError("CNPJ inválido.")