from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    client = app.test_client()
    # try to login as admin if exists
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        # login via test client post to auth.login
        resp = client.post('/auth/login', data={'username': admin.username, 'password': 'password'}, follow_redirects=True)
        print('Login status code:', resp.status_code)
    else:
        print('No admin user found; will test routes without login (expect redirect)')

    routes = ['/history/receptions', '/history/deliveries', '/history/incidents']
    for r in routes:
        try:
            resp = client.get(r)
            print(f'GET {r} ->', resp.status_code)
            if resp.status_code >= 400:
                print(resp.get_data(as_text=True)[:1000])
        except Exception as e:
            print(f'EXCEPTION requesting {r}:', repr(e))
