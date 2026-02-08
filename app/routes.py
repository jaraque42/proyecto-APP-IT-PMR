from flask import Blueprint, render_template, request, redirect, url_for, flash,current_app, send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
from app import db
from app.models import Device, Reception, Delivery, Incident, User
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import re

ALLOWED_EXT = {'pdf', 'jpg', 'jpeg'}

main = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def valid_imei(imei: str) -> bool:
    if not imei:
        return False
    s = imei.strip()
    return s.isdigit() and len(s) == 15


def valid_user_situm(user: str) -> bool:
    if not user:
        return False
    user = user.strip()
    # require an email ending with @mitie.es (case-insensitive)
    return re.match(r"^[^@\s]+@mitie\.es$", user, re.IGNORECASE) is not None


def valid_name(name: str) -> bool:
    if not name:
        return False
    name = name.strip()
    # must be three words: apellido1 apellido2 nombre
    parts = name.split()
    if len(parts) != 3:
        return False
    # no uppercase, no digits, no commas or dots
    if name != name.lower():
        return False
    if any(ch.isdigit() for ch in name):
        return False
    if ',' in name or '.' in name:
        return False
    return True


def valid_phone(phone: str) -> bool:
    if not phone:
        return False
    p = phone.strip()
    return p.isdigit() and len(p) == 9


@main.route('/export/receptions.csv')
@login_required
def export_receptions():
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))
    import csv, io
    start = request.args.get('start')
    end = request.args.get('end')
    imei = request.args.get('imei')
    name = request.args.get('name')
    q = Reception.query
    if imei:
        imei_s = imei.strip()
        if imei_s:
            q = q.filter(Reception.device_imei.ilike(f"%{imei_s}%"))
    if name:
        name_s = name.strip()
        if name_s:
            q = q.filter(Reception.name.ilike(f"%{name_s}%"))
    if start:
        try:
            sd = datetime.fromisoformat(start)
            q = q.filter(Reception.timestamp >= sd)
        except Exception:
            pass
    if end:
        try:
            ed = datetime.fromisoformat(end) + timedelta(days=1)
            q = q.filter(Reception.timestamp < ed)
        except Exception:
            pass
    si = io.StringIO()
    w = csv.writer(si)
    w.writerow(['id', 'device_id', 'device_imei', 'received_by', 'user_situm', 'name', 'phone', 'notes', 'timestamp'])
    for r in q.order_by(Reception.timestamp.desc()):
        w.writerow([r.id, r.device_id, r.device_imei, r.received_by, r.user_situm, r.name, r.phone, (r.notes or '').replace('\n',' '), r.timestamp])
    output = si.getvalue()
    return current_app.response_class(output, mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=receptions.csv'
    })


@main.route('/export/deliveries.csv')
@login_required
def export_deliveries():
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))
    import csv, io
    start = request.args.get('start')
    end = request.args.get('end')
    imei = request.args.get('imei')
    name = request.args.get('name')
    q = Delivery.query
    if imei:
        imei_s = imei.strip()
        if imei_s:
            q = q.filter(Delivery.device_imei.ilike(f"%{imei_s}%"))
    if name:
        name_s = name.strip()
        if name_s:
            q = q.filter(Delivery.name.ilike(f"%{name_s}%"))
    if start:
        try:
            sd = datetime.fromisoformat(start)
            q = q.filter(Delivery.timestamp >= sd)
        except Exception:
            pass
    if end:
        try:
            ed = datetime.fromisoformat(end) + timedelta(days=1)
            q = q.filter(Delivery.timestamp < ed)
        except Exception:
            pass
    si = io.StringIO()
    w = csv.writer(si)
    w.writerow(['id', 'device_id', 'device_imei', 'delivered_to', 'user_situm', 'name', 'phone', 'notes', 'timestamp'])
    for d in q.order_by(Delivery.timestamp.desc()):
        w.writerow([d.id, d.device_id, d.device_imei, d.delivered_to, d.user_situm, d.name, d.phone, (d.notes or '').replace('\n',' '), d.timestamp])
    output = si.getvalue()
    return current_app.response_class(output, mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=deliveries.csv'
    })


