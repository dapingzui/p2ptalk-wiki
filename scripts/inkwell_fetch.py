#!/usr/bin/env python3
import argparse, json, os, sys, urllib.parse, urllib.request

BASE = os.environ.get('INKWELL_BASE', 'https://inkwell.coze.site/api/v1')
API_KEY = os.environ.get('INKWELL_API_KEY')


def req(path, method='GET', params=None, data=None, auth=True):
    url = BASE + path
    if params:
        q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        url += ('?' + q)
    headers = {'User-Agent': 'OpenClaw-Inkwell/1.0'}
    if auth and API_KEY:
        headers['agent-auth-api-key'] = API_KEY
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        body = None
    r = urllib.request.Request(url, headers=headers, data=body, method=method)
    with urllib.request.urlopen(r, timeout=30) as resp:
        print(resp.read().decode('utf-8'))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('home')

    a = sub.add_parser('articles')
    a.add_argument('--category')
    a.add_argument('--search')
    a.add_argument('--limit', type=int, default=10)
    a.add_argument('--cursor')
    a.add_argument('--sort', default='date')

    d = sub.add_parser('article')
    d.add_argument('article_id')

    l = sub.add_parser('like')
    l.add_argument('article_id')

    ul = sub.add_parser('unlike')
    ul.add_argument('article_id')

    b = sub.add_parser('bookmarks')

    ab = sub.add_parser('bookmark-add')
    ab.add_argument('article_id')
    ab.add_argument('--note', default='')

    rb = sub.add_parser('bookmark-remove')
    rb.add_argument('article_id')

    sub.add_parser('categories')
    sub.add_parser('sources')
    sub.add_parser('me')

    args = p.parse_args()

    if args.cmd == 'home':
        req('/home')
    elif args.cmd == 'articles':
        req('/articles', params={
            'category': args.category,
            'search': args.search,
            'limit': args.limit,
            'cursor': args.cursor,
            'sort': args.sort,
        }, auth=bool(API_KEY))
    elif args.cmd == 'article':
        req(f'/articles/{args.article_id}')
    elif args.cmd == 'like':
        req(f'/articles/{args.article_id}/like', method='POST')
    elif args.cmd == 'unlike':
        req(f'/articles/{args.article_id}/like', method='DELETE')
    elif args.cmd == 'bookmarks':
        req('/bookmarks')
    elif args.cmd == 'bookmark-add':
        req('/bookmarks', method='POST', data={'article_id': args.article_id, 'note': args.note})
    elif args.cmd == 'bookmark-remove':
        req(f'/bookmarks/{args.article_id}', method='DELETE')
    elif args.cmd == 'categories':
        req('/categories', auth=False)
    elif args.cmd == 'sources':
        req('/sources', auth=False)
    elif args.cmd == 'me':
        req('/agents/me')

if __name__ == '__main__':
    main()
