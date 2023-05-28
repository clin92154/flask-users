from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 設定session的密鑰
app.templates_auto_reload = True 

# 建立資料庫連接
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('mydb.db')
        print(f'Successfully connected to the database')
        return conn
    except Error as e:
        print(f'Error connecting to the database: {e}')
    return conn

# 檢查使用者是否已登入
def check_login():
    if 'idno' in session:
        return True
    return False

# 登入頁面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        idno = request.form['idno']
        pwd = request.form['pwd']
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM member WHERE idno = ? AND pwd = ?', (idno, pwd))
        user = cursor.fetchone()
        
        if user:
            session['nm'] = user[1]  # 儲存登入使用者的名稱於session中
            session['idno'] = user[6]
            return redirect('/home')
        else:
            error = 'ID或密碼錯誤'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

# 首頁
@app.route('/home')
def home():
    if check_login():
        return render_template('home.html')
    else:
        return redirect('/')

# 修改個人資訊頁面
@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if check_login():
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM member WHERE nm = ?', (session['nm'],))
        user = cursor.fetchone()
        if request.method == 'POST':
            # 異動資料庫中的個人資訊
            nm = request.form['nm']
            birth = request.form['birth']
            blood = request.form['blood']
            phone = request.form['phone']
            email = request.form['email']
            session['nm'] = nm

            cursor.execute('UPDATE member SET nm = ?, birth = ?, blood = ?, phone = ?, email = ? WHERE idno = ?', (nm, birth, blood, phone, email, session['idno'],))
            conn.commit()
            
            return redirect('/home')
        
        return render_template('edit_profile.html', user=user)
    else:
        return redirect('/')

# 登出
@app.route('/logout')
def logout():
    session['nm'] = False
    session['idno'] = False
    return redirect('/')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80)
    session(app)