@main.route('/export/incidents.csv')
@login_required
def export_incidents():
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))
    import csv, io
    start = request.args.get('start')
    end = request.args.get('end')
    imei = request.args.get('imei')
    name = request.args.get('name')
    q = Incident.query
    if imei:
        imei_s = imei.strip()
        if imei_s:
            q = q.filter(Incident.device_imei.ilike(f"%{imei_s}%"))
    if name:
        name_s = name.strip()
        if name_s:
            q = q.filter(Incident.reported_by.ilike(f"%{name_s}%"))
    if start:
        try:
            sd = datetime.fromisoformat(start)
            q = q.filter(Incident.timestamp >= sd)
        except Exception:
            pass
    if end:
        try:
            ed = datetime.fromisoformat(end) + timedelta(days=1)
            q = q.filter(Incident.timestamp < ed)
        except Exception:
            pass
    si = io.StringIO()
    w = csv.writer(si)
    w.writerow(['id', 'device_id', 'device_imei', 'reported_by', 'phone', 'file_path', 'description', 'timestamp'])
    for it in q.order_by(Incident.timestamp.desc()):
        w.writerow([it.id, it.device_id, it.device_imei, it.reported_by, it.phone, it.file_path or '', (it.description or '').replace('\n',' '), it.timestamp])
    output = si.getvalue()
    return current_app.response_class(output, mimetype='text/csv', headers={
        'Content-Disposition': 'attachment; filename=incidents.csv'
    })


@main.route('/uploads/<int:incident_id>/file')
@login_required
def download_incident_file(incident_id):
    inc = Incident.query.get_or_404(incident_id)
    if not inc.file_path:
        flash('Archivo no disponible', 'warning')
        return redirect(url_for('main.history_incidents'))
    directory, filename = os.path.split(inc.file_path)
    # send file as attachment
    return send_from_directory(directory, filename, as_attachment=True)


@main.route('/')
@login_required
def index():
    return render_template('index.html')


@main.route('/receive', methods=['POST'])
@login_required
def receive():
    imei = request.form.get('imei')
    received_by = request.form.get('received_by') or (current_user.username if hasattr(current_user, 'username') else None)
    user_situm = request.form.get('user_situm')
    name = request.form.get('name')
    phone = request.form.get('phone')
    notes = request.form.get('notes')
    if not imei:
        flash('IMEI requerido', 'warning')
        return redirect(url_for('main.index'))
    # server-side validations
    if not valid_imei(imei):
        flash('IMEI inválido: debe contener 15 dígitos numéricos', 'warning')
        return redirect(url_for('main.index'))
    if not valid_user_situm(user_situm):
        flash('Usuario Situm inválido: debe ser un email en el dominio mitie.es', 'warning')
        return redirect(url_for('main.index'))
    if not valid_name(name):
        flash('Nombre inválido: debe ser "apellido1 apellido2 nombre", en minúsculas y sin números, comas ni puntos', 'warning')
        return redirect(url_for('main.index'))
    if not valid_phone(phone):
        flash('Teléfono inválido: debe contener exactamente 9 dígitos', 'warning')
        return redirect(url_for('main.index'))
    device = Device.query.filter_by(imei=imei).first()
    if not device:
        device = Device(imei=imei)
        db.session.add(device)
        db.session.commit()
    rec = Reception(device_id=device.id, device_imei=device.imei, received_by=received_by, user_situm=user_situm, name=name, phone=phone, notes=notes)
    db.session.add(rec)
    db.session.commit()
    flash('Recepción creada', 'success')
    return redirect(url_for('main.index'))


