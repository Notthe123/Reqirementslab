# A simple Flask application to manage student records with a RESTful API
from flask import Flask , render_template , request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api , Resource, abort

# Initialize the Flask application and configure the database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
db = SQLAlchemy(app)
api = Api(app)

# Define the Student model
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    grade = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Student name:{self.name}, student_id:{self.student_id}, course:{self.course}, grade:{self.grade}>"

 # Create the database tables   
with app.app_context():
    db.create_all()

# Define the function to validate student grades
def validate_grade(grade):
    try:
        grade = float(grade)
    except ValueError:
        abort(400, message="Grade must be a number")
    if grade < 0 or grade > 100:
        abort(400, message="Grade must be between 0 and 100")
    return grade
    
#api endpoints and resources
class StudentResource(Resource):

    # Get student information by student_id
    def get(self, student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            abort(404, message="Student not found")
        return {
            'student_id': student.student_id,
            'name': student.name,
            'course': student.course,
            'grade': student.grade
        }
    

class Students(Resource):
    # Create a new student record
    def post(self, student_id):
        data = request.get_json()
        if Student.query.filter_by(student_id=student_id).first():
            abort(400, message="Student with this ID already exists")
        name = data.get('name')
        course = data.get('course')
        grade = validate_grade(data.get('grade'))
        new_student = Student(student_id=student_id, name=name, course=course, grade=grade)
        db.session.add(new_student)
        db.session.commit()
        return {'message': 'Student created successfully'}, 201


    # Update student information
    def put(self, student_id):
        data = request.get_json()
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            abort(404, message="Student not found")
        student.name = data.get('name', student.name)
        student.course = data.get('course', student.course)
        if 'grade' in data:
            student.grade = validate_grade(data['grade'])
        db.session.commit()
        return {'message': 'Student updated successfully'}

    # Delete a student record
    def delete(self, student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            abort(404, message="Student not found")
        db.session.delete(student)
        db.session.commit()
        return {'message': 'Student deleted successfully'}
    

# Add the StudentResource to the API with the endpoint /students/<student_id>
api.add_resource(Students, '/students/<string:student_id>')
api.add_resource(StudentResource, '/students/<string:student_id>')

@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)

if __name__ == '__main__':
    app.run(debug=True)