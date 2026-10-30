from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Resource
from ..utils import role_required, current_user
from ..services.storage import allowed, save_file, send_stored

bp = Blueprint("resources", __name__, url_prefix="/api/resources")
TYPES = {"video", "audio", "article", "pdf", "exercise"}


@bp.get("")
@role_required()
def list_resources():
    q = Resource.query
    if request.args.get("topic_id"):
        q = q.filter_by(topic_id=int(request.args["topic_id"]))
    return jsonify(resources=[r.to_dict() for r in q.order_by(Resource.id.desc()).all()])


@bp.post("")
@role_required("teacher", "admin")
def upload():
    f = request.form
    title = (f.get("title") or "").strip()
    if not title:
        return jsonify(error="Title is required"), 400
    rtype = f.get("type") if f.get("type") in TYPES else "article"
    res = Resource(title=title, type=rtype, url=(f.get("url") or "").strip(), description=f.get("description", ""),
                   topic_id=int(f["topic_id"]) if f.get("topic_id") else None, uploaded_by=current_user().id)
    file = request.files.get("file")
    if file and file.filename:
        if not allowed(file.filename):
            return jsonify(error="This file type is not allowed"), 400
        res.storage_key = save_file(file)
    elif not res.url:
        return jsonify(error="Add a file or a link"), 400
    db.session.add(res)
    db.session.commit()
    return jsonify(resource=res.to_dict()), 201


@bp.get("/<int:rid>/download")
@role_required()
def download(rid):
    res = db.get_or_404(Resource, rid)
    if not res.storage_key:
        return jsonify(error="No file attached"), 404
    return send_stored(res.storage_key)


@bp.delete("/<int:rid>")
@role_required("teacher", "admin")
def delete(rid):
    res = db.get_or_404(Resource, rid)
    db.session.delete(res)
    db.session.commit()
    return jsonify(ok=True)
