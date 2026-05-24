# 课程评价系统 (Course Evaluation System)

基于 Python Flask + SQLite 的课程评价 Web 应用。

## 功能概览

### 学生端
- 浏览可选课程并选课
- 对已选课程进行 1-5 星评分并撰写评语
- 查看评价历史与已选课程

### 教师端
- 查看所授课程的评价统计（平均分、评分分布图）
- 查看学生详细评价列表
- 导出评价数据为 CSV 文件

### 管理员端
- 课程管理：添加、编辑、删除课程，分配授课教师
- 用户管理：查看用户列表，修改用户角色
- 数据仪表板：ECharts 可视化（课程平均分排名柱状图、评分分布饼图、评价趋势折线图）

## 技术栈

- **后端**：Python 3 + Flask
- **数据库**：SQLite（sqlite3）
- **前端**：纯 HTML + CSS + JS + ECharts CDN
- **认证**：基于 Flask Session

## 快速开始

### 1. 安装依赖

```bash
cd course-evaluation-system
pip install -r requirements.txt
```

### 2. 启动服务

```bash
cd backend
python app.py
```

服务默认运行在 `http://localhost:5000`。

### 3. 登录系统

打开浏览器访问 `http://localhost:5000`，使用以下账号登录：

| 角色   | 用户名    | 密码      |
|--------|-----------|-----------|
| 管理员 | admin     | admin123  |
| 管理员 | admin2    | admin123  |
| 教师   | teacher1  | 123456    |
| 教师   | teacher2  | 123456    |
| 教师   | teacher3  | 123456    |
| 学生   | student1  | 123456    |
| 学生   | student2  | 123456    |
| 学生   | student3  | 123456    |
| 学生   | student4  | 123456    |
| 学生   | student5  | 123456    |

## 目录结构

```
course-evaluation-system/
├── backend/
│   ├── app.py          # Flask 主程序，路由与 API 定义
│   ├── models.py       # 数据库模型与初始化（含示例数据）
│   └── auth.py         # 认证与权限控制
├── frontend/
│   ├── index.html      # 登录页
│   ├── student.html    # 学生端界面
│   ├── teacher.html    # 教师端界面
│   └── admin.html      # 管理员端界面
├── database/
│   └── init.sql        # 数据库初始化 SQL（参考用）
├── requirements.txt    # Python 依赖
└── README.md           # 本文件
```

## 数据库表设计

- **users** — 用户（id, username, password_hash, role, display_name, email, created_at）
- **courses** — 课程（id, name, description, teacher_id, created_at）
- **enrollments** — 选课记录（id, student_id, course_id, enrolled_at）
- **evaluations** — 评价记录（id, student_id, course_id, rating, comment, created_at）

## API 接口

所有 API 均需登录（基于 Session），并按照角色做权限控制。主要接口：

| 方法   | 路径                          | 角色            | 说明             |
|--------|-------------------------------|-----------------|------------------|
| POST   | /api/login                    | 所有            | 用户登录         |
| POST   | /api/logout                   | 所有            | 退出登录         |
| GET    | /api/me                       | 所有            | 获取当前用户信息 |
| GET    | /api/courses                  | 所有            | 课程列表         |
| POST   | /api/enroll/<course_id>       | 学生            | 选课             |
| POST   | /api/evaluate/<course_id>     | 学生            | 提交评价         |
| GET    | /api/my-enrollments           | 学生            | 我的选课         |
| GET    | /api/my-evaluations           | 学生            | 我的评价历史     |
| GET    | /api/my-courses               | 教师            | 我教授的课程     |
| GET    | /api/course/<id>/stats        | 教师/管理员     | 课程评价统计     |
| GET    | /api/course/<id>/evaluations  | 教师/管理员     | 课程详细评价     |
| GET    | /api/course/<id>/export       | 教师/管理员     | 导出评价 CSV     |
| GET    | /api/admin/courses            | 管理员          | 全部课程管理     |
| POST   | /api/admin/courses            | 管理员          | 添加课程         |
| PUT    | /api/admin/courses/<id>       | 管理员          | 编辑课程         |
| DELETE | /api/admin/courses/<id>       | 管理员          | 删除课程         |
| GET    | /api/admin/users              | 管理员          | 用户列表         |
| PUT    | /api/admin/users/<id>/role    | 管理员          | 修改用户角色     |
| GET    | /api/admin/dashboard          | 管理员          | 仪表板数据       |