@main.route('/deliver', methods=['POST'])
@login_required
def deliver():
    imei = request.form.get('imei')
    delivered_to = request.form.get('delivered_to')
    user_situm = request.form.get('user_situm')
    name = request.form.get('name')
    phone = request.form.get('phone')
    notes = request.form.get('notes')
    if not imei:
        flash('IMEI requerido', 'warning')
        return redirect(url_for('main.index'))
    # server-side validations
    if not valid_imei(imei):
        flash('IMEI inválido: debe contener 15 dígitos numéricos', 'warning')
        return redirect(url_for('main.index'))
    if not valid_user_situm(user_situm):
        flash('Usuario Situm inválido: debe ser un email en el dominio mitie.es', 'warning')
        return redirect(url_for('main.index'))
    if not valid_name(name):
        flash('Nombre inválido: debe ser "apellido1 apellido2 nombre", en minúsculas y sin números, comas ni puntos', 'warning')
        return redirect(url_for('main.index'))
    if not valid_phone(phone):
        flash('Teléfono inválido: debe contener exactamente 9 dígitos', 'warning')
        return redirect(url_for('main.index'))
    device = Device.query.filter_by(imei=imei).first()
    if not device:
        flash('Dispositivo no encontrado', 'warning')
        return redirect(url_for('main.index'))
    d = Delivery(device_id=device.id, device_imei=device.imei, delivered_to=delivered_to, user_situm=user_situm, name=name, phone=phone, notes=notes)
    db.session.add(d)
    db.session.commit()
    flash('Entrega creada', 'success')
    return redirect(url_for('main.index'))


