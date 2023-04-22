# Databases

## sqlite3

### hello.py
```python
app.app_context().push()
```

### terminal
```bash
(virt)$ python3
>>> from hello import app
>>> from hello import db
>>> db.create_all()
```


## mysql
hello.py
```python
app.app_context().push()
```

### terminal
```bash
# Install MySQL Server
(virt)$ sudo apt-get install mysql-server
(virt)$ systemctl status mysql

# Create MySQL User & Password
(virt)$ sudo mysql --user=root mysql
mysql> CREATE USER 'db-admin'@'localhost' IDENTIFIED BY 'password';
mysql> GRANT ALL PRIVILEGES ON *.* TO 'db-admin'@'localhost';
mysql> FLUSH PRIVILEGES;
mysql> quit;
(virt)$ sudo systemctl restart mysql
(virt)$ python3 create_db.py

# Initialize MySQL Database for Flask usage
(virt)$ pip install pymysql
(virt)$ pip install cryptography
(virt)$ python3
>>> from hello import app
>>> from hello import db
>>> db.create_all()
>>> quit()

# Login as MySQL User
(virt)$ mysql -u db-user -p
```