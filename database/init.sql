-- Course Evaluation System - Database Initialization
-- This script is for reference; the actual tables are created by models.py

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

-- Sample admin users (password: admin123)
INSERT OR IGNORE INTO users (username, password_hash, role, display_name, email) VALUES
('admin', 'scrypt:32768:8:1$Z0HLOg0kQzYjPqgN$8d2c9a1cf7a3a2a2e769ee0e4e3d8e5260b7e7c8b65f0545a3a540e038432d5108faeab45eaa84a2fa1c95211fe2ebe', 'admin', '系统管理员', 'admin@university.edu.cn'),
('admin2', 'scrypt:32768:8:1$Z0HLOg0kQzYjPqgN$8d2c9a1cf7a3a2a2e769ee0e4e3d8e5260b7e7c8b65f0545a3a540e038432d5108faeab45eaa84a2fa1c95211fe2ebe', 'admin', '副管理员', 'admin2@university.edu.cn');

-- Sample teachers (password: 123456)
INSERT OR IGNORE INTO users (username, password_hash, role, display_name, email) VALUES
('teacher1', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'teacher', '张教授', 'zhang@university.edu.cn'),
('teacher2', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'teacher', '李教授', 'li@university.edu.cn'),
('teacher3', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'teacher', '王教授', 'wang@university.edu.cn');

-- Sample students (password: 123456)
INSERT OR IGNORE INTO users (username, password_hash, role, display_name, email) VALUES
('student1', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'student', '赵同学', 'student1@university.edu.cn'),
('student2', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'student', '钱同学', 'student2@university.edu.cn'),
('student3', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'student', '孙同学', 'student3@university.edu.cn'),
('student4', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'student', '周同学', 'student4@university.edu.cn'),
('student5', 'scrypt:32768:8:1$okmC1SiqYRynhYt7$645740a401a15d0484e5a63b96c743914391bbf3b25e59cd801bde1c5b98aeea40e128e41cfdda1813083d03cfc9d6fe', 'student', '吴同学', 'student5@university.edu.cn');

-- Sample courses (teacher IDs: 3,4,5)
INSERT OR IGNORE INTO courses (id, name, description, teacher_id) VALUES
(1, '高等数学A', '微积分与线性代数基础课程，涵盖极限、导数、积分及矩阵理论', 3),
(2, '大学物理B', '力学、电磁学与热学基础知识', 4),
(3, '程序设计基础', 'Python语言入门，包括基本语法、数据结构与算法', 5),
(4, '数据结构与算法', '链表、树、图等核心数据结构及经典算法分析', 3),
(5, '数据库原理', '关系型数据库理论、SQL语言及数据库设计范式', 4),
(6, '计算机网络', 'TCP/IP协议栈、网络分层模型及网络安全基础', 5);
