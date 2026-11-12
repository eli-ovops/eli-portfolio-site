from pathlib import Path
import json, datetime, re

R = Path(__file__).resolve().parents[2]
E = Path(__file__).resolve().parent
tech = json.loads((E/'technical-checks.json').read_text())
origin = json.loads((E/'verified-ai-origin-requests.json').read_text())
links = json.loads((E/'directed-citation-links.json').read_text())
for path in E.glob('*.txt'):
    assert not re.search(r'token=(?!\[REDACTED\])[^\s"\'&<>]+', path.read_text()), path.name
for slug in ['inventory','knowledge','ai-basics']:
    g = (E/('google-'+slug+'-inspection.txt')).read_text()
    b = (E/('bing-'+slug+'-inspection.txt')).read_text()
    assert 'url_unknown' in g
    assert 'The inspected URL is not known to Bing.' in b
assert len(links['chatgpt']) == 3
assert all('utm_source=chatgpt.com' in x['url'] for x in links['chatgpt'])
receipt = dict(
    checked_at=datetime.datetime.now().astimezone().isoformat(),
    status='AUDITED_DISCOVERY_NOT_YET_CONFIRMED', site='https://www.eliai.cn/',
    revision=tech['revision'], website_changes=False, visual_motion_changes=False,
    server_changes=False, search_submissions=0, user_action_required=False,
    technical={k:tech[k] for k in ['status','pages_checked','public_sitemap_urls',
        'article_detail_pages','crawler_access','duplicate_titles','duplicate_descriptions',
        'static_list_link_counts','llms_has_article_entry']},
    native_index_sample=['articles/inventory-reconciliation.html',
        'articles/enterprise-knowledge-base.html','articles/what-is-ai.html'],
    Google=dict(sitemap_last_read='2026-10-17',sitemap_discovered_total=88,
        inspected=3,result='URL unknown;not indexed;no referring sitemap or crawl timestamp'),
    Bing=dict(sitemap_last_crawl='2026-10-15',sitemap_discovered_total=82,
        inspected=3,result='Not discovered;URL not known to Bing',
        ai_report_sources='Microsoft Copilots and Partners',
        ai_report_window='2026-07-17 through2026-10-16',ai_citations=0),
    Baidu=dict(index='Data calculating;count UNKNOWN',sitemap_daily_quota=0,
        sitemap_daily_balance=0,sitemap_stock_limit=1,sitemap_stock_balance=1,
        sitemap_files=0,ai_citations=0,ai_impressions=0,ai_clicks=0,
        ai_report_limit='Traditional search scenes;previous-day update;possible delay'),
    public_search=dict(query='site:www.eliai.cn/articles/',
        engines=['Google Hong Kong','Bing China','Baidu'],
        observed='All3 current result pages say no matching results',
        limit='One query/current region/session;not a full index inventory'),
    ai=dict(unbranded=dict(sample='1prompt/platform;3article intents;no seeded domain',
        platforms=['ChatGPT','Perplexity','Yuanbao','Doubao'],
        result='Each selected other sources;own site absent from selected articles'),
        directed=dict(sample='3Chinese pages;inventory/knowledge-base/agent',
            ChatGPT=dict(body_read=3,clickable_own_sources=3,
                official_range_verified_origin_requests=3,
                quote_accuracy='2/3 selected extracts literal;knowledge-base extract paraphrased'),
            Yuanbao=dict(body_read=3,links='Website URL text returned;ordinary hrefs not confirmed',
                quotes='Selected extracted strings found in source'),
            Doubao=dict(grounded_body_summaries=3,
                links='3destinations through platform redirect hrefs, repeated in prompt and answer',
                quote_accuracy='All3 strings labelled original are paraphrases'),
            Perplexity=dict(body_read=0,verified_origin_article_requests=0,
                result='All3 failed;echoed user URLs are not grounded citations',root_cause='UNKNOWN'))),
    origin=origin,
    recommendations=['Keep existing sitemap URL;allow natural refetch and compare future reports',
        'Track inventory and knowledge-base long-tail article queries first',
        'Optional future bilingual article index entry in llms.txt;not a Google requirement',
        'Keep Perplexity upstream fetch issue separate;do not weaken security without evidence',
        'Do not rewrite correct article text to match AI paraphrases'],
    limitations=['Native index checks sampled3Chinese pages/engine,not all204URLs',
        'AI reading tested3Chinese pages,not all102topics or English pages',
        'Single unbranded run/platform is not a citation rate or ranking benchmark',
        'Source logs limited to current access.log and2026-10-17',
        'No API credentials or raw visitor IPs retained in evidence'])
(E/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
(E/'artifacts.md').write_text('# Audit artifacts\n\nTask-owned read-only audit evidence: technical checks, official public crawler ranges, redacted platform reports, AI test records, screenshots and receipt. Keep for future comparison. No deployment package or server writes. No indexing submissions.\n')
print(json.dumps({k:receipt[k] for k in ['status','revision','search_submissions',
    'website_changes','user_action_required']}))
