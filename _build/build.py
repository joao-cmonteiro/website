#!/usr/bin/env python3
"""Rebuild index.html, research.html, discussions.html, cv.html from _build/site.json.
Run from anywhere:  python3 _build/build.py
Edit _build/site.json (papers, discussions, coauthor links), then rerun."""
import json, html, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, '_build', 'site.json'), encoding='utf-8'))
C = S['coauthor_links']

def ext(u):
    return ' target=_blank rel=noopener' if u.startswith('http') else ''

def authors(a):
    for n, u in C.items():
        a = a.replace(n, f'<a href="{u}" target="_blank" rel="noopener">{n}</a>')
    return a

def card(p):
    bib = open(os.path.join(ROOT, p['bib']), encoding='utf-8').read().strip() if p.get('bib') else None
    lk = ''.join(f'<a href="{l["url"]}"{ext(l["url"])}>{l["label"]}</a>' for l in p['links'])
    tg = ('<button class="tg" data-p="ab" aria-expanded="false">Abstract</button>' if p['abstract'] else '') + \
         ('<button class="tg" data-p="cite" aria-expanded="false">Cite</button>' if bib else '')
    panels = (f'<div class="panel ab"><p>{p["abstract"]}</p></div>' if p['abstract'] else '') + \
             (f'<div class="panel cite"><div class="bib"><button class="copy">Copy</button><pre>{html.escape(bib)}</pre></div></div>' if bib else '')
    md = ('<div class="media">Media: ' + ' · '.join(f'<a href="{m["url"]}" target="_blank" rel="noopener">{m["label"]}</a>' for m in p['media']) + '</div>') if p['media'] else ''
    f = p.get('figure')
    fig = (f'<figure class="figwrap"><button class="fig" aria-label="Enlarge figure"><img src="{f}" alt="{html.escape(p["caption"])}" loading="lazy"></button><figcaption>{p["caption"]}</figcaption></figure>') if f else ''
    auth = 'with ' + authors(p['coauthors']) + (f', {p["year"]}' if p.get('year') else '')
    return f'<article class="card{"" if f else " nofig"}">{fig}<div class="body"><h3>{p["title"]}</h3><div class="auth">{auth}</div><div class="links">{lk}{tg}</div>{panels}{md}</div></article>'

def page(cur, title, body, desc):
    nav = ''.join(f'<li><a href="{h}"{" class=cur aria-current=page" if k == cur else ""}>{n}</a></li>' for k, h, n in
                  [('home', 'index.html', 'Home'), ('research', 'research.html', 'Research'), ('discussions', 'discussions.html', 'Discussions'), ('cv', 'cv.html', 'CV')])
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://joao-cmonteiro.github.io/website/img/photo.jpg">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="stylesheet" href="style.css">
</head>
<body>
<nav class="nav"><a class="nm" href="index.html">Joao Monteiro</a><ul>{nav}</ul></nav>
<main>
{body}
</main>
<footer>Joao Monteiro · Einaudi Institute for Economics and Finance · Via Sallustiana 62, 00187 Rome</footer>
<div class="lb" hidden><img alt=""></div>
<script src="site.js"></script>
</body>
</html>
'''

desc = 'Joao Monteiro, Assistant Professor at the Einaudi Institute for Economics and Finance (EIEF). Corporate finance, international economics, macroeconomics, and the economics of conflict.'
home = open(os.path.join(ROOT, '_build', 'home.html'), encoding='utf-8').read().strip()

sections = []
for p in S['papers']:
    if p['section'] not in sections: sections.append(p['section'])
research = ''.join(f'<h2{" class=\"sub\"" if i else ""}>{s}</h2>' + ''.join(card(p) for p in S['papers'] if p['section'] == s) for i, s in enumerate(sections))

years = sorted({d['year'] for d in S['discussions']}, reverse=True)
disc = '<h2>Discussions</h2>' + ''.join(
    f'<section class="dgroup"><h3 class="dyear">{y}</h3><div>' +
    ''.join(f'<article class="disc"><h3>{d["title"]}</h3><div class="auth">by {d["authors"]}</div><div class="venue">{d["venue"]}</div><div class="links"><a href="{d["slides"]}">Slides</a></div></article>' for d in S['discussions'] if d['year'] == y) +
    '</div></section>' for y in years)

cv = '''<div class="cvbar"><h2>CV</h2><a class="btn" href="cv.pdf" download>Download PDF</a></div>
<object class="cvframe" data="cv.pdf#view=FitH" type="application/pdf" aria-label="CV">
<p class="fallback">Your browser can’t show the CV here. <a href="cv.pdf">Open the CV (PDF)</a>.</p>
</object>'''

out = {'index.html': page('home', 'Joao Monteiro — EIEF', home, desc),
       'research.html': page('research', 'Research — Joao Monteiro', research, desc),
       'discussions.html': page('discussions', 'Discussions — Joao Monteiro', disc, desc),
       'cv.html': page('cv', 'CV — Joao Monteiro', cv, desc)}
for n, c in out.items():
    open(os.path.join(ROOT, n), 'w', encoding='utf-8').write(c)
print('Built:', ', '.join(out))
