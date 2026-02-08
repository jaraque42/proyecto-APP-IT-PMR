import os
from app import create_app, db
from app.models import User


def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        admin_user = os.environ.get('ADMIN_USER')
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        if admin_user and admin_pass:
            u = User.query.filter_by(username=admin_user).first()
            if not u:
                u = User(username=admin_user, is_admin=True)
                u.set_password(admin_pass)
                db.session.add(u)
                db.session.commit()
                print('Admin user created')
            else:
                print('Admin user already exists')
        else:
            print('ADMIN_USER or ADMIN_PASSWORD not set; skipping admin creation')


if __name__ == '__main__':
    init_db()
