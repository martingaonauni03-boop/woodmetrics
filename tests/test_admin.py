import tempfile
import unittest
from pathlib import Path
from werkzeug.security import generate_password_hash
from woodmetrics import create_app
from woodmetrics.models import db, rows
from woodmetrics.controllers import ENTITIES

class AdminTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.app=create_app({'TESTING':True,'SECRET_KEY':'test-only','DATABASE':str(Path(self.tmp.name)/'test.sqlite')})
        with self.app.app_context():
            with db():
                db().execute('INSERT INTO users(name,email,password,role) VALUES (?,?,?,?)',('Admin','admin@example.com',generate_password_hash('test-password'),'admin'))
                db().execute("INSERT INTO users(name,email,password,role) VALUES ('Operador','op@example.com',?,'operador')",(generate_password_hash('test-password'),))
        self.app.test_cli_runner().invoke(args=['seed-demo'])
        self.client=self.app.test_client()
        self.client.get('/login')
        self.post('/login',{'email':'admin@example.com','password':'test-password'})

    def tearDown(self): self.tmp.cleanup()

    def post(self,path,data):
        with self.client.session_transaction() as session: token=session['csrf']
        return self.client.post(path,data={**data,'csrf':token},follow_redirects=True)

    def count(self,table):
        with self.app.app_context(): return rows(f'SELECT COUNT(*) n FROM {table}')[0]['n']

    def test_all_pages_and_forms_render(self):
        self.assertEqual(self.client.get('/').status_code,200)
        for entity in ENTITIES:
            for path in (f'/admin/{entity}',f'/admin/{entity}/new',f'/admin/{entity}/1/edit'):
                self.assertEqual(self.client.get(path).status_code,200,path)

    def test_server_rejects_invalid_sensitive_numbers(self):
        for kerf in ('0','-3','21','nan','inf','not-a-number'):
            response=self.post('/admin/settings/new',{'name':'Invalid','kerf':kerf,'min_length':'200','min_width':'100'})
            self.assertIn('error',response.text)
        self.assertEqual(self.count('settings'),1)

    def test_relations_rejected_even_with_forged_request(self):
        data={'name':'TEST','category_id':'2','type_id':'1','length':'1000','width':'1000','enabled':'1'}
        response=self.post('/admin/formats/new',data)
        self.assertIn('no pertenece',response.text)
        data['type_id']='999'
        self.assertIn('no existe',self.post('/admin/formats/new',data).text)
        self.assertEqual(self.count('formats'),4)

    def test_dependent_options_and_api(self):
        response=self.client.get('/api/board-types?category_id=2')
        self.assertEqual([r['id'] for r in response.json],[3])
        form=self.client.get('/admin/formats/new').text
        self.assertIn('data-category="2"',form)
        self.assertIn('id="category_id"',form)

    def test_piece_dimensions_and_rotation(self):
        data={'order_id':'1','category_id':'1','type_id':'1','name':'Rotación','length':'900','width':'1400','quantity':'1'}
        self.assertIn('no cabe',self.post('/admin/pieces/new',data).text)
        self.assertEqual(self.count('pieces'),1)
        self.post('/admin/pieces/new',{**data,'rotate':'1'})
        self.assertEqual(self.count('pieces'),2)
        with self.app.app_context(): self.assertEqual(rows('SELECT version FROM orders WHERE id=1')[0]['version'],2)

    def test_order_state_and_invalidation(self):
        self.post('/orders/1/status',{'status':'Listo'})
        self.post('/admin/pieces/1/edit',{'order_id':'1','category_id':'1','type_id':'1','name':'Entrepaño','length':'590','width':'490','quantity':'5','rotate':'1'})
        with self.app.app_context():
            order=rows('SELECT * FROM orders WHERE id=1')[0]
            self.assertEqual(order['status'],'Borrador'); self.assertEqual(order['version'],2)

    def test_empty_order_cannot_be_ready(self):
        self.post('/admin/orders/new',{'name':'Vacío','client_id':'1','setting_id':'1'})
        self.assertIn('al menos una pieza',self.post('/orders/2/status',{'status':'Listo'}).text)

    def test_delete_referenced_data_is_blocked(self):
        response=self.post('/admin/categories/1/delete',{})
        self.assertIn('otros registros dependen',response.text)
        self.assertEqual(self.count('categories'),2)

    def test_csrf_and_permissions(self):
        self.assertEqual(self.client.post('/admin/clients/new',data={'name':'Injected'}).status_code,400)
        self.post('/logout',{})
        self.client.get('/login')
        self.assertEqual(self.client.get('/admin/clients').status_code,302)
        self.post('/login',{'email':'op@example.com','password':'test-password'})
        self.assertEqual(self.client.get('/admin/users').status_code,403)
        self.assertEqual(self.post('/admin/settings/new',{}).status_code,403)
        self.assertEqual(self.client.get('/admin/pieces').status_code,200)

    def test_password_hash_and_unique_email(self):
        self.post('/admin/users/new',{'name':'Nuevo','email':'new@example.com','role':'operador','active':'1','password':'strong-password'})
        with self.app.app_context(): self.assertNotEqual(rows("SELECT password FROM users WHERE email='new@example.com'")[0]['password'],'strong-password')
        self.post('/admin/users/new',{'name':'Duplicado','email':'new@example.com','role':'operador','password':'strong-password'})
        self.assertEqual(self.count('users'),3)

    def test_crud_client(self):
        self.post('/admin/clients/new',{'name':'Nuevo','email':'new@example.com'})
        self.assertEqual(self.count('clients'),2)
        self.post('/admin/clients/2/edit',{'name':'Editado','email':'updated@example.com'})
        self.assertIn('Editado',self.client.get('/admin/clients').text)
        self.post('/admin/clients/2/delete',{})
        self.assertEqual(self.count('clients'),1)

    def test_last_admin_cannot_be_disabled(self):
        result=self.post('/admin/users/1/edit',{'name':'Admin','email':'admin@example.com','role':'admin'})
        self.assertIn('al menos un administrador',result.text)
        with self.app.app_context(): self.assertEqual(rows('SELECT active FROM users WHERE id=1')[0]['active'],1)

    def test_disabled_format_cannot_feed_core(self):
        self.post('/admin/formats/1/edit',{'name':'MDF-1200','type_id':'1','category_id':'1','length':'1200','width':'1000'})
        self.post('/admin/formats/2/edit',{'name':'MDF-1500','type_id':'1','category_id':'1','length':'1500','width':'1000'})
        self.assertIn('no cabe',self.post('/admin/pieces/new',{'order_id':'1','category_id':'1','type_id':'1','name':'Sin formatos','length':'100','width':'100','quantity':'1'}).text)

if __name__=='__main__': unittest.main()
