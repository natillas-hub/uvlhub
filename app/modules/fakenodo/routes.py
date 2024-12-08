from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import FakenodoService

fakenodo_service = FakenodoService()


@fakenodo_bp.route('/fakenodo/<deposition_id>', methods=['GET'])
def getDeposition(deposition_id):
    deposition = fakenodo_service.get_deposition(deposition_id)
    return deposition.dep_metadata
