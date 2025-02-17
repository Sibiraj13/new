from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'library_secret_key'

# Set the upload folder to static/uploads so that the files are accessible via url_for('static', ...)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    added_by = db.Column(db.String(100), nullable=False)
    pdf_file = db.Column(db.String(100), nullable=True)
    image_file = db.Column(db.String(100), nullable=True)

# Routes
@app.route('/')
def home():
    materials = Material.query.all()
    return render_template('index.html', materials=materials)

@app.route('/admin')
def admin():
    students = Student.query.all()
    materials = Material.query.all()
    return render_template('admin.html', students=students, materials=materials)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        # Check if fields are empty
        if not name or not email or not course:
            flash('All fields are required!')
            return redirect(url_for('register'))
        
        if Student.query.filter_by(email=email).first():
            flash('Email already registered!')
            return redirect(url_for('register'))
        
        new_student = Student(name=name, email=email, course=course)
        db.session.add(new_student)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/add_material', methods=['GET', 'POST'])
def add_material():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        added_by = request.form['added_by']
        
        # Handle file uploads
        pdf_file = request.files.get('pdf_file')
        image_file = request.files.get('image_file')
        
        if pdf_file and allowed_file(pdf_file.filename):
            pdf_filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))
        else:
            pdf_filename = None
        
        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = None
        
        new_material = Material(
            title=title,
            content=content,
            added_by=added_by,
            pdf_file=pdf_filename,
            image_file=image_filename
        )
        db.session.add(new_material)
        db.session.commit()
        flash('Material added successfully!')
        return redirect(url_for('admin'))
    return render_template('add_material.html')

@app.route('/delete_material/<int:material_id>')
def delete_material(material_id):
    material = Material.query.get_or_404(material_id)
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully!')
    return redirect(url_for('admin'))

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!')
    return redirect(url_for('admin'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
