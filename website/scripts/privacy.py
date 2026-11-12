"""Public export policy for customer identities; raw records remain local."""
import re

CLIENT_TERMS = ('予善', '卓建', '淼瀚', '原点向量', 'otherwater',
                'williamrock', 'zhuojian', 'guangming', 'miaohan',
                'yu shan you', 'yushanyou', '乔帮主')


def assert_no_client_identifiers(text, path):
    normalized = re.sub(r'[\s_-]+', '', text).casefold()
    for term in CLIENT_TERMS:
        if re.sub(r'[\s_-]+', '', term).casefold() in normalized:
            raise ValueError('Customer identity in public output: ' + str(path))
