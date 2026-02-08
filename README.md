# Gestión de Recepciones / Entregas / Incidencias de Móviles

Minimal app en Flask para gestionar recepciones, entregas e incidencias de dispositivos móviles.

Arranque con Docker (Debian base):

1. Copiar `.env.example` a `.env` y ajustar credenciales.

2. Levantar con docker-compose:

```bash
docker-compose build
docker-compose up -d
```

3. Crear usuario admin desde shell del contenedor:

```bash
docker-compose exec web flask shell
>>> from app import db
>>> from app.models import User
>>> u = User(username='admin', is_admin=True)
>>> u.set_password('password')
>>> db.session.add(u); db.session.commit()
```

La aplicación escucha en el puerto `8000` y usa PostgreSQL para datos compartidos.
