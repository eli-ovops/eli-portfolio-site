# -*- coding: utf-8 -*-
"""Page composition; no file writes, network requests or global content state."""
from components import escape, CLIENT_PROJECT_IDS, international_phone
from project_order import FEATURED_PROJECT_IDS, prioritize_projects


def shared_content(r, profile, projects):
    client_ids = CLIENT_PROJECT_IDS
    def project_entry(p):
        sentences = {
            'P02': '参与公益官网开发，呈现机构介绍、公益项目与信息公开内容。',
            'P03': '参与律所官网开发，整合专业服务、律师团队与咨询入口。',
            'P04': '依据团队驻场调研开发律所 OA，整合办公流程与分散资料。',
            'P05': '参与品牌出海营销，开展活动策划、AI 视频制作与社交平台引流。',
            'P07': '主导英文家具品牌官网开发，展示产品、工厂与品牌信息。',
            'P08': '制作家具产品目录，整理图片、型号、尺寸与规格。',
            'P09': '主导扫码库存系统开发，实现入库、移库、出库与撤销纠错。',
            'P10': '独立开发洁具行业库存管理系统，完成需求梳理与项目交付。',
            'P11': '制作海外小商户网站改版演示，梳理移动端浏览与询盘路径。',
            'P12': '开发小红书营销工具，串联自动做图、文案生成与内容上传。',
            'P14': '开发宠物陪伴专注应用，设计专注流程并接入通知与锁屏活动。',
            'P15': '开发宠物社交应用，串联宠物资料、发现邀请与聊天流程。',
            'P16': '开发地点水印相机，支持拍摄、定位、水印生成与分享。',
            'P17': '制作起卦与卦文阅读原型，加入反思问题和本地历史记录。',
            'P18': '制作学习时长提醒原型，验证用量回调与达标提醒逻辑。',
            'P19': '制作发型试戴原型，组织三视图输入、候选对比与参考卡。',
            'P20': '制作理赔产品概念页，展示工作流、功能与使用场景。',
            'P21': '修复自动挂单流程，加入重连续办、订单核对与持久审计。',
            'P22': '搭建跨交易所价差取证流程，保存盘口事件并进行数据回放。',
            'P23': '构建策略研究框架，核对交易规则、费用情景与回测过程。',
            'P24': '研究公司与产业机会，依据官方资料核对估值假设与反证。',
            'P25': '设计个性化 AI 新闻简报，梳理兴趣画像、信息去重与订阅解析。',
            'P26': '制作应用推广短视频素材，整理脚本、分镜、字幕与声音剪辑。',
            'P27': '研究无脸播客与历史奇事频道，整理选题、成本与制作计划。',
            'P28': '研究海外小应用机会，比较用户需求、替代工具与本土化方向。',
            'P29': '整理 AI 项目情报，建立公开来源、评分规则与日报模板。',
            'P30': '整理 AI 协作流程，明确任务分工、工具选择与成果检查。',
            'P31': '开展 Mac 磁盘审计，核对清理范围、数据副本与空间变化。',
            'P32': '整理技能与知识索引，明确适用范围、依赖与复用方式。',
            'P33': '制作远程模型试用客户端，提供隔离配置与指定调用入口。',
            'P34': '整理合作提案与机会评估材料，梳理服务范围和客户需求。',
            'P35': '整理化工论文要求与选题材料，建立写作目录和资料交接包。',
            'P36': '参与品牌 RAG 客服定制，负责知识库整理、检索配置与测试。',
            'N01': '搭建远程通知验证界面，核对授权、设备注册与真机送达流程。',
            'N02': '整理 DevDay 官方内容，研究开发能力、开放状态与应用边界。'
        }
        return ('<li><h4>' + escape(r.title(p)) + '</h4><p>'
                + escape(sentences[p['id']]) + '</p></li>')
    remaining = [p for p in projects if p['id'] not in client_ids + ('P01', 'P06', 'P13')]
    groups = [('客户项目', [r.projects[pid] for pid in client_ids]),
              ('产品与工具实践', [p for p in remaining if p['category'] in ('网站与工具', 'App 实践')]),
              ('研究与工作方法', [p for p in remaining if p['category'] not in ('网站与工具', 'App 实践')])]
    clients = ''.join('<section class="project-experience-group"><h3>' + escape(label)
                      + '</h3><ul class="project-experience-grid">' + ''.join(project_entry(p) for p in items)
                      + '</ul></section>' for label, items in groups)
    filters = ''
    categories = [('全部', '全部'), ('客户参与', '客户项目'), ('网站与工具', '网站与工具'),
                  ('App 实践', '移动应用'), ('内容与研究', '内容与研究'), ('方法与支持', '方法与工具')]
    for category, label in categories:
        pressed = str(category == '全部').lower()
        filters += (f'<button type="button" data-filter="{escape(category)}" '
                    f'aria-pressed="{pressed}">{escape(label)}</button>')
    fields = {key: escape(profile[key]) for key in ('intro', 'personality', 'about', 'background')}
    fields['headline'] = escape(profile['headline']).replace('\n', '<br>')
    return dict(fields, clients=clients, filters=filters,
                archive=''.join(r.archive_row(p) for p in prioritize_projects(projects)))


