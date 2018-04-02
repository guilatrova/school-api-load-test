import time
from locust import TaskSet, task
from factories import create_questions

class OnStartSetupDataMixin:
    def post_json_get_id(self, url, payload):
        response = self.client.post(url, json=payload)
        time.sleep(0.1) #Required to avoid connection error
        return response.json()['id']

    def setup_people(self):        
        self.student = self.post_json_get_id("/students/", { 'name': 'Guilherme' })
        self.new_comer = self.post_json_get_id("/students/", { 'name': 'Bill Gates' })
        self.waiting_assignment = self.post_json_get_id("/students/", { 'name': 'Steve Wozniak' })

        self.teacher = self.post_json_get_id("/teachers/", { 'name': 'Kwan' })

    def setup_classes(self):
        self.school_class = self.post_json_get_id("/classes/", { 'name': 'Load Testing', 'teacher': self.teacher })
        self.student_enrollment = self.post_json_get_id("/students/{}/classes/".format(self.student), { 'student': self.student, 'school_class': self.school_class, 'semester': '2018-01-01' })
        self.waiting_assignment_enrollment = self.post_json_get_id("/students/{}/classes/".format(self.student), { 'student': self.waiting_assignment, 'school_class': self.school_class, 'semester': '2018-01-01' })

    def setup_quizzes_and_assignments(self):
        self.quiz = self.post_json_get_id("/quizzes/", { 'school_class': self.school_class, 'questions': create_questions(10) })
        self.assignment = self.post_json_get_id("/students/{}/assignments/".format(self.student), { 'quiz': self.quiz, 'enrollment': self.student_enrollment })

    def on_start(self):
        self.setup_people()
        self.setup_classes()
        self.setup_quizzes_and_assignments()

class TeacherTaskSet(OnStartSetupDataMixin, TaskSet):
    @task
    def create_teacher(self):
        self.client.post("/teachers/", json={ 'name': 'Mary' })

    @task
    def create_class(self):
        self.client.post("/classes/", json={ 'name': 'Managing Great Companies', 'teacher': self.teacher })    

    @task
    def create_quiz(self):
        questions = create_questions(5)
        self.client.post("/quizzes/", json={ 'school_class': self.school_class, 'questions': questions })

    @task
    def assign_quiz_to_student(self):
        self.client.post("/students/{}/assignments/".format(self.waiting_assignment), json={ 'quiz': self.quiz, 'enrollment': self.waiting_assignment_enrollment })

    @task 
    def check_assignment_status(self):
        self.client.get("/assignments/{}".format(str(self.assignment)))

    @task
    def check_students_grades(self):        
        self.client.get("/assignments/reports/student-grades/?teacher={}&semester=2018-01-01".format(self.teacher))        

class StudentTaskSet(OnStartSetupDataMixin, TaskSet):
    @task
    def create_student(self):
        self.client.post("/students/", json={ 'name': 'Jhon' })

    @task
    def check_classes(self):
        self.client.get("/students/{}/classes/".format(self.student))

    @task
    def check_assignments(self):
        self.client.get("/students/{}/assignments/".format(self.student))

    @task
    def enroll_in_class(self):
        data = { 'student': self.new_comer, 'school_class': self.school_class, 'semester': '2018-01-01' }
        self.client.post("/students/{}/classes/".format(self.new_comer), json=data)

    @task
    def check_assignment_result(self):
        self.client.get("/assignments/{}/".format(str(self.assignment)))
