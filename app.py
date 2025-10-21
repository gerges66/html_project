from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# إعدادات الداتابيز
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="facebook_clone"
    )

# الصفحة الرئيسية
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/home')
    return redirect('/login')

# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # الباسوورد كما هو
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # إدخال البيانات بدون أي hashing
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (name, email, password)
            )
            conn.commit()
            
            # عرض البيانات المدخلة
            print(f"✅ تم التسجيل: {name} | {email} | {password}")
            return f'''
            <h2>✅ تم إنشاء الحساب بنجاح!</h2>
            <p>الاسم: {name}</p>
            <p>الإيميل: {email}</p>
            <p style="color: red; font-weight: bold;">الباسوورد: {password}</p>
            <a href="/login">سجل الدخول</a>
            '''
            
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>تسجيل جديد</title>
        <style>
            body { font-family: Arial; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .box { background: white; padding: 30px; border-radius: 10px; width: 400px; text-align: center; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; }
            button { width: 100%; padding: 12px; background: #1877f2; color: white; border: none; border-radius: 6px; font-size: 16px; }
            h2 { color: #1877f2; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>فيسبوك</h2>
            <p>أنشئ حساب جديد</p>
            <form method="POST">
                <input type="text" name="name" placeholder="الاسم الكامل" required>
                <input type="email" name="email" placeholder="البريد الإلكتروني" required>
                <input type="text" name="password" placeholder="كلمة المرور" required>
                <button type="submit">إنشاء حساب جديد</button>
            </form>
            <p><a href="/login">هل لديك حساب بالفعل؟</a></p>
        </div>
    </body>
    </html>
    '''

# صفحة الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        print(f"🔐 محاولة دخول: {email} | {password}")
        if user:
            print(f"📊 الباسوورد في الداتابيز: {user['password']}")
        
        # مقارنة مباشرة - بدون hashing
        if user and password == user['password']:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect('/home')
        else:
            return '''
            <h2>❌ خطأ في الدخول</h2>
            <p>البريد الإلكتروني أو كلمة المرور غير صحيحة</p>
            <a href="/login">حاول مرة أخرى</a>
            '''
        
        cursor.close()
        conn.close()
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>تسجيل الدخول</title>
        <style>
            body { font-family: Arial; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .box { background: white; padding: 30px; border-radius: 10px; width: 400px; text-align: center; }
            input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; }
            button { width: 100%; padding: 12px; background: #1877f2; color: white; border: none; border-radius: 6px; font-size: 16px; }
            h2 { color: #1877f2; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>فيسبوك</h2>
            <form method="POST">
                <input type="email" name="email" placeholder="البريد الإلكتروني" required>
                <input type="text" name="password" placeholder="كلمة المرور" required>
                <button type="submit">تسجيل الدخول</button>
            </form>
            <p><a href="/register">إنشاء حساب جديد</a></p>
        </div>
    </body>
    </html>
    '''

# صفحة عرض كل المستخدمين
@app.route('/view_users')
def view_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>جميع المستخدمين</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background: #1877f2; color: white; }
            .password { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>جميع المستخدمين المسجلين</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>الاسم</th>
                <th>الإيميل</th>
                <th>الباسوورد</th>
            </tr>
    '''
    
    for user in users:
        html += f'''
            <tr>
                <td>{user['id']}</td>
                <td>{user['name']}</td>
                <td>{user['email']}</td>
                <td class="password">{user['password']}</td>
            </tr>
        '''
    
    html += '''
        </table>
        <br>
        <a href="/register">تسجيل جديد</a> | 
        <a href="/login">تسجيل الدخول</a>
    </body>
    </html>
    '''
    
    return html

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)