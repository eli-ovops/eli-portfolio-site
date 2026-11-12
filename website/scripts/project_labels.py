"""Visitor-facing names only; persisted category keys and search data stay stable."""
PROJECT_FILTERS = ('全部','客户参与','网站与工具','App 实践','内容与研究','方法与支持')
CATEGORY_LABELS = {
    '客户参与':'客户项目',
    '网站与工具':'网站与工具',
    'App 实践':'移动应用',
    '内容与研究':'内容与研究',
    '方法与支持':'方法与工具',
}

def category_label(key):
    return CATEGORY_LABELS.get(key,key)
