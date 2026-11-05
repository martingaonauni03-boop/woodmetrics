"""Vista de revisión desechable. No usar este usuario ni este servidor en producción."""
import sys
from pathlib import Path
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from woodmetrics import create_app
from woodmetrics.models import db
from werkzeug.security import generate_password_hash

if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='woodmetrics-qa-') as directory:
        app=create_app({'DATABASE':str(Path(directory)/'qa.sqlite'),'SECRET_KEY':'local-qa-only'})
        app.test_cli_runner().invoke(args=['seed-demo'])
        with app.app_context():
            with db(): db().execute('INSERT INTO users(name,email,password,role) VALUES (?,?,?,?)',('Revisión local','preview@example.com',generate_password_hash('LocalPreview2026!'),'admin'))
        app.run(host='127.0.0.1',port=5000,debug=False)
