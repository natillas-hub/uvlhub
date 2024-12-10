from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import FakenodoService
from flask import abort

fakenodo_service = FakenodoService()


@fakenodo_bp.route('/fakenodo/<deposition_id>', methods=['GET'])
def getDeposition(deposition_id):
    deposition = fakenodo_service.get_deposition(deposition_id)
    if deposition is None:
        abort(404, description="Deposition not found")
    return deposition.dep_metadata
