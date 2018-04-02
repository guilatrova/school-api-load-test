import os
from locust import HttpLocust
from tasks import StudentTaskSet, TeacherTaskSet

class BaseHttpLocust(HttpLocust):
    host = os.getenv('TARGET_URL', "http://localhost:8000")
    min_wait = 1000
    max_wait = 10000

class StudentUser(BaseHttpLocust):
    task_set = StudentTaskSet

class TeacherUser(BaseHttpLocust):
    task_set = TeacherTaskSet