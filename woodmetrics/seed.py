import click
from werkzeug.security import generate_password_hash
from .models import db, rows

def register_commands(app):
    @app.cli.command('create-admin')
    @click.option('--email',prompt=True)
    @click.option('--password',prompt=True,hide_input=True,confirmation_prompt=True)
    def create_admin(email,password):
        if not 10<=len(password)<=128: raise click.ClickException('Usa entre 10 y 128 caracteres.')
        from .services import email as validate_email
        try: email=validate_email({'email':email})
        except ValueError as exc: raise click.ClickException(str(exc)) from exc
        try:
            with db(): db().execute('INSERT INTO users(name,email,password,role) VALUES (?,?,?,?)',('Administrador',email.strip().lower(),generate_password_hash(password),'admin'))
        except Exception as exc: raise click.ClickException('No se pudo crear el usuario; revisa si el correo ya existe.') from exc
        click.echo('Administrador creado.')

    @app.cli.command('seed-demo')
    def seed_demo():
        """Datos ficticios para la demostración. No crea contraseñas públicas."""
        if rows('SELECT id FROM categories'): raise click.ClickException('La base ya tiene categorías. No se modificó.')
        with db():
            db().execute("INSERT INTO categories(name) VALUES ('Melamínicos'),('Contrachapados')")
            db().execute("INSERT INTO board_types(category_id,name,thickness,finish) VALUES (1,'MDF',18,'Roble natural'),(1,'Aglomerado',15,'Blanco mate'),(2,'Plywood',12,'Natural')")
            db().execute("INSERT INTO formats(type_id,name,length,width) VALUES (1,'MDF-1200',1200,1000),(1,'MDF-1500',1500,1000),(2,'AGL-2440',2440,1830),(3,'PLY-2440',2440,1220)")
            db().execute("INSERT INTO settings(name,kerf,min_length,min_width) VALUES ('Sierra estándar',3,200,100)")
            db().execute("INSERT INTO clients(name,email) VALUES ('Carpintería Bosque · Demo','bosque@example.com')")
            db().execute("INSERT INTO orders(client_id,setting_id,name) VALUES (1,1,'Estantería de roble · Demo')")
            db().execute("INSERT INTO pieces(order_id,type_id,name,length,width,quantity,rotate) VALUES (1,1,'Entrepaño',590,490,4,1)")
        click.echo('Datos ficticios creados. Ejecuta create-admin para habilitar el acceso.')
