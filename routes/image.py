# routes/image.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Image
from utils.replicate import generate_image  # Import the synchronous function
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
import os
from datetime import datetime

image_bp = Blueprint('image', __name__)

class ImageForm(FlaskForm):
    prompt = TextAreaField('Enter Image Description', validators=[DataRequired(), Length(min=5, max=500)])
    style = TextAreaField('Enter Style (optional)', validators=[Length(max=100)])
    submit = SubmitField('Generate Image')

@image_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    form = ImageForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            prompt = form.prompt.data
            style = form.style.data if form.style.data else "Default"
            try:
                # Generate image and get the saved image path
                image_path = generate_image(prompt, style, user_id=current_user.id)
                
                # Save to database
                new_image = Image(
                    prompt=prompt,
                    image_path=image_path,
                    user_id=current_user.id
                )
                db.session.add(new_image)
                db.session.commit()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # If AJAX request, return JSON response
                    return jsonify({
                        'success': True,
                        'image': {
                            'id': new_image.id,
                            'prompt': new_image.prompt,
                            'image_path': url_for('static', filename=new_image.image_path),
                            'created_at': new_image.generated_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    })
                
                flash('Image generated successfully!', 'success')
                return redirect(url_for('image.generate'))
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': str(e)}), 400
                flash(f"Image generation failed: {str(e)}", 'danger')
    
    # Get user's images for initial display
    images = Image.query.filter_by(user_id=current_user.id).order_by(Image.generated_at.desc()).all()
    return render_template('generate.html', form=form, images=images)

@image_bp.route('/gallery')
@login_required
def gallery():
    images = Image.query.filter_by(user_id=current_user.id).order_by(Image.generated_at.desc()).all()
    # Add debug logging
    for image in images:
        print(f"Image ID: {image.id}, Path: {image.image_path}")
    return render_template('gallery.html', images=images)

@image_bp.route('/api/images/<int:image_id>')
@login_required
def get_image_details(image_id):
    image = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': image.id,
        'prompt': image.prompt,
        'image_path': url_for('static', filename=image.image_path),
        'created_at': image.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
        'model': 'FLUX.1 [schnell]'
    })

@image_bp.route('/api/images/<int:image_id>', methods=['DELETE'])
@login_required
def delete_image(image_id):
    image = Image.query.filter_by(id=image_id, user_id=current_user.id).first_or_404()
    
    try:
        # Delete the actual image file
        file_path = os.path.join('static', image.image_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Image deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
