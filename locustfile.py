# Copyright 2015-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.

import os
import time
import string
import random
from locust import HttpLocust, TaskSet, task

def create_questions(how_many):
    answers = create_answers('A', 'B', 'C', 'D')
    return [create_question(answers) for x in range(how_many)]

def create_question(answers):
    return {
        'description': 'question',
        'correct_answer': 1,
        'answers': answers
    }

def create_answers(*args):
    lst = []
    for i in range(len(args)):
        description = args[i]
        choice = i + 1
        lst.append({ 'choice': choice, 'description': description })

    return lst

class MyTaskSet(TaskSet):
    def post_json_get_id(self, url, payload):
        response = self.client.post(url, json=payload)
        time.sleep(0.2) #Required to avoid connection error
        return response.json()['id']

    def setup_people(self):        
        self.student = self.post_json_get_id("/students/", { 'name': 'Guilherme' })
        self.teacher = self.post_json_get_id("/teachers/", { 'name': 'Kwan' })

        self.new_comer = self.post_json_get_id("/students/", { 'name': 'Jhonny' })

    def setup_classes(self):
        self.school_class = self.post_json_get_id("/classes/", { 'name': 'Load Testing', 'teacher': self.teacher })
        self.student_enrollment = self.post_json_get_id("/students/{}/classes/".format(self.student), { 'student': self.student, 'school_class': self.school_class, 'semester': '2018-01-01' })

    def setup_quizzes_and_assignments(self):
        self.quiz = self.post_json_get_id("/quizzes/", { 'school_class': self.school_class, 'questions': create_questions(10) })
        self.assignment = self.post_json_get_id("/students/{}/assignments/".format(self.student), { 'quiz': self.quiz, 'enrollment': self.student_enrollment })

    def on_start(self):
        self.setup_people()
        self.setup_classes()
        self.setup_quizzes_and_assignments()

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

    # @task
    # def assign_quiz_to_student(self):
    #     self.client.post("/assignments/", json={ 'quiz': self.quiz, 'enrollment': self.student_enrollment })

    @task 
    def check_assignment_status(self):
        self.client.get("/assignments/{}".format(str(self.assignment)))

    @task
    def check_students_grades(self):        
        self.client.get("/assignments/reports/student-grades/?teacher={}&semester=2018-01-01".format(self.teacher))
        
    #Student
    @task
    def create_student(self):
        self.client.post("/students/", json={ 'name': 'Jhon' })

    @task
    def check_classes(self):
        pass

    @task
    def check_assignments(self):
        pass

    @task
    def enroll_in_class(self):
        self.client.post("/students/{}/classes/".format(self.new_comer), json={ 'school_class': self.school_class, 'semester': '2018-01-01' })

    @task
    def submits_answer(self):
        pass

    @task
    def check_assignment_result(self):
        pass
    

class MyLocust(HttpLocust):
    host = os.getenv('TARGET_URL', "http://localhost:8000")
    task_set = MyTaskSet
    min_wait = 1000
    max_wait = 10000
