# Flasker
An online blog template created using Flask from YouTube Tutorial series called "Create A Flask Blog - Flask Friday"
https://youtu.be/0Qxtt4veJIc

### Dependencies
- (apt) python3 
- (apt) grip
- (pip) flask
- (pip) flask-wtf
- (pip) flask-sqlalchemy
- (apt) mysql-server
- (pip) mysql-connector-python
- (pip) pymysql
- (pip) cryptography
- (pip) Flask-Migrate
- (pip) flask_login

### Setup
- python3 -m venv virt
- source virt/bin/activate
- deactivate (optional)
- pip install <dependencies>
- pip freeze (to view install python modules)
- export FLASK_DEBUG=True
- export FLASK_APP=hello.py
- flask run

### Daily Use
- source virt/bin/activate
- flask run
- grip (view README.md locally)

### Other Commands
- echo $FLASK_ENV
- unset FLASK_ENV
- flask shell