"""
app.py - Flask main application for Course Evaluation System
"""

import os
import csv
import io

from flask import Flask, request, jsonify, session, send_from_directory, make_response
from backend.models import init_db, get_db, query_to_dict, query_all
from backend.auth import login_user, login_required, role_required, get_current_user

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'frontend'),
            static_url_path='')
app.secret_key = 'course-eval-secret-key-2024-change-in-production'

# ---------------------------------------------------------------------------
# Initialize DB on startup
# ---------------------------------------------------------------------------
with app.app_context():
    init_db()

# ---------------------------------------------------------------------------
# Frontend page serving
# ---------------------------------------------------------------------------

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/student.html')
@login_required
def serve_student():
    return send_from_directory(app.static_folder, 'student.html')

@app.route('/teacher.html')
@login_required
def serve_teacher():
    return send_from_directory(app.static_folder, 'teacher.html')

@app.route('/admin.html')
@login_required
def serve_admin():
    return send_from_directory(app.static_folder, 'admin.html')

# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    user = login_user(username, password)
    if user is None:
        return jsonify({'error': '用户名或密码错误'}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']
    session['display_name'] = user['display_name']

    return jsonify({
        'message': '登录成功',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'display_name': user['display_name'],
            'email': user['email']
        },
        'redirect': f'/{user["role"]}.html'
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': '已退出登录'})

@app.route('/api/me', methods=['GET'])
@login_required
def api_me():
    user = get_current_user()
    if user is None:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'display_name': user['display_name'],
        'email': user['email']
    })

# ---------------------------------------------------------------------------
# Student APIs
# ---------------------------------------------------------------------------

@app.route('/api/courses', methods=['GET'])
@login_required
def api_courses():
    """List all courses. For students, include enrollment and evaluation status."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.*, u.display_name as teacher_name
        FROM courses c
        JOIN users u ON c.teacher_id = u.id
        ORDER BY c.id
    ''')
    courses = query_all(cursor)

    user_id = session['user_id']
    user_role = session['role']

    for course in courses:
        # Check enrollment
        cursor.execute(
            "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
            (user_id, course['id'])
        )
        course['enrolled'] = cursor.fetchone() is not None

        # Check if already evaluated
        cursor.execute(
            "SELECT id, rating, comment, created_at FROM evaluations WHERE student_id = ? AND course_id = ?",
            (user_id, course['id'])
        )
        eval_row = cursor.fetchone()
        course['evaluated'] = eval_row is not None
        course['my_evaluation'] = dict(eval_row) if eval_row else None

    conn.close()
    return jsonify(courses)


@app.route('/api/enroll/<int:course_id>', methods=['POST'])
@login_required
@role_required('student')
def api_enroll(course_id):
    """Enroll in a course."""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Check course exists
    cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': '课程不存在'}), 404

    # Check already enrolled
    cursor.execute(
        "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
        (user_id, course_id)
    )
    if cursor.fetchone() is not None:
        conn.close()
        return jsonify({'error': '已选过该课程'}), 400

    cursor.execute(
        "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
        (user_id, course_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': '选课成功'})


@app.route('/api/evaluate/<int:course_id>', methods=['POST'])
@login_required
@role_required('student')
def api_evaluate(course_id):
    """Submit an evaluation for a course."""
    data = request.get_json() or {}
    rating = data.get('rating')
    comment = data.get('comment', '').strip()

    if rating is None or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': '评分必须为1-5的整数'}), 400

    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    # Check enrolled
    cursor.execute(
        "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
        (user_id, course_id)
    )
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': '请先选课再进行评价'}), 400

    # Check not already evaluated
    cursor.execute(
        "SELECT id FROM evaluations WHERE student_id = ? AND course_id = ?",
        (user_id, course_id)
    )
    if cursor.fetchone() is not None:
        conn.close()
        return jsonify({'error': '已经评价过该课程'}), 400

    cursor.execute(
        "INSERT INTO evaluations (student_id, course_id, rating, comment) VALUES (?, ?, ?, ?)",
        (user_id, course_id, rating, comment)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': '评价提交成功'})


@app.route('/api/my-enrollments', methods=['GET'])
@login_required
@role_required('student')
def api_my_enrollments():
    """Get student's enrolled courses."""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.*, u.display_name as teacher_name, e.enrolled_at,
               (SELECT ev.id FROM evaluations ev WHERE ev.student_id = ? AND ev.course_id = c.id) as evaluation_done
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        JOIN users u ON c.teacher_id = u.id
        WHERE e.student_id = ?
        ORDER BY e.enrolled_at DESC
    ''', (user_id, user_id))

    enrollments = query_all(cursor)
    conn.close()

    for item in enrollments:
        item['evaluated'] = item['evaluation_done'] is not None

    return jsonify(enrollments)


@app.route('/api/my-evaluations', methods=['GET'])
@login_required
@role_required('student')
def api_my_evaluations():
    """Get student's evaluation history."""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT ev.*, c.name as course_name, c.description as course_description,
               u.display_name as teacher_name
        FROM evaluations ev
        JOIN courses c ON ev.course_id = c.id
        JOIN users u ON c.teacher_id = u.id
        WHERE ev.student_id = ?
        ORDER BY ev.created_at DESC
    ''', (user_id,))

    evaluations = query_all(cursor)
    conn.close()
    return jsonify(evaluations)


