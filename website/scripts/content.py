# -*- coding: utf-8 -*-
"""Validate the public content contract before rendering or writing output."""
import json
import re
from urllib.parse import urlparse


def load_content(root):
    def read(name):
        return json.loads((root / 'content' / (name + '.json')).read_text(encoding='utf-8'))
    profile, projects, images = read('profile'), read('projects'), read('images')
    required = ('id', 'name', 'fullName', 'category', 'label', 'intro', 'work', 'displaySummary',
                'evidence', 'boundary', 'status', 'experience', 'personalRole')
    seen = set()
    for p in projects:
        if any(not isinstance(p.get(k), str) for k in required):
            raise ValueError('Project fields must be strings: ' + str(p.get('id')))
        if not re.fullmatch(r'[A-Z][0-9]+', p['id']) or p['id'].lower() in seen:
            raise ValueError('Invalid or duplicate project id: ' + p['id'])
        seen.add(p['id'].lower())
        if p.get('image'):
            key = p['image'].lower()
            image_format = p.get('imageFormat', 'webp')
            if not re.fullmatch(r'img[0-9]+', key) or image_format not in ('webp', 'png', 'jpg'):
                raise ValueError('Invalid image path: ' + p['id'])
            if key not in images or not (root / 'assets' / (key + '.' + image_format)).is_file():
                raise ValueError('Missing image: ' + key)
        for key in ('imageAlt', 'imageCaption'):
            if key in p and not isinstance(p[key], str):
                raise ValueError('Invalid image description: ' + p['id'])
        if p.get('anonymized') and p.get('image') and not p.get('publicImage'):
            raise ValueError('Anonymous case needs a sanitized image: ' + p['id'])
        if p.get('publicImage'):
            dims = p.get('publicImageDimensions')
            if (not re.fullmatch(r'assets/public-cases/p[0-9]+\.png', p['publicImage'])
                or not (root / p['publicImage']).is_file()
                or not isinstance(dims, list) or len(dims) != 2
                or any(not isinstance(x, int) or x <= 0 for x in dims)
                or not isinstance(p.get('publicImageAlt'), str)):
                raise ValueError('Invalid anonymous image: ' + p['id'])
        if p.get('publicUrl'):
            url = urlparse(p['publicUrl'])
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise ValueError('Invalid public project URL: ' + p['id'])
        if p.get('evidenceDate') and not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', p['evidenceDate']):
            raise ValueError('Invalid evidence date: ' + p['id'])
        if 'caseStudy' in p:
            for key in ('why', 'role', 'outputs', 'process', 'result', 'evidence'):
                value = p['caseStudy'].get(key)
                if not isinstance(value, list) or not value or any(not isinstance(x, str) for x in value):
                    raise ValueError('Invalid case study field: ' + p['id'] + '/' + key)
        story = p.get('publicStory')
        if not isinstance(story, list) or not story:
            raise ValueError('Missing visitor story: ' + p['id'])
        story_ids = set()
        for entry in story:
            key = entry.get('id', '')
            paragraphs = entry.get('paragraphs')
            if (key not in ('why', 'role', 'outputs', 'process', 'result', 'qa', 'evidence') or key in story_ids
                or not isinstance(entry.get('title'), str) or not isinstance(paragraphs, list)
                or not paragraphs or any(not isinstance(x, str) or not x for x in paragraphs)):
                raise ValueError('Invalid visitor story: ' + p['id'])
            story_ids.add(key)
        if 'homePreview' in p:
            for key in ('title', 'kind', 'summary', 'stage', 'role'):
                if not isinstance(p['homePreview'].get(key), str):
                    raise ValueError('Invalid home preview: ' + p['id'] + '/' + key)
    for p in projects:
        for related in p.get('caseStudy', {}).get('related', []):
            if not isinstance(related, str) or related.lower() not in seen:
                raise ValueError('Unknown related case: ' + str(related))
    for k in ('headline', 'intro', 'about', 'personality', 'background'):
        if not isinstance(profile.get(k), str):
            raise ValueError('Missing profile field: ' + k)
    email = profile.get('email')
    if email and not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+', email):
        raise ValueError('Invalid public email')
    phone = profile.get('phone')
    if phone and not re.fullmatch(r'\+?[0-9]{7,15}', phone):
        raise ValueError('Invalid public phone')
    qr = profile.get('wechatQr')
    if qr and (not re.fullmatch(r'assets/[a-z0-9-]+\.(png|jpg|webp)', qr) or not (root / qr).is_file()):
        raise ValueError('Invalid WeChat image')
    return profile, projects, images
