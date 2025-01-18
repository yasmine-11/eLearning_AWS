# eLearning_AWS

This project is about developing an eLearning Application, using the knowledge gained from the Advanced Web Development Module. Throughout this project, I have successfully designed a suitable database for the application that adheres to normalisation standards and worked on the server-side code/backend of the application, such as models, forms, views, URLs, WebSockets, consumers, signals..etc.
Moreover, I have also created appropriate templates and styled them accordingly and implemented a comprehensive testing regime through all separate applications in the project which covered server-side code(models, forms, views, serialization...etc.) and the API for users' data.


The application can be deployed in the following few simple steps:

- Unzip folder.
- Open in VScode or preferred software.
- Open terminal (WSL Ubuntu terminal).
- Create a virtual environment ‘python3 -m venv testenv’
- Activate the virtual environment ‘source testenv/bin/activate’
- Change the directory into the application ‘cd elearning_app’
- Install all necessary dependencies ‘pip3 install -r requirements.txt’
- Deploy by running ‘python3 manage.py runserver 127.0.0.1:8080’

The development environment:
- WSL (Windows Subsystem for Linux).
- Python Version: 3.10.12

Software used to develop the Web Application: 
- Visual Studio Code.

The location of the example data loading scripts:
- ‘elearning_app/core/management/commands/seed_users.py’
- ‘elearning_app/core/management/commands/seed_courses.py’

To run the Unit Tests, do the following: 
- Activate the virtual environment 
- Change the directory to the app (cd elearing_app) 
- Run this command to test users app: ‘python3 manage.py test users’
- Run this command to test courses app: ‘python3 manage.py test courses’
- Run this command to test communications app: ‘python3 manage.py test communications’
- Run this command to test api app: ‘python3 manage.py test api’
