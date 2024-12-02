from flask import render_template, request, jsonify

from app.modules.explore import explore_bp
from app.modules.explore.forms import ExploreForm
from app.modules.explore.services import ExploreService


@explore_bp.route('/explore', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        query = request.args.get('query', '')
        form = ExploreForm()
        return render_template('explore/index.html', form=form, query=query)

    if request.method == 'POST':
        try:
            criteria = request.get_json()
            if not criteria:
                return jsonify({'error': 'Invalid JSON data'}), 400

            required_fields = ['sorting', 'publication_type']
            if not all(field in criteria for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400

            try:
                datasets = ExploreService().filter(**criteria)
                return jsonify([dataset.to_dict() for dataset in datasets])
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        except Exception:
            return jsonify({'error': 'Invalid request'}), 400
