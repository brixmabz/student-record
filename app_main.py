from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__)


class Student(object):
    def __init__(self, idnum, Fname, Mname, Lname, Sex, Course, Year):
        self.idno = idnum
        self.fname = Fname
        self.mname = Mname
        self.lname = Lname
        self.sex = Sex
        self.course = Course
        self.year = Year


conn = sql.connect('database.db')
conn. execute('CREATE TABLE IF NOT EXISTS studentCourses(COURSE_ID TEXT PRIMARY KEY, DESCRIPTION TEXT, COLLEGE TEXT)')
cur = conn.cursor()
cur.execute("INSERT OR IGNORE INTO studentCourses(COURSE_ID, DESCRIPTION, COLLEGE) VALUES ('BSCS', 'Bachelor of Science in Computer Science', 'SCS')")
cur.execute("INSERT OR IGNORE INTO studentCourses(COURSE_ID, DESCRIPTION, COLLEGE) VALUES ('BSIT', 'Bachelor of Science in Information Technology', 'SCS')")
cur.execute("INSERT OR IGNORE INTO studentCourses(COURSE_ID, DESCRIPTION, COLLEGE) VALUES ('BSECT', 'Bachelor of Science in Electronics and Computer Technology', 'SCS')")
cur.execute("INSERT OR IGNORE INTO studentCourses(COURSE_ID, DESCRIPTION, COLLEGE) VALUES ('ECET', 'Electronics Engineering Technology', 'SCS')")

conn.execute('CREATE TABLE IF NOT EXISTS studentRecord(ID TEXT PRIMARY KEY NOT NULL CHECK (length(ID)=9), FIRST_NAME TEXT CHECK (length(FIRST_NAME)>0), MID_NAME TEXT CHECK (length(MID_NAME)>0), LAST_NAME TEXT CHECK (length(LAST_NAME)>0), SEX TEXT CHECK (length(SEX)=1), COURSE TEXT CHECK (length(COURSE)>0), YEAR_LEVEL INTEGER CHECK (length(YEAR_LEVEL)=1))')


conn.execute("CREATE VIEW IF NOT EXISTS courseRecord AS SELECT COURSE_ID, LAST_NAME, FIRST_NAME, DESCRIPTION, COLLEGE, YEAR_LEVEL FROM studentRecord CROSS JOIN studentCourses WHERE studentCourses.COURSE_ID = studentRecord.COURSE")
conn.execute("CREATE VIEW IF NOT EXISTS infoComplete AS SELECT  ID, COURSE_ID, DESCRIPTION, COLLEGE, LAST_NAME, FIRST_NAME, MID_NAME, SEX, YEAR_LEVEL FROM studentRecord CROSS JOIN studentCourses WHERE studentCourses.COURSE_ID = studentRecord.COURSE")
conn.close()


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/add')
def add():
    return render_template('studentAdd.html')


@app.route('/addstudent', methods=['POST', 'GET'])
def addstudent():
    if request.method == "POST":
        try:
            idnumber = request.form['id_number']
            first_name = request.form['firstname']
            middle_name = request.form['middlename']
            last_name = request.form['lastname']
            sex = request.form['sex']
            course = request.form['course']
            year = request.form['year']

            stud = Student(idnumber, first_name, middle_name, last_name, sex, course, year)

            with sql.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO studentRecord(ID,FIRST_NAME,MID_NAME,LAST_NAME,SEX,COURSE,YEAR_LEVEL) VALUES(?,?,?,?,?,?,?)",
                            (stud.idno, stud.fname, stud.mname, stud.lname, stud.sex, stud.course, stud.year))
                con.commit()
                msg = "STUDENT ADDED SUCCESSFULLY"
        except:
            con.rollback()
            msg = "ERROR ADDING STUDENT. INSTRUCTIONS MIGHT'VE NOT BEEN FOLLOWED CORRECTLY OR ID NUMBER ALREADY EXISTS"
        finally:
            return render_template('result.html', msg=msg)
            con.close()