@main.route('/incident', methods=['POST'])
@login_required
def incident():
    imei = request.form.get('imei')
    description = request.form.get('description')
    reported_by = request.form.get('user') or request.form.get('reported_by')
    phone = request.form.get('phone')
    f = request.files.get('file')
    if not imei:
        flash('IMEI requerido', 'warning')
        return redirect(url_for('main.index'))
    # server-side validations for incident reporter and phone
    if not valid_imei(imei):
        flash('IMEI inválido: debe contener 15 dígitos numéricos', 'warning')
        return redirect(url_for('main.index'))
    # reported_by may be an email (user) or a name; if it's an email, enforce mitie.es
    if reported_by and '@' in reported_by and not valid_user_situm(reported_by):
        flash('Usuario Situm inválido: si se indica email debe pertenecer a mitie.es', 'warning')
        return redirect(url_for('main.index'))
    if phone and not valid_phone(phone):
        flash('Teléfono inválido: debe contener exactamente 9 dígitos', 'warning')
        return redirect(url_for('main.index'))
    device = Device.query.filter_by(imei=imei).first()
    if not device:
        device = Device(imei=imei)
        db.session.add(device)
        db.session.commit()
    file_path = None
    if f and f.filename:
        if not allowed_file(f.filename):
            flash('Tipo de archivo no permitido', 'warning')
            return redirect(url_for('main.index'))
        filename = secure_filename(f.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', '/app/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        dest = os.path.join(upload_folder, f"{device.id}_" + filename)
        f.save(dest)
        # server-side size check
        try:
            max_bytes = current_app.config.get('MAX_CONTENT_LENGTH') or (16 * 1024 * 1024)
            if os.path.getsize(dest) > max_bytes:
                os.remove(dest)
                flash('Archivo demasiado grande', 'warning')
                return redirect(url_for('main.index'))
        except Exception:
            pass
        file_path = dest
    inc = Incident(device_id=device.id, device_imei=device.imei, description=description, reported_by=reported_by, phone=phone, file_path=file_path)
    db.session.add(inc)
    db.session.commit()
    flash('Incidencia registrada', 'success')
    return redirect(url_for('main.index'))


@main.route('/history/receptions')
@login_required
def history_receptions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start = request.args.get('start')
    end = request.args.get('end')
    imei = request.args.get('imei')
    name = request.args.get('name')
    q = Reception.query
    if imei:
        imei_s = imei.strip()
        if imei_s:
            q = q.filter(Reception.device_imei.ilike(f"%{imei_s}%"))
    if name:
        name_s = name.strip()
        if name_s:
            q = q.filter(Reception.name.ilike(f"%{name_s}%"))
    if start:
        try:
            sd = datetime.fromisoformat(start)
            q = q.filter(Reception.timestamp >= sd)
        except Exception:
            pass
    if end:
        try:
            ed = datetime.fromisoformat(end) + timedelta(days=1)
            q = q.filter(Reception.timestamp < ed)
        except Exception:
            pass
    pagination = q.order_by(Reception.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    return render_template('history_receptions.html', items=items, pagination=pagination, start=start, end=end, per_page=per_page, imei=imei, name=name)


@main.route('/history/deliveries')
@login_required
def history_deliveries():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start = request.args.get('start')
    end = request.args.get('end')
    imei = request.args.get('imei')
    name = request.args.get('name')
    q = Delivery.query
    if imei:
        imei_s = imei.strip()
        if imei_s:
            q = q.filter(Delivery.device_imei.ilike(f"%{imei_s}%"))
    if name:
        name_s = name.strip()
        if name_s:
            q = q.filter(Delivery.name.ilike(f"%{name_s}%"))
    if start:
        try:
            sd = datetime.fromisoformat(start)
            q = q.filter(Delivery.timestamp >= sd)
        except Exception:
            pass
    if end:
        try:
            ed = datetime.fromisoformat(end) + timedelta(days=1)
            q = q.filter(Delivery.timestamp < ed)
        except Exception:
            pass
    pagination = q.order_by(Delivery.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    return render_template('history_deliveries.html', items=items, pagination=pagination, start=start, end=end, per_page=per_page, imei=imei, name=name)


@main.route('/history/incidents')
@login_required
def history_incidents():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start = request.args.get('start')
    end = request.args.get('end')
    imei = request.args.get('imei')
    name = request.args.get('name')
    q = Incident.query
    if imei:
        imei_s = imei.strip()
        if imei_s:
            q = q.filter(Incident.device_imei.ilike(f"%{imei_s}%"))
    if name:
        name_s = name.strip()
        if name_s:
            q = q.filter(Incident.reported_by.ilike(f"%{name_s}%"))
    if start:
        try:
            sd = datetime.fromisoformat(start)
            q = q.filter(Incident.timestamp >= sd)
        except Exception:
            pass
    if end:
        try:
            ed = datetime.fromisoformat(end) + timedelta(days=1)
            q = q.filter(Incident.timestamp < ed)
        except Exception:
            pass
    pagination = q.order_by(Incident.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = pagination.items
    return render_template('history_incidents.html', items=items, pagination=pagination, start=start, end=end, per_page=per_page, imei=imei, name=name)


@main.route('/reception/<int:reception_id>/delete', methods=['POST'])
@login_required
def delete_reception(reception_id):
    rec = Reception.query.get_or_404(reception_id)
    action = request.form.get('action', 'partial')
    password = request.form.get('password')
    # full deletion: only admin and require admin password
    if action == 'full':
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.history_receptions'))
        if not password or not current_user.check_password(password):
            flash('Contraseña de administrador incorrecta', 'warning')
            return redirect(url_for('main.history_receptions'))
        db.session.delete(rec)
        db.session.commit()
        flash('Registro eliminado completamente', 'success')
        return redirect(url_for('main.history_receptions'))
    # partial deletion: admin or operator, require user's own password
    if current_user.role not in ('admin','operator'):
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.history_receptions'))
    if not password or not current_user.check_password(password):
        flash('Contraseña incorrecta', 'warning')
        return redirect(url_for('main.history_receptions'))
    # anonymize fields
    rec.name = None
    rec.phone = None
    rec.notes = '[ANONIMIZADO]'
    db.session.commit()
    flash('Registro anonimizado (parcial)', 'success')
    return redirect(url_for('main.history_receptions'))


@main.route('/delivery/<int:delivery_id>/delete', methods=['POST'])
@login_required
def delete_delivery(delivery_id):
    d = Delivery.query.get_or_404(delivery_id)
    action = request.form.get('action', 'partial')
    password = request.form.get('password')
    if action == 'full':
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.history_deliveries'))
        if not password or not current_user.check_password(password):
            flash('Contraseña de administrador incorrecta', 'warning')
            return redirect(url_for('main.history_deliveries'))
        db.session.delete(d)
        db.session.commit()
        flash('Registro eliminado completamente', 'success')
        return redirect(url_for('main.history_deliveries'))
    if current_user.role not in ('admin','operator'):
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.history_deliveries'))
    if not password or not current_user.check_password(password):
        flash('Contraseña incorrecta', 'warning')
        return redirect(url_for('main.history_deliveries'))
    d.delivered_to = None
    d.name = None
    d.phone = None
    d.notes = '[ANONIMIZADO]'
    db.session.commit()
    flash('Registro anonimizado (parcial)', 'success')
    return redirect(url_for('main.history_deliveries'))


@main.route('/incident/<int:incident_id>/delete', methods=['POST'])
@login_required
def delete_incident(incident_id):
    it = Incident.query.get_or_404(incident_id)
    action = request.form.get('action', 'partial')
    password = request.form.get('password')
    if action == 'full':
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.history_incidents'))
        if not password or not current_user.check_password(password):
            flash('Contraseña de administrador incorrecta', 'warning')
            return redirect(url_for('main.history_incidents'))
        # remove any file
        if it.file_path and os.path.exists(it.file_path):
            try:
                os.remove(it.file_path)
            except Exception:
                pass
        db.session.delete(it)
        db.session.commit()
        flash('Incidencia eliminada completamente', 'success')
        return redirect(url_for('main.history_incidents'))
    if current_user.role not in ('admin','operator'):
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.history_incidents'))
    if not password or not current_user.check_password(password):
        flash('Contraseña incorrecta', 'warning')
        return redirect(url_for('main.history_incidents'))
    # anonymize
    it.reported_by = None
    it.phone = None
    it.description = '[ANONIMIZADO]'
    if it.file_path and os.path.exists(it.file_path):
        try:
            os.remove(it.file_path)
        except Exception:
            pass
        it.file_path = None
    db.session.commit()
    flash('Incidencia anonimizada (parcial)', 'success')
    return redirect(url_for('main.history_incidents'))


@main.route('/receptions/delete_bulk', methods=['POST'])
@login_required
def receptions_bulk_delete():
    raw_action = request.form.get('action') or request.form.get('action_button') or request.values.get('action')
    # action can be like 'selected_partial', 'all_full' or simple 'full'/'partial'
    target = 'selected'
    action = 'partial'
    if raw_action:
        if '_' in raw_action:
            target, action = raw_action.split('_', 1)
        else:
            action = raw_action
    password = request.form.get('password')
    start = request.form.get('start')
    end = request.form.get('end')
    imei = request.form.get('imei')
    name = request.form.get('name')
    selected = request.form.getlist('selected_ids')
    ids = []
    if target == 'all':
        q = Reception.query
        if imei:
            imei_s = imei.strip()
            if imei_s:
                q = q.filter(Reception.device_imei.ilike(f"%{imei_s}%"))
        if name:
            name_s = name.strip()
            if name_s:
                q = q.filter(Reception.name.ilike(f"%{name_s}%"))
        if start:
            try:
                sd = datetime.fromisoformat(start)
                q = q.filter(Reception.timestamp >= sd)
            except Exception:
                pass
        if end:
            try:
                ed = datetime.fromisoformat(end) + timedelta(days=1)
                q = q.filter(Reception.timestamp < ed)
            except Exception:
                pass
        ids = [r.id for r in q.all()]
    else:
        ids = [int(i) for i in selected if i]

    if action == 'full':
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.history_receptions'))
        if not password or not current_user.check_password(password):
            flash('Contraseña de administrador incorrecta', 'warning')
            return redirect(url_for('main.history_receptions'))
        for _id in ids:
            r = Reception.query.get(_id)
            if r:
                db.session.delete(r)
        db.session.commit()
        flash('Registros eliminados completamente', 'success')
        return redirect(url_for('main.history_receptions', start=start, end=end, imei=imei, name=name))

    # partial
    if current_user.role not in ('admin', 'operator'):
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.history_receptions'))
    if not password or not current_user.check_password(password):
        flash('Contraseña incorrecta', 'warning')
        return redirect(url_for('main.history_receptions'))
    for _id in ids:
        r = Reception.query.get(_id)
        if r:
            r.name = None
            r.phone = None
            r.notes = '[ANONIMIZADO]'
    db.session.commit()
    flash('Registros anonimizados (parcial)', 'success')
    return redirect(url_for('main.history_receptions', start=start, end=end, imei=imei, name=name))


@main.route('/deliveries/delete_bulk', methods=['POST'])
@login_required
def deliveries_bulk_delete():
    raw_action = request.form.get('action') or request.values.get('action')
    target = 'selected'
    action = 'partial'
    if raw_action:
        if '_' in raw_action:
            target, action = raw_action.split('_', 1)
        else:
            action = raw_action
    password = request.form.get('password')
    start = request.form.get('start')
    end = request.form.get('end')
    imei = request.form.get('imei')
    name = request.form.get('name')
    selected = request.form.getlist('selected_ids')
    ids = []
    if target == 'all':
        q = Delivery.query
        if imei:
            imei_s = imei.strip()
            if imei_s:
                q = q.filter(Delivery.device_imei.ilike(f"%{imei_s}%"))
        if name:
            name_s = name.strip()
            if name_s:
                q = q.filter(Delivery.name.ilike(f"%{name_s}%"))
        if start:
            try:
                sd = datetime.fromisoformat(start)
                q = q.filter(Delivery.timestamp >= sd)
            except Exception:
                pass
        if end:
            try:
                ed = datetime.fromisoformat(end) + timedelta(days=1)
                q = q.filter(Delivery.timestamp < ed)
            except Exception:
                pass
        ids = [d.id for d in q.all()]
    else:
        ids = [int(i) for i in selected if i]

    if action == 'full':
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.history_deliveries'))
        if not password or not current_user.check_password(password):
            flash('Contraseña de administrador incorrecta', 'warning')
            return redirect(url_for('main.history_deliveries'))
        for _id in ids:
            d = Delivery.query.get(_id)
            if d:
                db.session.delete(d)
        db.session.commit()
        flash('Registros eliminados completamente', 'success')
        return redirect(url_for('main.history_deliveries', start=start, end=end, imei=imei, name=name))

    # partial
    if current_user.role not in ('admin', 'operator'):
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.history_deliveries'))
    if not password or not current_user.check_password(password):
        flash('Contraseña incorrecta', 'warning')
        return redirect(url_for('main.history_deliveries'))
    for _id in ids:
        d = Delivery.query.get(_id)
        if d:
            d.delivered_to = None
            d.name = None
            d.phone = None
            d.notes = '[ANONIMIZADO]'
    db.session.commit()
    flash('Registros anonimizados (parcial)', 'success')
    return redirect(url_for('main.history_deliveries', start=start, end=end, imei=imei, name=name))


@main.route('/incidents/delete_bulk', methods=['POST'])
@login_required
def incidents_bulk_delete():
    raw_action = request.form.get('action') or request.values.get('action')
    target = 'selected'
    action = 'partial'
    if raw_action:
        if '_' in raw_action:
            target, action = raw_action.split('_', 1)
        else:
            action = raw_action
    password = request.form.get('password')
    start = request.form.get('start')
    end = request.form.get('end')
    imei = request.form.get('imei')
    name = request.form.get('name')
    selected = request.form.getlist('selected_ids')
    ids = []
    if target == 'all':
        q = Incident.query
        if imei:
            imei_s = imei.strip()
            if imei_s:
                q = q.filter(Incident.device_imei.ilike(f"%{imei_s}%"))
        if name:
            name_s = name.strip()
            if name_s:
                q = q.filter(Incident.reported_by.ilike(f"%{name_s}%"))
        if start:
            try:
                sd = datetime.fromisoformat(start)
                q = q.filter(Incident.timestamp >= sd)
            except Exception:
                pass
        if end:
            try:
                ed = datetime.fromisoformat(end) + timedelta(days=1)
                q = q.filter(Incident.timestamp < ed)
            except Exception:
                pass
        ids = [it.id for it in q.all()]
    else:
        ids = [int(i) for i in selected if i]

    if action == 'full':
        if not current_user.is_admin:
            flash('Acceso denegado', 'danger')
            return redirect(url_for('main.history_incidents'))
        if not password or not current_user.check_password(password):
            flash('Contraseña de administrador incorrecta', 'warning')
            return redirect(url_for('main.history_incidents'))
        for _id in ids:
            it = Incident.query.get(_id)
            if it:
                if it.file_path and os.path.exists(it.file_path):
                    try:
                        os.remove(it.file_path)
                    except Exception:
                        pass
                db.session.delete(it)
        db.session.commit()
        flash('Incidencias eliminadas completamente', 'success')
        return redirect(url_for('main.history_incidents', start=start, end=end, imei=imei, name=name))

    # partial
    if current_user.role not in ('admin', 'operator'):
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.history_incidents'))
    if not password or not current_user.check_password(password):
        flash('Contraseña incorrecta', 'warning')
        return redirect(url_for('main.history_incidents'))
    for _id in ids:
        it = Incident.query.get(_id)
        if it:
            it.reported_by = None
            it.phone = None
            it.description = '[ANONIMIZADO]'
            if it.file_path and os.path.exists(it.file_path):
                try:
                    os.remove(it.file_path)
                except Exception:
                    pass
                it.file_path = None
    db.session.commit()
    flash('Incidencias anonimizadas (parcial)', 'success')
    return redirect(url_for('main.history_incidents', start=start, end=end, imei=imei, name=name))


@main.route('/admin/users', methods=['GET','POST'])
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role') or 'operator'
        is_admin_flag = True if role == 'admin' else False
        if not username or not password:
            flash('Usuario y contraseña requeridos', 'warning')
            return redirect(url_for('main.admin_users'))
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'warning')
            return redirect(url_for('main.admin_users'))
        u = User(username=username, is_admin=is_admin_flag, role=role)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash('Usuario creado', 'success')
        return redirect(url_for('main.admin_users'))
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@main.route('/admin/users/<int:user_id>/edit', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))
    u = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role') or 'operator'
        if not username:
            flash('Usuario requerido', 'warning')
            return redirect(url_for('main.edit_user', user_id=user_id))
        # prevent removing own admin rights
        if u.id == current_user.id and role != 'admin':
            flash('No puedes eliminar tus privilegios de administrador', 'warning')
            return redirect(url_for('main.edit_user', user_id=user_id))
        u.username = username
        u.role = role
        u.is_admin = True if role == 'admin' else False
        if password:
            u.set_password(password)
        db.session.commit()
        flash('Usuario actualizado', 'success')
        return redirect(url_for('main.admin_users'))
    return render_template('admin_user_edit.html', user=u)


@main.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('main.index'))
    if user_id == current_user.id:
        flash('No puedes eliminarte a ti mismo', 'warning')
        return redirect(url_for('main.admin_users'))
    u = User.query.get_or_404(user_id)
    db.session.delete(u)
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('main.admin_users'))
