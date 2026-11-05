"""Controladores MVC: autenticación, permisos, formularios y respuestas HTTP."""
import secrets
import sqlite3
from functools import wraps
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, abort, jsonify, g
from werkzeug.security import check_password_hash, generate_password_hash
from .models import db, rows
from .services import validate, required, email, invalidate

bp = Blueprint('web', __name__)
# Etiqueta, campos visibles y relaciones. Las tablas se seleccionan exclusivamente de esta lista.
ENTITIES = {
 'categories': ('Categorías', [('name','Nombre','text')]),
 'board_types': ('Tipos de tablero', [('category_id','Categoría','categories'),('name','Material / nombre','text'),('thickness','Espesor (mm)','number'),('finish','Acabado','text')]),
 'formats': ('Formatos', [('name','Código de formato','text'),('category_id','Categoría','categories'),('type_id','Tipo de tablero','board_types'),('length','Largo (mm)','number'),('width','Ancho (mm)','number'),('enabled','Habilitado','checkbox')]),
 'clients': ('Clientes', [('name','Nombre','text'),('email','Correo','email')]),
 'settings': ('Configuraciones', [('name','Nombre','text'),('kerf','Ancho de sierra (mm)','number'),('min_length','Largo mínimo reutilizable (mm)','number'),('min_width','Ancho mínimo reutilizable (mm)','number')]),
 'orders': ('Pedidos', [('name','Referencia del pedido','text'),('client_id','Cliente','clients'),('setting_id','Configuración','settings')]),
 'pieces': ('Piezas', [('order_id','Pedido','orders'),('name','Nombre de pieza','text'),('category_id','Categoría','categories'),('type_id','Tipo de tablero','board_types'),('length','Largo (mm)','number'),('width','Ancho (mm)','number'),('quantity','Cantidad','number'),('rotate','Permitir giro de 90°','checkbox')]),
 'users': ('Usuarios', [('name','Nombre','text'),('email','Correo','email'),('role','Rol','role'),('active','Usuario activo','checkbox'),('password','Contraseña (mínimo 10 caracteres)','password')]),
}
ADMIN_ONLY = {'categories','board_types','formats','settings','users'}

@bp.before_request
def security():
    g.user = None
    if session.get('user_id'):
        found = rows('SELECT id,name,email,role FROM users WHERE id=? AND active=1',(session['user_id'],))
        g.user = found[0] if found else None
    if 'csrf' not in session: session['csrf'] = secrets.token_hex(32)
    if request.method == 'POST' and not secrets.compare_digest(session['csrf'],request.form.get('csrf','')):
        abort(400,description='Formulario vencido o inválido. Recarga la página.')

@bp.after_request
def headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'"
    return response

@bp.context_processor
def context(): return {'entities':ENTITIES,'admin_only':ADMIN_ONLY}

def login_required(fn):
    @wraps(fn)
    def inner(*args,**kwargs):
        if not g.user: return redirect(url_for('web.login'))
        return fn(*args,**kwargs)
    return inner

def check_entity(entity):
    if entity not in ENTITIES: abort(404)
    if entity in ADMIN_ONLY and g.user['role']!='admin': abort(403)

@bp.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        user=rows('SELECT * FROM users WHERE email=?',(request.form.get('email','').strip().lower(),))
        if user and user[0]['active'] and check_password_hash(user[0]['password'],request.form.get('password','')):
            session.clear(); session['user_id']=user[0]['id']; session['csrf']=secrets.token_hex(32)
            return redirect(url_for('web.dashboard'))
        flash('Correo o contraseña incorrectos.','error')
    return render_template('login.html')

@bp.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('web.login'))

@bp.get('/')
@login_required
def dashboard():
    counts={key:rows(f'SELECT COUNT(*) n FROM {key}')[0]['n'] for key in ('clients','orders','board_types','formats','pieces')}
    recent=rows('SELECT o.*,c.name client FROM orders o JOIN clients c ON c.id=o.client_id ORDER BY o.id DESC LIMIT 5')
    return render_template('dashboard.html',counts=counts,recent=recent)

@bp.get('/admin/<entity>')
@login_required
def listing(entity):
    check_entity(entity)
    records=[dict(r) for r in rows(f'SELECT * FROM {entity} ORDER BY id DESC')]
    fields=[f for f in ENTITIES[entity][1] if f[0] not in ('password','category_id') or entity=='board_types' and f[0]=='category_id']
    lookups={kind:{r['id']:r['name'] for r in rows(f'SELECT id,name FROM {kind}')} for _,_,kind in fields if kind in ENTITIES}
    return render_template('listing.html',entity=entity,title=ENTITIES[entity][0],fields=fields,records=records,lookups=lookups)