# ---------------------------------------------------------------------------
# Teacher APIs
# ---------------------------------------------------------------------------

@app.route('/api/my-courses', methods=['GET'])
@login_required
@role_required('teacher')
def api_my_courses():
    """Get courses taught by this teacher with evaluation stats."""
    user_id = session['user_id']
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.*,
               COUNT(DISTINCT e.student_id) as enrollment_count,
               COUNT(ev.id) as evaluation_count,
               ROUND(AVG(ev.rating), 1) as avg_rating
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        LEFT JOIN evaluations ev ON c.id = ev.course_id
        WHERE c.teacher_id = ?
        GROUP BY c.id
        ORDER BY c.id
    ''', (user_id,))

    courses = query_all(cursor)
    conn.close()
    return jsonify(courses)


@app.route('/api/course/<int:course_id>/stats', methods=['GET'])
@login_required
@role_required('teacher', 'admin')
def api_course_stats(course_id):
    """Get detailed evaluation statistics for a course."""
    conn = get_db()
    cursor = conn.cursor()

    # Verify ownership for teachers
    if session['role'] == 'teacher':
        cursor.execute("SELECT teacher_id FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if course is None:
            conn.close()
            return jsonify({'error': '课程不存在'}), 404
        if course['teacher_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': '您不是该课程的授课教师'}), 403

    # Stats
    cursor.execute('''
        SELECT
            COUNT(*) as total_evaluations,
            ROUND(AVG(rating), 1) as avg_rating,
            SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as r1,
            SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as r2,
            SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as r3,
            SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as r4,
            SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as r5
        FROM evaluations
        WHERE course_id = ?
    ''', (course_id,))

    stats = query_to_dict(cursor.fetchone())
    conn.close()
    return jsonify(stats)


@app.route('/api/course/<int:course_id>/evaluations', methods=['GET'])
@login_required
@role_required('teacher', 'admin')
def api_course_evaluations(course_id):
    """Get detailed evaluation list for a course."""
    conn = get_db()
    cursor = conn.cursor()

    # Verify ownership for teachers
    if session['role'] == 'teacher':
        cursor.execute("SELECT teacher_id FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if course is None:
            conn.close()
            return jsonify({'error': '课程不存在'}), 404
        if course['teacher_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': '您不是该课程的授课教师'}), 403

    cursor.execute('''
        SELECT ev.*, u.display_name as student_name, u.username as student_username
        FROM evaluations ev
        JOIN users u ON ev.student_id = u.id
        WHERE ev.course_id = ?
        ORDER BY ev.created_at DESC
    ''', (course_id,))

    evaluations = query_all(cursor)
    conn.close()
    return jsonify(evaluations)


@app.route('/api/course/<int:course_id>/export', methods=['GET'])
@login_required
@role_required('teacher', 'admin')
def api_course_export(course_id):
    """Export course evaluations as CSV."""
    conn = get_db()
    cursor = conn.cursor()

    # Verify ownership for teachers
    if session['role'] == 'teacher':
        cursor.execute("SELECT teacher_id, name FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if course is None:
            conn.close()
            return jsonify({'error': '课程不存在'}), 404
        if course['teacher_id'] != session['user_id']:
            conn.close()
            return jsonify({'error': '您不是该课程的授课教师'}), 403
        course_name = course['name']
    else:
        cursor.execute("SELECT name FROM courses WHERE id = ?", (course_id,))
        course = cursor.fetchone()
        if course is None:
            conn.close()
            return jsonify({'error': '课程不存在'}), 404
        course_name = course['name']

    cursor.execute('''
        SELECT ev.rating, ev.comment, ev.created_at,
               u.display_name as student_name, u.username as student_username
        FROM evaluations ev
        JOIN users u ON ev.student_id = u.id
        WHERE ev.course_id = ?
        ORDER BY ev.created_at DESC
    ''', (course_id,))

    evaluations = query_all(cursor)
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['学生姓名', '学号', '评分(1-5)', '评语', '评价时间'])
    for ev in evaluations:
        writer.writerow([
            ev['student_name'],
            ev['student_username'],
            ev['rating'],
            ev['comment'],
            ev['created_at']
        ])

    csv_content = output.getvalue()
    output.close()

    safe_name = course_name.replace(' ', '_')
    response = make_response(csv_content)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    response.headers['Content-Disposition'] = f'attachment; filename={safe_name}_评价数据.csv'
    return response


# ---------------------------------------------------------------------------
# Admin APIs
# ---------------------------------------------------------------------------

@app.route('/api/admin/courses', methods=['GET'])
@login_required
@role_required('admin')
def api_admin_courses():
    """Admin: get all courses with full details."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.*, u.display_name as teacher_name,
               COUNT(DISTINCT e.student_id) as enrollment_count,
               COUNT(ev.id) as evaluation_count,
               ROUND(AVG(ev.rating), 1) as avg_rating
        FROM courses c
        JOIN users u ON c.teacher_id = u.id
        LEFT JOIN enrollments e ON c.id = e.course_id
        LEFT JOIN evaluations ev ON c.id = ev.course_id
        GROUP BY c.id
        ORDER BY c.id
    ''')

    courses = query_all(cursor)
    conn.close()
    return jsonify(courses)