def home(r, profile, projects):
    shared = shared_content(r, profile, projects)
    shared['public_name'] = escape(profile.get('displayName') or '作者')
    shared['featured_gallery'] = ''.join(r.gallery_card(pid) for pid in FEATURED_PROJECT_IDS)
    english = r.lang == 'en'
    heading = 'Find work for your workflow' if english else '按需求看案例'
    topics = [
        ('Inventory & scanning', '库存与扫码',
         'Receiving, transfers, dispatch and stocktakes.', '连接入库、移库、出库与盘点，核对库存数量。',
         [('P10', 'Inventory case', '看库存案例'), ('P09', 'Barcode case', '看扫码案例')]),
        ('Business websites', '企业官网',
         'Organize products, brand information and buyer inquiry paths.', '组织产品、品牌和工厂信息，梳理采购商的浏览与询盘路径。',
         [('P07', 'Website case', '看官网案例')]),
    ]
    cards = ''
    for en_title, zh_title, en_text, zh_text, links in topics:
        actions = ''.join(r.link(r.projects[pid], en_label if english else zh_label)
                          for pid, en_label, zh_label in links)
        cards += (f'<article><h3>{en_title if english else zh_title}</h3>'
                  f'<p>{en_text if english else zh_text}</p><div class="topic-actions">{actions}</div></article>')
    shared['customer_topics'] = (f'<section class="customer-topics" id="needs" aria-labelledby="needs-title">'
                                 f'<h2 id="needs-title">{heading}</h2><div class="topic-grid">{cards}</div></section>')
    body = r.template('home', **shared)
    return r.shell('Eli · FDE 与项目经历', body, current='home')


def about(r, profile, projects):
    shared = shared_content(r, profile, projects)
    email = profile.get('email')
    methods = ''
    if email:
        methods += (f'<div class="contact-method"><p>邮箱</p>'
                    f'<a class="text-link" href="mailto:{escape(email)}">{escape(email)} ↗</a></div>')
    phone = profile.get('phone')
    if phone:
        number = international_phone(phone)
        methods += (f'<div class="contact-method"><p>电话</p>'
                    f'<a class="text-link" href="tel:{escape(number)}">{escape(number)} ↗</a></div>')
        if number.startswith('+'):
            methods += (f'<div class="contact-method"><p>WhatsApp</p>'
                        f'<a class="text-link" href="https://wa.me/{escape(number[1:])}" target="_blank" '
                        f'rel="noopener noreferrer">{escape(number)} ↗</a></div>')
    shared['contact_content'] = '<div class="contact-methods">' + methods + '</div>'
    qr = profile.get('wechatQr')
    shared['wechat_qr'] = (
        '<figure class="wechat-contact" id="wechat"><h3>微信</h3>'
        f'<a href="{escape(qr)}" target="_blank" rel="noopener noreferrer" aria-label="放大微信二维码">'
        f'<img src="{escape(qr)}" width="728" height="728" loading="lazy" decoding="async" alt="Eli 的微信二维码">'
        '</a></figure>' if qr else '')
    english = r.lang == 'en'
    heading = 'Tools in practice' if english else '技术与实践'
    intro = 'Technology choices, connected to the work they support.' if english else '技术选择，落在具体项目与流程里。'
    groups = [('Web interfaces', '网页交互', 'React · TypeScript · Vite', 'P06'),
              ('Inventory systems', '业务系统', 'Java · Spring Boot · Vue · MySQL', 'P10'),
              ('Cloud inventory', '云端库存', 'Cloudflare Workers · D1 / SQLite · Playwright', 'P09'),
              ('AI content workflows', 'AI 内容工作流', 'TypeScript · Node.js · Provider abstraction', 'P12'),
              ('Native iOS', '原生 iOS', 'SwiftUI · SwiftData · StoreKit · XCTest', 'P13')]
    rows = ''
    for en_label, zh_label, stack, pid in groups:
        title = r.title(r.projects[pid])
        tools = ''.join(f'<li>{escape(tool.strip())}</li>' for tool in stack.split('·'))
        link_label = 'View case study' if english else '查看案例'
        rows += (f'<div class="technology-row"><dt>{escape(en_label if english else zh_label)}</dt>'
                 f'<dd><ul class="technology-tools">{tools}</ul>'
                 f'<a class="text-link technology-project" href="cases/{pid.lower()}.html" aria-label="{escape(title)}">{link_label} <span aria-hidden="true">↗</span></a></dd></div>')
    shared['technical_content'] = (f'<section class="technology-section" id="technology"><h2>{heading}</h2>'
                                   f'<p class="technology-intro">{intro}</p><dl>{rows}</dl></section>')
    questions = ''
    for number, item in enumerate(r.seo['questions'], 1):
        copy = item[r.lang]
        links = ''.join(f'<a class="text-link" href="cases/{pid.lower()}.html">'
                        f'{escape(r.title(r.projects[pid]))} <span aria-hidden="true">↗</span></a> '
                        for pid in item['projects'])
        questions += (f'<details class="about-question" name="cooperation"><summary>'
                      f'<span class="question-number" aria-hidden="true">{number:02}</span>'
                      f'<span>{escape(copy["question"])}</span><span class="question-symbol" aria-hidden="true"></span></summary>'
                      f'<div class="question-answer"><p class="question-lead">{escape(copy["lead"])}</p>'
                      f'<p>{escape(copy["answer"])}</p><div class="question-links">{links}</div></div></details>')
    questions_heading = 'Working together' if english else '常见合作问题'
    shared['questions_content'] = (f'<section class="cooperation-section" id="questions" aria-labelledby="questions-title">'
                                   f'<h2 id="questions-title">{questions_heading}</h2><div class="question-list">{questions}</div></section>')
    body = r.template('about', **shared)
    return r.shell('关于我', body, current='about')


