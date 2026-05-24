"""
课程评价系统 - 项目报告生成（彻底修复中文）
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import copy

doc = Document()

# ========== 全局字体修复 ==========
# 修复 Normal 样式
style = doc.styles['Normal']
style.font.name = '微软雅黑'
style.font.size = Pt(12)
style.font.color.rgb = RGBColor(0, 0, 0)
# 设置 Normal 的默认段落字体（影响表格等）
style.element.get_or_add_pPr()
# 关键：设置 east-asia 字体
rPr = style.element.get_or_add_rPr()
rFonts = rPr.find(qn('w:rFonts'))
if rFonts is None:
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="微软雅黑" w:ascii="微软雅黑" w:hAnsi="微软雅黑"/>')
    rPr.insert(0, rFonts)
else:
    rFonts.set(qn('w:eastAsia'), '微软雅黑')
    rFonts.set(qn('w:ascii'), '微软雅黑')
    rFonts.set(qn('w:hAnsi'), '微软雅黑')

# 修复 Heading 1-3 样式
for level in [1, 2, 3]:
    hstyle = doc.styles[f'Heading {level}']
    hstyle.font.name = '微软雅黑'
    hrPr = hstyle.element.get_or_add_rPr()
    hrFonts = hrPr.find(qn('w:rFonts'))
    if hrFonts is None:
        hrFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="微软雅黑" w:ascii="Arial" w:hAnsi="Arial"/>')
        hrPr.insert(0, hrFonts)
    else:
        hrFonts.set(qn('w:eastAsia'), '微软雅黑')
    hstyle.font.color.rgb = RGBColor(0, 51, 102)

# 页面设置
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

def p(text, bold=False, size=Pt(12), align=None, color=None, indent=False):
    """添加段落"""
    para = doc.add_paragraph()
    run = para.add_run(text)
    run.font.name = '微软雅黑'
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="微软雅黑" w:ascii="微软雅黑" w:hAnsi="微软雅黑"/>')
    rPr.insert(0, rFonts)
    run.font.size = size
    run.bold = bold
    if color:
        run.font.color.rgb = color
    if align:
        para.alignment = align
    if indent:
        para.paragraph_format.first_line_indent = Cm(0.74)
    return para

def bullet(text):
    """添加项目符号"""
    para = doc.add_paragraph(style='List Bullet')
    run = para.add_run(text)
    run.font.name = '微软雅黑'
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="微软雅黑" w:ascii="微软雅黑" w:hAnsi="微软雅黑"/>')
    rPr.insert(0, rFonts)
    run.font.size = Pt(12)
    return para

def h(text, level=1):
    """添加标题"""
    heading = doc.add_heading(level=level)
    run = heading.add_run(text)
    run.font.name = '微软雅黑'
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="微软雅黑" w:ascii="Arial" w:hAnsi="Arial"/>')
    rPr.insert(0, rFonts)
    sizes = {1: Pt(22), 2: Pt(16), 3: Pt(13)}
    run.font.size = sizes.get(level, Pt(12))
    return heading

def tbl(headers, data):
    """添加表格"""
    table = doc.add_table(rows=len(data)+1, cols=len(headers), style='Light Grid Accent 1')
    for i, hdr in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(hdr)
        run.bold = True
        run.font.name = '微软雅黑'
        run.font.size = Pt(10)
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            cell = table.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(val)
            run.font.name = '微软雅黑'
            run.font.size = Pt(10)
    doc.add_paragraph()
    return table

# ========== 封面 ==========
doc.add_paragraph()
doc.add_paragraph()
p('人工智能通识课·实践项目', bold=True, size=Pt(26), align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(0, 51, 102))
p('课程评价系统', bold=True, size=Pt(22), align=WD_ALIGN_PARAGRAPH.CENTER, color=RGBColor(0, 102, 153))
doc.add_paragraph()
p('项目类别：第一类——智能体编程应用开发\n技术栈：Python Flask + SQLite + HTML/CSS/JS + ECharts\nGitHub：https://github.com/cty23/project', size=Pt(12), align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_paragraph()
doc.add_paragraph()
p('2026年5月', size=Pt(14), align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_page_break()

# ========== 一、任务阐述 ==========
h('一、任务阐述', 1)
p('本项目来源于《人工智能通识课》实践项目任务书中"第一类：智能体编程应用开发"的要求。任务是利用AI编程助手协同开发一个真实可用的Web应用程序，系统需基于角色进行权限划分，并实现核心业务逻辑。', indent=True)
p('核心硬性指标包括：')
bullet('技术栈：前端（HTML/JS），后端（Python Flask），数据库（SQLite）')
bullet('角色要求：实现至少2个角色（学生、教师、管理员）')
bullet('功能要求：每个角色拥有至少3个核心功能')
bullet('代码规范：完整代码、README.md运行说明及requirements.txt依赖配置')
p('经过选题比较，本项目选择"课程评价系统"作为开发主题。该系统面向高校教学场景，允许学生对已选课程进行打分和文字评价，教师可以查看授课评价的统计数据和详细反馈，管理员负责课程和用户管理并查看全校数据仪表板。系统实现了完整的权限分流，不同角色登录后呈现完全不同的功能界面，并集成了ECharts图表库用于数据可视化展示。', indent=True)

# ========== 二、背景调研 ==========
h('二、背景调研', 1)
h('2.1 课程评价的现实意义', 2)
p('课程评价是高等教育教学质量保障体系的重要组成部分。传统纸质评教方式存在效率低、统计难、反馈滞后等问题。构建一套线上课程评价系统，可以实现评价数据的实时采集、自动统计和可视化呈现，帮助教师及时了解教学效果、调整教学策略，为教学管理部门提供数据支撑。', indent=True)
h('2.2 技术选型依据', 2)
p('后端选择Python Flask框架，原因如下：Flask轻量灵活，学习曲线平缓，适合中小型Web应用的快速开发；Python生态丰富，便于集成数据处理和导出功能。数据库选择SQLite，零配置、无需独立服务进程，适合教学演示和轻量部署场景。前端采用纯HTML/CSS/JS方案，避免引入前端框架的额外学习成本；数据可视化采用ECharts，是国内高校项目中广泛使用的图表库，文档完善、示例丰富。', indent=True)
h('2.3 相关系统分析', 2)
p('目前市面上主流的教务管理系统（如正方、青果等）虽然包含评教模块，但多为大型商业系统，功能冗余、定制困难。部分高校使用问卷星等通用表单工具进行评教，但数据管理分散、分析能力有限。本项目旨在开发一个轻量、专注、易部署的课程评价系统，作为现有方案的有效补充。', indent=True)

# ========== 三、项目设计文档 ==========
h('三、项目设计文档', 1)
h('3.1 系统架构', 2)
p('系统采用经典的B/S（Browser/Server）三层架构：')
bullet('表现层（Frontend）：纯HTML/CSS/JS页面，包含登录页及学生、教师、管理员三个功能界面')
bullet('业务逻辑层（Backend）：Python Flask框架，处理路由、认证、业务逻辑和API接口')
bullet('数据层（Database）：SQLite数据库，存储用户、课程、选课和评价数据')
p('（系统架构图见演示PPT或网页截图）')

h('3.2 数据库设计', 2)
p('数据库包含4张核心表：')
h('users（用户表）', 3)
tbl(['字段', '类型', '说明', '备注'], [
    ('id', 'INTEGER', '主键（自增）', ''),
    ('username', 'TEXT', '用户名（唯一）', '登录用'),
    ('password_hash', 'TEXT', '密码哈希值', 'werkzeug加密'),
    ('role', 'TEXT', '角色', 'student / teacher / admin'),
    ('display_name', 'TEXT', '显示名称', ''),
    ('email', 'TEXT', '邮箱', ''),
    ('created_at', 'TIMESTAMP', '创建时间', '默认当前时间'),
])
h('courses（课程表）', 3)
tbl(['字段', '类型', '说明', '备注'], [
    ('id', 'INTEGER', '主键（自增）', ''),
    ('name', 'TEXT', '课程名称', ''),
    ('description', 'TEXT', '课程描述', ''),
    ('teacher_id', 'INTEGER', '授课教师ID', '外键 -> users.id'),
])
h('enrollments（选课表）', 3)
tbl(['字段', '类型', '说明', '备注'], [
    ('id', 'INTEGER', '主键（自增）', ''),
    ('student_id', 'INTEGER', '学生ID', '外键 -> users.id'),
    ('course_id', 'INTEGER', '课程ID', '外键 -> courses.id'),
])
h('evaluations（评价表）', 3)
tbl(['字段', '类型', '说明', '备注'], [
    ('id', 'INTEGER', '主键（自增）', ''),
    ('student_id', 'INTEGER', '学生ID', '外键 -> users.id'),
    ('course_id', 'INTEGER', '课程ID', '外键 -> courses.id'),
    ('rating', 'INTEGER', '评分（1-5星）', ''),
    ('comment', 'TEXT', '文字评语', ''),
])

h('3.3 功能设计', 2)
p('三个角色的核心功能如下：')
tbl(['角色', '功能1', '功能2', '功能3'], [
    ('学生', '浏览课程列表并选课', '提交课程评价（1-5星+文字）', '查看个人评价历史'),
    ('教师', '查看授课评价统计（均分/图表）', '浏览学生详细评价列表', '导出评价数据为CSV'),
    ('管理员', '课程管理（增删改、分配教师）', '用户管理（查看/修改角色）', '数据仪表板（ECharts可视化）'),
])

h('3.4 权限控制设计', 2)
p('系统基于角色的访问控制（RBAC）模型实现权限管理，关键设计点：')
bullet('每个HTML页面加载时调用 /api/me 接口验证身份和角色，失败则跳转登录页')
bullet('后端使用 @login_required 和 @require_role 装饰器进行接口级权限拦截')
bullet('API层对每次请求重新校验角色，即使前端被篡改也无法越权访问')
bullet('前端根据角色动态渲染不同的菜单和操作按钮，实现界面级权限分流')
bullet('Session有效期控制，超时自动登出')

h('3.5 项目目录结构', 2)
p('项目采用清晰的前后端分离目录组织：')
p('''course-evaluation-system/
├── backend/
│   ├── app.py          # Flask主程序（路由、API端点）
│   ├── models.py       # SQLite数据库模型与初始化
│   └── auth.py         # 登录验证与权限控制装饰器
├── frontend/
│   ├── index.html      # 登录页
│   ├── student.html    # 学生功能界面
│   ├── teacher.html    # 教师功能界面
│   └── admin.html      # 管理员功能界面
├── database/
│   └── init.sql        # 数据库初始化脚本与示例数据
├── requirements.txt    # Python依赖包清单
└── README.md           # 项目运行说明文档''', size=Pt(9))

# ========== 四、结果展示 ==========
h('四、结果展示', 1)
h('4.1 登录页面', 2)
p('登录页为系统入口，采用居中卡片式布局。输入用户名和密码后，系统自动识别角色跳转对应页面。预置测试账号：管理员 admin/admin123，教师 teacher1-teacher3 / 123456，学生 student1-student5 / 123456。', indent=True)
p('[  此处插入登录页截图  ]', bold=True)
h('4.2 学生端', 2)
bullet('选课：浏览全部课程，点击选课按钮加入课程，已选课程按钮自动置灰')
bullet('评价：对已选课程进行1-5星打分 + 文字评语（200字以内）')
bullet('我的评价：查看个人历史评价记录，含课程名、评分、评语、时间')
p('[  此处插入学生端截图  ]', bold=True)
h('4.3 教师端', 2)
bullet('评分统计：显示所授课程的平均分 + ECharts评分分布柱状图')
bullet('评价列表：表格展示学生对课程的详细评价（学生名、评分、评语、时间）')
bullet('数据导出：一键导出评价数据为CSV文件，Excel可直接打开')
p('[  此处插入教师端截图  ]', bold=True)
h('4.4 管理员端', 2)
bullet('课程管理：添加/编辑/删除课程，为课程分配授课教师')
bullet('用户管理：查看全部用户列表，修改用户角色')
bullet('数据仪表板（ECharts）：课程平均分排名柱状图、评分分布饼图、选课统计')
p('[  此处插入管理员端截图  ]', bold=True)
h('4.5 数据可视化', 2)
p('管理员仪表板集成ECharts实现三类图表：（1）课程平均评分排名柱状图，横向比较各课程评价水平；（2）评分分布饼图，展示1-5星的数量与占比；（3）选课人数横向对比图。所有图表数据通过后端API实时查询数据库生成，支持交互式tooltip。', indent=True)
p('[  此处插入ECharts图表截图  ]', bold=True)

# ========== 五、GitHub ==========
h('五、GitHub仓库证明', 1)
p('项目代码已托管至GitHub公开仓库：', indent=True)
p('仓库地址：https://github.com/cty23/project', bold=True, color=RGBColor(0, 102, 204))
p('仓库内容：')
bullet('backend/：Flask后端代码（路由、数据库、认证）')
bullet('frontend/：4个HTML前端页面')
bullet('database/：数据库初始化脚本（10用户+6课程示例数据）')
bullet('requirements.txt：Python依赖清单')
bullet('README.md：安装配置运行说明')
bullet('课程评价系统-项目报告.docx + 课程评价系统-演示.pptx')
p('[  此处插入GitHub仓库首页截图  ]', bold=True)

# ========== 六、总结 ==========
h('六、总结与展望', 1)
h('6.1 项目总结', 2)
p('本项目完成了课程评价系统全部核心功能，实现了学生选课评教、教师统计分析、管理员系统管理的完整业务流程。系统达到任务书全部硬性指标：指定技术栈（Flask+SQLite+HTML/JS）、3角色权限控制、每角色3+核心功能、完整README和依赖文件。', indent=True)
p('额外完成的加分项：')
bullet('完整权限控制——三角色登录后完全不同的功能界面，API层+前端双层校验')
bullet('数据可视化——ECharts集成，展示课程排名、评分分布等多维统计图表')
h('6.2 未来展望', 2)
bullet('部署到云服务器（如Render/Railway），实现公网访问')
bullet('增加匿名评价功能，保护学生隐私，鼓励真实反馈')
bullet('引入NLP情感分析，自动识别评价中的关键意见')
bullet('对接学校统一身份认证（SSO/CAS/OAuth2）')
bullet('增加评价提醒和自动催办功能')
bullet('移动端适配，方便随时随地进行评教')
h('6.3 开发体会', 2)
p('通过本项目，我深入实践了AI辅助编程的工作模式。在与AI编程助手的协作过程中，学习了如何清晰描述需求、分解复杂任务、验证生成代码的正确性。项目覆盖了从需求到部署的完整软件工程流程，加深了对Web开发全流程的理解。AI助手虽大幅提升开发效率，但系统设计能力、问题定位能力和质量标准把控仍是开发者不可替代的核心素养。学会使用AI是手段，理解技术原理和培养工程思维才是目的。', indent=True)

# 保存
output_path = r'C:\Users\cty27\.openclaw\workspace\course-evaluation-system\课程评价系统-项目报告.docx'
doc.save(output_path)
print('OK')
