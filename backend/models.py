"""
models.py - Database models and initialization for Course Evaluation System
Uses sqlite3 directly with a simple interface.
"""

import sqlite3
import os
from datetime import datetime

# 优先用环境变量，否则用当前工作目录
DATABASE_DIR = os.environ.get('DB_DIR', os.path.join(os.getcwd(), 'database'))
DATABASE_PATH = os.path.join(DATABASE_DIR, 'course_eval.db')


def get_db():
    """Get a database connection with row factory set to sqlite3.Row"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database tables and seed data"""
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    # Create tables
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
            display_name TEXT NOT NULL,
            email TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            teacher_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            UNIQUE(student_id, course_id)
        );

        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        );
    ''')

    # Check if data already exists
    existing = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Seed users (passwords generated via werkzeug)
    from werkzeug.security import generate_password_hash

    users = [
        ('admin', generate_password_hash('admin123'), 'admin', '系统管理员', 'admin@university.edu.cn'),
        ('admin2', generate_password_hash('admin123'), 'admin', '副管理员', 'admin2@university.edu.cn'),
        ('teacher1', generate_password_hash('123456'), 'teacher', '张教授', 'zhang@university.edu.cn'),
        ('teacher2', generate_password_hash('123456'), 'teacher', '李教授', 'li@university.edu.cn'),
        ('teacher3', generate_password_hash('123456'), 'teacher', '王教授', 'wang@university.edu.cn'),
        ('student1', generate_password_hash('123456'), 'student', '赵同学', 'student1@university.edu.cn'),
        ('student2', generate_password_hash('123456'), 'student', '钱同学', 'student2@university.edu.cn'),
        ('student3', generate_password_hash('123456'), 'student', '孙同学', 'student3@university.edu.cn'),
        ('student4', generate_password_hash('123456'), 'student', '周同学', 'student4@university.edu.cn'),
        ('student5', generate_password_hash('123456'), 'student', '吴同学', 'student5@university.edu.cn'),
    ]

    cursor.executemany(
        "INSERT INTO users (username, password_hash, role, display_name, email) VALUES (?, ?, ?, ?, ?)",
        users
    )

    courses = [
        ('高等数学A', '微积分与线性代数基础课程，涵盖极限、导数、积分及矩阵理论', 3),
        ('大学物理B', '力学、电磁学与热学基础知识', 4),
        ('程序设计基础', 'Python语言入门，包括基本语法、数据结构与算法', 5),
        ('数据结构与算法', '链表、树、图等核心数据结构及经典算法分析', 3),
        ('数据库原理', '关系型数据库理论、SQL语言及数据库设计范式', 4),
        ('计算机网络', 'TCP/IP协议栈、网络分层模型及网络安全基础', 5),
    ]

    cursor.executemany(
        "INSERT INTO courses (name, description, teacher_id) VALUES (?, ?, ?)",
        courses
    )

    # Enrollments: student1(6) in course 1,2,3; student2(7) in 2,3,4; student3(8) in 3,4,5; etc.
    enrollments = [
        (6, 1), (6, 2), (6, 3),
        (7, 2), (7, 3), (7, 4),
        (8, 3), (8, 4), (8, 5),
        (9, 4), (9, 5), (9, 6),
        (10, 5), (10, 6), (10, 1),
    ]

    cursor.executemany(
        "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
        enrollments
    )

    # Evaluations
    evaluations = [
        (6, 1, 5, '张教授讲得非常清晰，受益匪浅！'),
        (6, 2, 4, '实验课很有趣，理论部分稍难。'),
        (6, 3, 5, '王教授的Python课太棒了，动手实践很多。'),
        (7, 2, 3, '物理课内容还可以，但节奏有点快。'),
        (7, 3, 4, '编程课学到了很多实用技能。'),
        (7, 4, 4, '张教授的数据结构课很有深度。'),
        (8, 3, 5, '非常喜欢这门课，老师很耐心。'),
        (8, 4, 3, '算法部分比较难理解，希望有更多例题。'),
        (8, 5, 4, '李教授的数据库课讲得很系统。'),
        (9, 4, 5, '数据结构是我学得最好的一门课！'),
        (9, 5, 4, '数据库实验设计得很好。'),
        (9, 6, 4, '网络课内容丰富，老师讲解透彻。'),
        (10, 5, 3, '数据库理论部分有点枯燥。'),
        (10, 6, 5, '计算机网络是我最喜欢的课！'),
        (10, 1, 4, '数学课内容充实，作业量适中。'),
    ]

    cursor.executemany(
        "INSERT INTO evaluations (student_id, course_id, rating, comment) VALUES (?, ?, ?, ?)",
        evaluations
    )

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DATABASE_PATH}")


def query_to_dict(row):
    """Convert sqlite3.Row to dict"""
    if row is None:
        return None
    return dict(row)


def query_all(cursor):
    """Convert all rows to list of dicts"""
    return [dict(row) for row in cursor.fetchall()]