def records(r, profile, projects):
    shared = shared_content(r, profile, projects)
    english = r.lang == 'en'
    copy = ('Try inventory, barcode or website. Stock management shows related inventory work; check each case for its scope.'
            if english else '可搜库存、扫码、官网。进销存显示相关库存实践，具体功能以案例为准。')
    inventory, website = ('inventory', 'website') if english else ('库存', '网站')
    shared['customer_search_help'] = (f'<p class="customer-search-help">{copy}</p>'
        f'<nav class="customer-search-links" aria-label="'+ ('Workflow shortcuts' if english else '业务快捷入口') +'">'
        f'<a class="text-link" href="records.html?q={inventory}">'+ ('Inventory cases' if english else '看库存案例') +' ↗</a>'
        f'<a class="text-link" href="records.html?q={website}">'+ ('Website cases' if english else '看官网案例') +' ↗</a></nav>')
    body = r.template('records', **shared)
    return r.shell('项目索引', body, current='work')


def case(r, p):
    example = r.case_examples.get(p['id'], {})
    lang = r.lang
    image = ''
    if p.get('image'):
        note = f'<p class="case-image-note">{escape(p["publicImageNote"])}</p>' if p.get('publicImageNote') else ''
        image_path = escape(r.image_path(p, '../'))
        title = escape(r.title(p))
        label = ('Enlarge screenshot: ' if lang == 'en' else '放大截图：') + title
        viewer = (f'data-image-view data-image-title="{title}" '
                  f'data-image-note="{escape(p.get("publicImageNote", ""))}" aria-haspopup="dialog"')
        image = (f'<figure class="detail-image {p["id"].lower()}">'
                 f'<a class="detail-image-trigger" href="{image_path}" {viewer} aria-label="{label}">'
                 + '<span class="detail-image-visual">' + r.image(p, '../') + '</span></a>'
                 '<figcaption>' + note +
                 f'<a class="text-link" href="{image_path}" {viewer} target="_blank" rel="noopener noreferrer">查看大图 ↗</a>'
                 '</figcaption></figure>')
    fields = {k: escape(v) for k, v in p.items() if isinstance(v, str)}
    fields['image'] = image
    fields['project_summary'] = escape(example.get('hero_intro', {}).get(lang, p['displaySummary']))
    stage = example.get('hero_stage', example.get('stage', {}))
    fields['case_stage'] = f'<p class="case-stage">{escape(stage[lang])}</p>' if stage else ''
    study = p.get('caseStudy', {})
    fields['case_title'] = escape(p.get('publicTitle') or p.get('homePreview', {}).get('title') or p['name'])
    facts = [f'<div><dt>{escape(label)}</dt><dd>{escape(text)}</dd></div>'
             for label, text in example.get('facts', {}).get(lang, [])]
    fields['case_facts'] = '<dl class="case-facts">' + ''.join(facts) + '</dl>' if facts else ''
    sections, index = '', ''
    for entry in p['publicStory']:
        key, title = entry['id'], entry['title']
        section = (f'<section id="{key}"><h2>{escape(title)}</h2>'
                   + ''.join(f'<p>{escape(text)}</p>' for text in entry['paragraphs']))
        if key == 'process' and example.get('rows'):
            heading = example['heading'][lang]
            headers = ''.join(f'<th scope="col">{escape(label)}</th>' for label in example['headers'][lang])
            rows = ''.join('<tr>' + f'<th scope="row">{escape(row[0])}</th>'
                           + ''.join(f'<td>{escape(cell)}</td>' for cell in row[1:]) + '</tr>'
                           for row in example['rows'][lang])
            section += (f'<div class="case-example"><h3>{escape(heading)}</h3>'
                        f'<p>{escape(example["intro"][lang])}</p>'
                        f'<table aria-label="{escape(heading)}"><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>'
                        f'<p class="case-example-note">{escape(example["note"][lang])}</p></div>')
        if key == 'qa' and example.get('illustrations'):
            illustrative = 'AI-written illustration · not a real support record' if lang == 'en' else 'AI 拟写示意 · 非真实客服记录'
            answer_label = 'Illustrative answer' if lang == 'en' else '示意答复'
            for item in example['illustrations'][lang]:
                section += (f'<article class="case-example"><h3>{escape(item["question"])}</h3>'
                            f'<p class="case-example-note">{illustrative}</p>'
                            f'<p><strong>{answer_label}：</strong>{escape(item["answer"])}</p>'
                            f'<p><a class="text-link" href="#{escape(item["source_id"])}">{escape(item["source_label"])} ↓</a></p>'
                            f'<blockquote class="case-source-excerpt" id="{escape(item["source_id"])}">'
                            f'<p>{escape(item["excerpt"])}</p><cite>{escape(item["source_label"])}</cite></blockquote></article>')
        sections += section + '</section>'
        index += f'<a href="#{key}">{escape(title)}</a>'
    if p.get('publicUrl') and not p.get('anonymized'):
        sections += (f'<section id="evidence"><h2>项目链接</h2><p><a class="text-link" href="{escape(p["publicUrl"])}" '
                     'target="_blank" rel="noopener noreferrer">打开项目网站 ↗</a></p></section>')
        index += '<a href="#evidence">项目链接</a>'
    technical = r.technical.get(p['id'])
    if technical:
        lang = r.lang
        title = 'Technical approach' if lang == 'en' else '技术与实现'
        validation = 'Validation scope' if lang == 'en' else '验证范围'
        tags = ''.join(f'<li>{escape(tool)}</li>' for tool in technical['stack'])
        flow = ''.join(f'<li><strong>{escape(step["label"])}</strong><p>{escape(step["detail"])}</p></li>' for step in technical.get('flow', {}).get(lang, []))
        flow_heading = 'Implementation flow' if lang == 'en' else '实现流程'
        flow_html = f'<h3>{flow_heading}</h3><ol class="technical-flow" aria-label="{flow_heading}">{flow}</ol>' if flow else ''

        sections += (f'<section id="technical"><h2>{title}</h2><ul class="technology-tools">{tags}</ul>'
                     f'<p>{escape(technical["approach"][lang])}</p>{flow_html}'
                     f'<h3>{validation}</h3><p>{escape(technical["verification"][lang])}</p></section>')
        index += f'<a href="#technical">{title}</a>'
    fields.update(case_sections=sections, case_index=index)
    fields['related'] = ''.join(
        f'<p class="case-related"><a class="text-link" href="{pid.lower()}.html">'
        f'{escape(r.projects[pid].get("publicTitle") or r.projects[pid]["name"])} ↗</a></p>' for pid in study.get('related', []))
    heading = 'Discuss your workflow' if lang == 'en' else '聊聊你的需求'
    copy = ('Share your current workflow, the problem and the outcome you need. We can then discuss scope and delivery.'
            if lang == 'en' else '说清现有流程、遇到的问题和希望改善的结果，再讨论实施范围与交付安排。')
    label = 'Discuss scope' if lang == 'en' else '讨论实施范围'
    fields['case_contact'] = (f'<section class="case-contact" aria-labelledby="case-contact-title">'
        f'<div><h2 id="case-contact-title">{heading}</h2><p>{copy}</p></div>'
        f'<a class="text-link" href="../about.html#contact">{label} <span aria-hidden="true">↗</span></a></section>')
    body = r.template('case', **fields)
    return r.shell(r.title(p), body, '../', 'work', 'cases/' + p['id'].lower() + '.html')


def not_found(r):
    body = ('<main id="main" class="not-found"><p class="meta">404</p>'
            '<h1>页面未找到</h1><p>请返回首页浏览项目。</p>'
            '<a class="primary" href="index.html">返回首页 ↗</a></main>')
    return r.shell('未找到页面', body, page_path='404.html')