@app.route('/delete')
def delete():
    con = sql.connect('database.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM studentRecord")
    rows = cur.fetchall()
    return render_template('studentDelete.html', rows=rows)


@app.route('/deletestudent', methods=['POST', 'GET'])
def deletestudent():
    if request.method == "POST":
        try:
            idnumber = request.form['id_number']

            with sql.connect('database.db') as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM studentRecord')
                for row in cur.fetchall():
                    if row[0] == idnumber:
                        cur.execute('DELETE FROM studentRecord WHERE ID = ?', (idnumber,))
                        con.commit()
                        msg = "SUCCESSFULLY DELETED"
                        break
                    else:
                        msg = "STUDENT COULD NOT BE FOUND"
        except:
            msg = "DELETION FAILURE"
        finally:
            return render_template('result.html', msg=msg)


@app.route('/printtable')
def printtable():
    con = sql.connect('database.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('SELECT * FROM studentRecord')

    rows = cur.fetchall()
    return render_template('printtable.html', rows=rows)

@app.route('/studentcoursetable')
def studentcoursetable():
    con = sql.connect('database.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM courseRecord")
    rows = cur.fetchall()
    return render_template('courseTable.html', rows=rows)


@app.route('/update')
def update():
    con = sql.connect('database.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("SELECT * FROM studentRecord")
    rows = cur.fetchall()
    return render_template('studentUpdateCheck.html', rows=rows)


@app.route('/updatestudentcheck', methods=['POST', 'GET'])
def updatestudentcheck():
    if request.method == "POST":
        try:
            idnumber = request.form['id_number']
            with sql.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM studentRecord")
                for row in cur.fetchall():
                    if row[0] == idnumber:
                        find = row
                        check = 1
                        msg = "FOUND"
                        break
                    else:
                        msg = "ID NUMBER NOT FOUND"
                        check = 0
                        find = ""

        except:
            find = ""
            msg = "AN ERROR OCCURRED"
            check = 0
        finally:
            con.close()
            return render_template('studentUpdateCheckResult.html', check=check, msg=msg, find=find)


@app.route('/updatecheckresult', methods=['POST', 'GET'])
def updatecheckresult():
    if request.method == "POST":
        try:
            checks = request.form['checker']
            if checks == "YES":
                result = 1
                msg = "IT WORKED"
            elif checks == "NO":
                result = 0
            else:
                msg = "DAMN"
        except:
            msg = "ERROR"
        finally:
            if result == 1:
                return render_template('studentUpdate.html')
            else:
                return render_template('home.html')


@app.route('/updatestudent', methods=['POST', 'GET'])
def updatestudent():
    if request.method == "POST":
        try:
            idnumber = request.form['id_number']
            first_name = request.form['firstname']
            middle_name = request.form['middlename']
            last_name = request.form['lastname']
            sex = request.form['sex']
            course = request.form['course']
            year = request.form['year']

            with sql.connect('database.db') as con:
                cur = con.cursor()
                cur.execute('SELECT * FROM studentRecord')
                for row in cur.fetchall():
                    if row[0] == idnumber:
                        cur.execute('UPDATE studentRecord SET FIRST_NAME = ?, MID_NAME = ?, LAST_NAME = ?, SEX = ?, COURSE = ?, YEAR_LEVEL = ? WHERE ID = ?',
                                    (first_name, middle_name, last_name, sex, course, year, idnumber))
                        con.commit()
                        msg = "STUDENT UPDATED SUCCESSFULLY"
                        break
                    elif not row[0] == idnumber:
                        msg = "THIS STUDENT CANT BE UPDATED"
        except:
            msg = "ERROR"
        finally:
            con.close()
            return render_template('result.html', msg=msg)


@app.route('/search')
def search():
    return render_template('studentSearch.html')

@app.route('/studentsearch', methods=['POST', 'GET'])
def studentsearch():
    if request.method == "POST":
        try:
            searchinfo = request.form['info']

            conn = sql.connect('database.db')
            cur = conn.cursor()
            cur.execute("SELECT * FROM infoComplete where ID = ? or COURSE_ID = ? or COLLEGE = ? or DESCRIPTION = ? or FIRST_NAME = ? or MID_NAME = ? or LAST_NAME = ? or SEX = ? or YEAR_LEVEL = ?",
                        (searchinfo, searchinfo, searchinfo, searchinfo, searchinfo, searchinfo, searchinfo, searchinfo, searchinfo))
            print "1"
            coffee = cur.fetchall()
            msg = "existed"
            '''for row in cur.fetchall():
    #coffee = row
    print coffee
    msg = "existed"'''

        except:
            msg = "error"
        finally:
            print coffee
            print " copied"
            print "the message: " + msg
            return render_template("studentSearchResult.html", msg=msg, coffee=coffee)


if __name__ == '__main__':
    app.run(debug=True)
