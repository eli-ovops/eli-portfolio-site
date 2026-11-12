"""English copy and locale-specific public rendering. No automatic translation service."""
import copy
import json
import re

UI = {
'FDE（前沿部署工程师）：贴近业务，选工具、改流程，需要时开发软件。':'FDE (Forward Deployed Engineer): work close to the business, choose tools, improve workflows and build software when needed.',
'帮企业用好 AI，少一点焦虑':'Put AI to work with less uncertainty',
'跨行业成功案例':'successful cases across industries',
'免费咨询，先聊一件事。':'Free consultation. Start with one task.',
'免费咨询':'Free consultation',
'说说公司最费时间的工作。不必先懂 AI，也不用准备完整方案，一起找一个适合开始的小改动。':'Share the task that takes your company the most time. No AI knowledge or complete plan needed. Find one small change to start with.',
'一起找到 AI 的实际用处':'Find practical uses for AI together',
'聊聊你的业务':'Talk about your business',
'看实际案例':'See project work',
'服务方式':'Ways I can help',
'先聊公司最费时间的一件事。':'Start with your company’s most time-consuming task.',
'不用先想清方案。说说你的业务、团队人数和重复工作，一起判断从哪里开始。':'You do not need a complete solution. Share your business, team size and repetitive tasks, and we can find a starting point.',
'从需求推进到开发与测试。':'Take requirements through development and testing.',
'按明确职责推进项目。':'Contribute within clearly defined responsibilities.',
'看独立开发案例':'See independent work',
'看团队项目案例':'See team contribution',
'先明确问题，再推进实现。':'Define the problem. Then build.',
'从需求梳理推进到可运行版本。':'Take requirements through to a working version.',
'按明确分工协同推进项目。':'Work together within clear project roles.',
'贴近业务做工程，并跟进实际使用反馈。':'Build close to the business and follow real-use feedback.',
'先识别重复操作、信息断点和实际约束，再判断软件能解决什么。':'Identify repetitive work, information gaps and constraints before choosing what software should solve.',
'明确岗位、数据来源与实施范围。':'Define roles, data sources and scope.',
'让流程、数据与运行环境相互衔接。':'Connect workflows, data and the operating environment.',
'分阶段验证，保留测试与验收记录。':'Validate in stages and keep test and acceptance records.',
'明确培训、移交与维护安排。':'Set out training, handover and maintenance.',

'问答与引用示意':'Illustrative answers and citations',
'已有证据与缺口':'Available evidence and gaps',
'FDE · 前沿部署工程师': 'FDE · Forward deployed engineer',
'内容工作台':'Content workbench',
'首次联系，可以先说说你的业务流程、遇到的问题和希望改善的结果。':'To start, share your workflow, the problem you face and the outcome you want.',
'Eli首页': 'Eli home',
'Eli 的项目经历与当前 FDE 工作方向。': 'Eli’s projects and work in forward deployed engineering.',
'上一个案例': 'Previous project', '下一个案例': 'Next project',
'需求往往藏在日常工作中。通过现场观察、访谈与协作，识别重复操作、信息断点和真正的约束，再将这些问题转化为可验证的流程、数据与软件方案。':'Real requirements often emerge from everyday work. Through observation, interviews and collaboration, I identify repetitive tasks, gaps in information and practical constraints, then turn them into testable workflows and software.',
'我理解的 FDE，是贴近客户业务、参与工程实现，并关注方案实际使用结果的工作方式。':'For me, forward deployed engineering means working closely with a business, contributing to implementation and following how the solution performs in practice.',
'理解岗位职责、业务语言与数据来源，明确问题、优先级和实施范围。':'Understand responsibilities, business terminology and data sources; define the problem, priorities and scope.',
'将流程转化为原型与可运行系统，重视数据处理、AI 接入及运行环境。':'Turn workflows into prototypes and working systems, with attention to data, AI integration and the operating environment.',
'以演示和使用反馈校准需求，分阶段验证，保留测试与验收记录。':'Refine requirements through demonstrations and user feedback, validate in stages and retain test and acceptance records.',
'关注使用培训、资料移交与维护安排，让方案能够持续使用和演进。':'Plan training, handover and maintenance so the solution can keep working and evolve.',
'观察流程，了解各岗位的重复工作与实际困难。':'Observe workflows and understand repetitive tasks and practical difficulties.',
'综合业务价值、数据条件与实施成本，确定首个场景。':'Choose the first use case based on business value, available data and implementation cost.',
'用可演示的方案明确流程与范围，及时收集反馈。':'Use a demonstrable prototype to clarify the workflow and scope, and gather feedback early.',
'结合实际使用调整功能，逐步推进测试与验收。':'Adjust features based on real use and progress through testing and acceptance.',
'整理代码、文档与操作说明，做好移交和版本管理。':'Organize code, documentation and operating instructions for handover and version management.',
'回顾使用效果与未解决的问题，为下一轮改进提供依据。':'Review results and unresolved issues to guide the next iteration.',
'想了解 AI 如何融入企业业务？':'How could AI work for your business?',
'欢迎联系我，聊聊你的实际需求。':'Get in touch to discuss what you need.',
'你的工作，也许能用 AI 提效。':'AI could make your work more efficient.',
'聊聊你的实际流程，看看 AI 能在哪些地方帮上忙。':'Let’s discuss your workflow and see where AI could help.',
'代表项目纵深展示，可向下滚动或使用上一项和下一项按钮':'Selected projects in depth. Scroll within this area or use the previous and next buttons.',
'流程示意 · 非客户系统截图':'Workflow illustration · not a client system screenshot',
'客户项目、产品实践与专题研究。':'Client work, product development and research.',
'项目名称、功能或方向':'Project, feature or topic',
'未找到匹配的项目。':'No matching projects.',
'请返回首页浏览项目。':'Return home to explore the projects.',
'从业务调研到价值复盘':'From discovery to review',
'业务理解，<br>工程实践。':'Understand the business.<br>Build the solution.',
'← 返回项目选集':'← Back to selected projects',
'查看项目过程 ＋':'Project process ＋',
'放大微信二维码':'Enlarge WeChat QR code',
'Eli 的微信二维码':'Eli’s WeChat QR code',
'Eli · FDE 与项目经历':'Eli · Forward Deployed Engineering',
'业务理解':'Business understanding', '工程实现':'Engineering', '迭代交付':'Iterative delivery', '长期协作':'Ongoing collaboration',
'业务调研':'Discovery', '场景筛选':'Use-case selection', '原型验证':'Prototype validation', '协同迭代':'Iteration', '成果沉淀':'Handover', '价值复盘':'Review',
'背景与经历':'Background', '关于 Eli':'About Eli', '关于我':'About me',
'项目索引':'Project library', '项目库':'Projects', '代表项目':'Selected projects',
'项目与实践':'PROJECTS & PRACTICE', '工作方式':'HOW I WORK', '独立项目':'Independent work', '团队协作':'Team collaboration',
'流程设计':'Workflow design', 'AI 辅助开发':'AI-assisted development', '测试与维护':'Testing & maintenance',
'← 返回项目库':'← Back to projects',
'需求分析':'Requirements analysis', '文档编写':'Documentation', '开发实现':'Development',
'以 AI 辅助开发，承担流程设计、测试与维护。':'Use AI-assisted development and handle workflow design, testing and maintenance.',
'依据项目分工参与需求、文档或开发工作。':'Contribute to requirements, documentation or development according to the project role.',
'全部记录':'All projects', '项目分类':'Project categories', '搜索项目':'Search projects', '38 项记录':'38 projects',
'清除筛选':'Clear filters', '客户项目':'Client work', '网站与工具':'Websites & tools', '移动应用':'Mobile apps', '内容与研究':'Content & research', '方法与工具':'Methods & tools',
'客户参与':'Client work', 'App 实践':'Mobile apps', '方法与支持':'Methods & tools', '全部':'All',
'内容概览':'Overview', '案例内容':'Case sections', '更多项目':'More projects', '项目链接':'Project link', '打开项目网站':'Visit project website',
'查看大图':'View full image', '页面未找到':'Page not found', '未找到页面':'Page not found', '返回首页':'Back home',
'公益网站':'Nonprofit website', '律所网站':'Law firm website', '库存管理':'Inventory management', '办公协同':'Office workflows', '品牌营销':'Brand marketing', 'AI 客服':'AI support', '品牌网站':'Brand website', '扫码库存':'Barcode inventory', '小红书营销':'RED marketing', '每日任务应用':'Daily task app',
'产品目录':'Product catalog', '回到顶部':'Back to top', '跳到正文':'Skip to content', '主导航':'Main navigation', '个人介绍':'Introduction',
'浏览项目':'Explore projects', '联系我':'Contact', '联系方式':'Contact details', '页面导航':'Page navigation', '邮箱':'Email', '电话/微信/WhatsApp':'Phone/WeChat/WhatsApp', '电话':'Phone', '微信':'WeChat', '联系':'Contact', '首页':'Home', '关于':'About',
'查看 ':'View ', ' 截图':' screenshot', '展开 ':'Expand ', ' 案例':' project',
'公益机构\n展示官网':'Nonprofit\nwebsite', '专业服务\n展示官网':'Professional\nservices', '库存管理\n业务系统':'Inventory\nmanagement', '内部办公\n协同系统':'Office\nworkflows', '品牌出海\n全域营销':'International\nmarketing', '知识检索\n智能客服':'Knowledge\nretrieval', '品牌展示\n产品官网':'Brand\nwebsite', '扫码出入库\n库存追踪':'Scan\nand track', '自动做图\n自动上传':'Create\nand upload', '每日任务\n微冒险应用':'Daily\nadventures',
}


