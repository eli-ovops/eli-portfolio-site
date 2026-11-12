"""Homepage industry scenarios; related work is distinct from service coverage."""
import json
from components import escape


def render(renderer):
    content = json.loads((renderer.root / 'content/industry-scenarios.json').read_text())
    expected = ['manufacturing', 'ecommerce', 'cross-border', 'wholesale-retail',
                'home-building', 'professional-services', 'brands-studios', 'nonprofits']
    services = {s['slug'] for s in renderer.seo['service_pages']}
    for lang in ('zh-CN', 'en'):
        assert [item['id'] for item in content[lang]['items']] == expected
        assert content[lang]['contact_hint'].strip()
        for item in content[lang]['items']:
            assert item['service'] in services
            assert content[lang]['service_labels'][item['service']].strip()
            assert all(pid in renderer.projects for pid in item['cases'])
            assert all(isinstance(item[key], str) and item[key].strip()
                       for key in ('name', 'summary', 'detail'))
    assert [(i['service'], i['cases']) for i in content['zh-CN']['items']] == [
        (i['service'], i['cases']) for i in content['en']['items']]
    copy = content[renderer.lang]
    rows = []
    for item in copy['items']:
        cases = ''
        if item['cases']:
            links = ''.join(renderer.link(renderer.projects[pid], renderer.title(renderer.projects[pid]))
                            for pid in item['cases'])
            cases = (f'<div class="industry-related"><p class="industry-label">{escape(copy["case_label"])}</p>'
                     f'<p>{escape(item["case_note"])}</p><div class="industry-case-links">{links}</div></div>')
        rows.append(
            f'<details class="industry-item" id="industry-{item["id"]}" data-industry>'
            f'<summary><span class="industry-summary"><span class="industry-name">{escape(item["name"])}</span>'
            f'<span class="industry-brief">{escape(item["summary"])}</span></span>'
            f'<span class="industry-toggle" aria-hidden="true">+</span></summary>'
            f'<div class="industry-content"><p class="industry-label">{escape(copy["scenario_label"])}</p>'
            f'<p>{escape(item["detail"])}</p>{cases}<div class="industry-actions">'
            f'<a class="text-link" href="services/{item["service"]}.html">{escape(copy["service_labels"][item["service"]])} ↗</a>'
            f'<a class="text-link" href="about.html#contact">{escape(copy["contact_label"])} ↗</a>'
            f'</div><p>{escape(copy["contact_hint"])}</p></div></details>')
    return ('<section class="industry-overview" id="industries" aria-labelledby="industries-title">'
            f'<h2 id="industries-title">{escape(copy["heading"])}</h2>'
            f'<p class="industry-intro">{escape(copy["intro"])}</p>'
            '<div class="industry-grid">' + ''.join(rows) + '</div></section>')
