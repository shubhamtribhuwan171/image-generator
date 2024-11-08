# routes/sample.py

from flask import Blueprint, jsonify
from flask_login import login_required, current_user

sample_bp = Blueprint('sample', __name__)

@sample_bp.route('/protected')
@login_required
def protected():
    return jsonify({'message': f'Hello, {current_user.username}! This is a protected route.'}), 200


@sample_bp.route('/test')
def test():
    return jsonify({
        'message': 'Server is working!',
        'status': 'success'
    }), 200