@app.route('/api/admin/courses', methods=['POST'])
@login_required
@role_required('admin')
def api_admin_add_course():
    """Admin: add a new course."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    teacher_id = data.get('teacher_id')

    if not name:
        return jsonify({'error': '课程名称不能为空'}), 400
    if not teacher_id:
        return jsonify({'error': '请选择授课教师'}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Verify teacher exists
    cursor.execute("SELECT id FROM users WHERE id = ? AND role = 'teacher'", (teacher_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': '教师不存在'}), 400

    cursor.execute(
        "INSERT INTO courses (name, description, teacher_id) VALUES (?, ?, ?)",
        (name, description, teacher_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': '课程添加成功'}), 201


@app.route('/api/admin/courses/<int:course_id>', methods=['PUT'])
@login_required
@role_required('admin')
def api_admin_edit_course(course_id):
    """Admin: edit a course."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    teacher_id = data.get('teacher_id')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': '课程不存在'}), 404

    if teacher_id:
        cursor.execute("SELECT id FROM users WHERE id = ? AND role = 'teacher'", (teacher_id,))
        if cursor.fetchone() is None:
            conn.close()
            return jsonify({'error': '教师不存在'}), 400

    updates = []
    params = []
    if name:
        updates.append("name = ?")
        params.append(name)
    if description or 'description' in data:
        updates.append("description = ?")
        params.append(description)
    if teacher_id:
        updates.append("teacher_id = ?")
        params.append(teacher_id)

    if updates:
        params.append(course_id)
        cursor.execute(f"UPDATE courses SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    conn.close()
    return jsonify({'message': '课程更新成功'})


@app.route('/api/admin/courses/<int:course_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def api_admin_delete_course(course_id):
    """Admin: delete a course and its related data."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM courses WHERE id = ?", (course_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': '课程不存在'}), 404

    cursor.execute("DELETE FROM evaluations WHERE course_id = ?", (course_id,))
    cursor.execute("DELETE FROM enrollments WHERE course_id = ?", (course_id,))
    cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '课程已删除'})


@app.route('/api/admin/users', methods=['GET'])
@login_required
@role_required('admin')
def api_admin_users():
    """Admin: get all users."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, username, role, display_name, email, created_at
        FROM users
        ORDER BY
            CASE role
                WHEN 'admin' THEN 1
                WHEN 'teacher' THEN 2
                WHEN 'student' THEN 3
            END,
            id
    ''')

    users = query_all(cursor)
    conn.close()
    return jsonify(users)


@app.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
@login_required
@role_required('admin')
def api_admin_change_role(user_id):
    """Admin: change a user's role."""
    data = request.get_json() or {}
    new_role = data.get('role')

    if new_role not in ('student', 'teacher', 'admin'):
        return jsonify({'error': '无效的角色'}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': '用户不存在'}), 404

    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()
    return jsonify({'message': '角色更新成功'})


@app.route('/api/admin/teachers', methods=['GET'])
@login_required
@role_required('admin')
def api_admin_teachers():
    """Admin: get list of teachers for course assignment dropdown."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, display_name FROM users WHERE role = 'teacher' ORDER BY id"
    )
    teachers = query_all(cursor)
    conn.close()
    return jsonify(teachers)


@app.route('/api/admin/dashboard', methods=['GET'])
@login_required
@role_required('admin')
def api_admin_dashboard():
    """Admin: get dashboard statistics."""
    conn = get_db()
    cursor = conn.cursor()

    # Course ranking by average rating
    cursor.execute('''
        SELECT c.name, ROUND(AVG(ev.rating), 1) as avg_rating, COUNT(ev.id) as count
        FROM courses c
        LEFT JOIN evaluations ev ON c.id = ev.course_id
        GROUP BY c.id
        ORDER BY avg_rating DESC, count DESC
    ''')
    course_ranking = query_all(cursor)

    # Rating distribution (overall)
    cursor.execute('''
        SELECT rating, COUNT(*) as count
        FROM evaluations
        GROUP BY rating
        ORDER BY rating
    ''')
    rating_distribution = query_all(cursor)

    # Evaluation count trend (by date, last 30 days)
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM evaluations
        WHERE created_at >= DATE('now', '-30 days')
        GROUP BY DATE(created_at)
        ORDER BY date
    ''')
    evaluation_trend = query_all(cursor)

    # Summary counts
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    student_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'")
    teacher_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM courses")
    course_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM evaluations")
    eval_count = cursor.fetchone()[0]
    cursor.execute("SELECT ROUND(AVG(rating), 1) FROM evaluations")
    overall_avg = cursor.fetchone()[0] or 0

    conn.close()

    return jsonify({
        'summary': {
            'student_count': student_count,
            'teacher_count': teacher_count,
            'course_count': course_count,
            'evaluation_count': eval_count,
            'overall_avg_rating': overall_avg
        },
        'course_ranking': course_ranking,
        'rating_distribution': rating_distribution,
        'evaluation_trend': evaluation_trend
    })


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
