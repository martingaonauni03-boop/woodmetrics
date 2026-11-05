"""Reglas de negocio ejecutadas en servidor; nunca confía en el formulario."""
import math
from .models import rows, db

def required(data, key):
    value = data.get(key, '').strip()
    if not value or len(value) > 150:
        raise ValueError('Completa los campos de texto (máximo 150 caracteres).')
    return value

def number(data, key, maximum=10000, integer=False):
    try:
        value = float(data.get(key, ''))
    except (TypeError, ValueError):
        raise ValueError('Las medidas y cantidades deben ser numéricas.')
    if not math.isfinite(value) or not 0 < value <= maximum or (integer and value != int(value)):
        raise ValueError(f'{key}: debe ser positivo y no superar {maximum}' + ('; usa un entero.' if integer else '.'))
    return int(value) if integer else value

def reference(data, key, table):
    value = number(data, key, 2147483647, True)
    if not rows(f'SELECT id FROM {table} WHERE id=?', (value,)):
        raise ValueError('La referencia seleccionada no existe.')
    return value

def email(data):
    value = required(data, 'email').lower()
    if value.count('@') != 1 or '.' not in value.split('@')[-1] or any(c.isspace() for c in value):
        raise ValueError('Ingresa un correo válido.')
    return value

def validate(entity, data):
    values = {'name': required(data, 'name')}
    if entity == 'clients': values['email'] = email(data)
    elif entity == 'board_types':
        values.update(category_id=reference(data,'category_id','categories'), thickness=number(data,'thickness',100), finish=required(data,'finish'))
    elif entity == 'formats':
        values.update(type_id=reference(data,'type_id','board_types'), length=number(data,'length'), width=number(data,'width'), enabled=int(data.get('enabled')=='1'))
    elif entity == 'settings':
        values.update(kerf=number(data,'kerf',20), min_length=number(data,'min_length'), min_width=number(data,'min_width'))
    elif entity == 'orders':
        values.update(client_id=reference(data,'client_id','clients'), setting_id=reference(data,'setting_id','settings'))
    elif entity == 'pieces':
        values.update(order_id=reference(data,'order_id','orders'), type_id=reference(data,'type_id','board_types'), length=number(data,'length'), width=number(data,'width'), quantity=number(data,'quantity',1000,True), rotate=int(data.get('rotate')=='1'))
        order = rows('SELECT * FROM orders WHERE id=?',(values['order_id'],))[0]
        if order['status']=='Cancelado': raise ValueError('No se puede modificar un pedido cancelado.')
        formats = rows('SELECT * FROM formats WHERE type_id=? AND enabled=1',(values['type_id'],))
        if not any((values['length']<=f['length'] and values['width']<=f['width']) or (values['rotate'] and values['width']<=f['length'] and values['length']<=f['width']) for f in formats):
            raise ValueError('La pieza no cabe en ningún formato compatible. Revisa las dimensiones y el permiso de giro.')
    return values

def invalidate(order_id):
    db().execute("UPDATE orders SET version=version+1,status='Borrador' WHERE id=?",(order_id,))