def translate_ui(text):
    for source in sorted(UI, key=len, reverse=True):
        text = text.replace(source, UI[source])
    return text


def english_content(root, profile, projects):
    data = json.loads((root / 'content/en.json').read_text())
    assert set(data['projects']) == {p['id'] for p in projects}
    translated = copy.deepcopy(projects)
    for p in translated:
        item = data['projects'][p['id']]
        p['name'] = p['publicTitle'] = item['title']
        p['displaySummary'] = item['summary']
        p['processSummary'] = item.get('process', item['summary'])
        assert len(item['story']) == len(p['publicStory']), p['id']
        for section, paragraphs in zip(p['publicStory'], item['story']):
            assert len(paragraphs) == len(section['paragraphs']), p['id']
            section['title'] = {'why':'Context','role':'My role','outputs':'Work delivered','process':'Approach','result':'Delivery & feedback','qa':'Illustrative answers and citations','evidence':'Available evidence and gaps'}[section['id']]
            section['paragraphs'] = paragraphs
        p['publicImageAlt'] = item['title'] + (' — anonymized interface' if p.get('anonymized') else ' — interface preview')
        if item.get('imageNote'):
            p['publicImageNote'] = item['imageNote']
    return dict(profile, **data['profile']), translated


def english_assets(text):
    """Shared assets live at the site root; English pages live one directory deeper."""
    names = r'(?:assets/|styles\.css|motion\.css|app\.js|motion\.js)'
    return re.sub(r'((?:href|src|srcset)="|, )((?:\.\./)*)('+names+r')',
                  lambda m: m[1] + '../' + m[2] + m[3], text)