@bp.route('/admin/<entity>/new',methods=['GET','POST'])
@bp.route('/admin/<entity>/<int:record_id>/edit',methods=['GET','POST'])
@login_required
def edit(entity,record_id=None):
    check_entity(entity)
    record={'active':1,'enabled':1}
    if record_id:
        found=rows(f'SELECT * FROM {entity} WHERE id=?',(record_id,))
        if not found: abort(404)
        record=dict(found[0])
    if request.method=='POST':
        try:
            if entity=='users':
                values={'name':required(request.form,'name'),'email':email(request.form),'role':required(request.form,'role'),'active':int(request.form.get('active')=='1')}
                if values['role'] not in ('admin','operador'): raise ValueError('Rol inválido.')
                password=request.form.get('password','')
                if password or not record_id:
                    if not 10<=len(password)<=128: raise ValueError('La contraseña debe tener entre 10 y 128 caracteres.')
                    values['password']=generate_password_hash(password)
                if record_id and record['role']=='admin' and record['active'] and (values['role']!='admin' or not values['active']) and rows("SELECT COUNT(*) n FROM users WHERE role='admin' AND active=1")[0]['n']==1:
                    raise ValueError('Debe existir al menos un administrador.')
            else: values=validate(entity,request.form)
            if entity=='orders' and not record_id: values['user_id']=g.user['id']
            if entity=='pieces' and record_id and rows('SELECT status FROM orders WHERE id=?',(record['order_id'],))[0]['status']=='Cancelado':
                raise ValueError('No se puede modificar un pedido cancelado. Primero vuelve el pedido a Borrador.')
            if entity in ('formats','pieces'):
                category=request.form.get('category_id','')
                if not rows('SELECT id FROM board_types WHERE id=? AND category_id=?',(values['type_id'],category)):
                    raise ValueError('El tipo de tablero no pertenece a la categoría seleccionada.')
            with db():
                if record_id:
                    db().execute(f"UPDATE {entity} SET {','.join(k+'=?' for k in values)} WHERE id=?",(*values.values(),record_id))
                else:
                    db().execute(f"INSERT INTO {entity} ({','.join(values)}) VALUES ({','.join('?' for _ in values)})",tuple(values.values()))
                if entity=='orders' and record_id: invalidate(record_id)
                if entity=='pieces':
                    invalidate(values['order_id'])
                    if record_id and record['order_id']!=values['order_id']: invalidate(record['order_id'])
                # Cambios en datos que alimentan el core requieren revisar los pedidos listos.
                if record_id and entity in ('settings','formats','board_types'):
                    db().execute("UPDATE orders SET status='Borrador',version=version+1 WHERE status='Listo'")
            flash('Registro guardado correctamente.','success')
            return redirect(url_for('web.listing',entity=entity))
        except (ValueError,sqlite3.IntegrityError) as exc:
            flash(str(exc) if isinstance(exc,ValueError) else 'No se pudo guardar: hay un valor duplicado o una relación inválida.','error')
            record=dict(request.form)
            for key in ('active','enabled','rotate'): record.setdefault(key,0)
    if entity in ('formats','pieces') and record.get('type_id') and not record.get('category_id'):
        match=rows('SELECT category_id FROM board_types WHERE id=?',(record['type_id'],))
        if match: record['category_id']=match[0]['category_id']
    options={kind:rows(f'SELECT * FROM {kind} ORDER BY name') for _,_,kind in ENTITIES[entity][1] if kind in ENTITIES}
    return render_template('form.html',entity=entity,title=ENTITIES[entity][0],fields=ENTITIES[entity][1],record=record,options=options,editing=bool(record_id))

@bp.post('/admin/<entity>/<int:record_id>/delete')
@login_required
def delete(entity,record_id):
    check_entity(entity)
    record=rows(f'SELECT * FROM {entity} WHERE id=?',(record_id,))
    if not record: abort(404)
    if entity=='users' and record_id==g.user['id']:
        flash('No puedes eliminar tu propia cuenta.','error')
    elif entity=='users' and record[0]['role']=='admin' and record[0]['active'] and rows("SELECT COUNT(*) n FROM users WHERE role='admin' AND active=1")[0]['n']==1:
        flash('Debe existir al menos un administrador.','error')
    elif entity=='pieces' and rows('SELECT status FROM orders WHERE id=?',(record[0]['order_id'],))[0]['status']=='Cancelado':
        flash('No se puede modificar un pedido cancelado.','error')
    else:
        try:
            with db():
                db().execute(f'DELETE FROM {entity} WHERE id=?',(record_id,))
                if entity=='pieces': invalidate(record[0]['order_id'])
                if entity=='formats': db().execute("UPDATE orders SET status='Borrador',version=version+1 WHERE status='Listo'")
            flash('Registro eliminado.','success')
        except sqlite3.IntegrityError: flash('No se puede eliminar: otros registros dependen de este dato.','error')
    return redirect(url_for('web.listing',entity=entity))

@bp.post('/orders/<int:record_id>/status')
@login_required
def status(record_id):
    found=rows('SELECT * FROM orders WHERE id=?',(record_id,))
    if not found: abort(404)
    state=request.form.get('status')
    try:
        if state not in ('Borrador','Listo','Cancelado'): raise ValueError('Estado inválido.')
        if state=='Listo':
            pieces=rows('SELECT * FROM pieces WHERE order_id=?',(record_id,))
            if not pieces: raise ValueError('Agrega al menos una pieza antes de marcar Listo.')
            for p in pieces: validate('pieces',{k:str(v) for k,v in dict(p).items()})
        with db(): db().execute('UPDATE orders SET status=? WHERE id=?',(state,record_id))
        flash('Estado actualizado.','success')
    except ValueError as exc: flash(str(exc),'error')
    return redirect(url_for('web.listing',entity='orders'))

@bp.get('/api/board-types')
@login_required
def board_types():
    return jsonify([{'id':r['id'],'name':f"{r['name']} · {r['thickness']:g} mm · {r['finish']}"} for r in rows('SELECT * FROM board_types WHERE category_id=? ORDER BY name',(request.args.get('category_id'),))])

@bp.get('/health')
def health():
    db().execute('SELECT 1')
    return {'status':'ok'}

@bp.app_errorhandler(400)
@bp.app_errorhandler(403)
@bp.app_errorhandler(404)
def error_page(error): return render_template('error.html',error=error),error.code
