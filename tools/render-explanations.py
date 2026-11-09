"""Render public reasoning sections and interview notes from editable JSON.

Run from any directory: python tools/render-explanations.py
Uses only the Python standard library. It replaces its own comment-delimited
blocks and preserves each existing case's screenshots, branding and other text.
"""
from pathlib import Path
from html import escape
import json,re

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'content'/'explanations'
BASE='https://jaydensong0401.github.io/'

def text(value):
    if value is None:return ''
    if isinstance(value,str):return value
    if isinstance(value,list):return ' / '.join(text(v) for v in value)
    if isinstance(value,dict):return ' · '.join(text(v) for v in value.values())
    return str(value)

def inline(value):
    s=escape(text(value))
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    return s

def paragraphs(value):
    return ''.join('<p>'+inline(p)+'</p>' for p in text(value).split('\n\n') if p.strip())

def items(values):
    if not values:return ''
    if not isinstance(values,list):values=[values]
    return '<ul>'+''.join('<li>'+inline(v)+'</li>' for v in values)+'</ul>'

def block_replace(html,name,content,before=None):
    start='<!-- portfolio:'+name+':start -->';end='<!-- portfolio:'+name+':end -->'
    block=start+'\n'+content+'\n'+end
    pattern=re.escape(start)+r'.*?'+re.escape(end)
    if re.search(pattern,html,re.S):return re.sub(pattern,lambda _:block,html,count=1,flags=re.S)
    if before and before in html:return html.replace(before,block+'\n'+before,1)
    raise ValueError('No insertion target for '+name)

def first_section(html,anchor):
    match=re.search(r'<section\b[^>]*\bid=[\"\']'+re.escape(anchor)+r'[\"\'][^>]*>',html)
    if not match:raise ValueError('Missing existing case anchor: '+anchor)
    return match.group(0)

def public_section(p):
    cards=[]
    for i,s in enumerate(p['publicSections'],1):
        cards.append('<article class="ex-problem"><div class="ex-problem-top"><span>문제 '+str(i)+'</span><h3>'+inline(s['title'])+'</h3></div>'
          +'<div class="ex-story"><h4>문제와 원인</h4>'+paragraphs(s['problem'])+paragraphs(s['cause'])+'</div>'
          +'<div class="ex-story"><h4>선택한 해결과 이유</h4>'+paragraphs(s['decision'])+paragraphs(s['why'])+'</div>'
          +'<div class="ex-story"><h4>감수한 점</h4>'+paragraphs(s['tradeoff'])+'</div>'
          +'<div class="ex-evidence"><h4>확인한 근거</h4>'+paragraphs(s['evidence'])+'<h4>다음 확인</h4>'+paragraphs(s['nextCheck'])+'</div></article>')
    return '<section class="reasoning-section" id="problem-solving"><div class="ex-wrap"><header class="ex-section-head"><div><span class="ex-kicker">PROBLEM · DECISION · EVIDENCE</span><h2>문제를 정의하고,<br>해결의 기준을 정한 과정.</h2></div><a class="ex-link" href="../interview/'+p['id']+'/">이 프로젝트 면접 설명 노트 ↗</a></header><div class="ex-problems">'+''.join(cards)+'</div><p class="ex-reading-note">프로젝트의 동작·설계 근거와 실제 사용 효과는 구분해 설명합니다.</p></div></section>'

def prep_head(title,description,url,icon,prefix):
    apple=Path(icon).parent.as_posix()+'/apple-touch-icon.png'
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><meta name="description" content="'+escape(description)+'"><link rel="canonical" href="'+url+'"><meta name="theme-color" content="#245f4b"><link rel="icon" href="'+icon+'?v=20261109"><link rel="apple-touch-icon" href="'+apple+'?v=20261109"><link rel="stylesheet" href="'+prefix+'assets/explanations.css"><script src="'+prefix+'assets/interview.js" defer></script></head>'

def prep_footer(prefix):
    return '<footer class="prep-footer ex-wrap"><a href="'+prefix+'">Jayden Song · 전체 포트폴리오</a><span>설명 기록 · 확인한 근거를 기준으로 계속 보완합니다.</span></footer>'

def interview_page(p):
    n=p['interview'];prefix='../../';icon=prefix+'assets/brands/'+p['favicon'];logo=prefix+'assets/brands/'+p['logo']
    h=prep_head(p['name']+' · 면접 설명 노트','문제 정의와 설계 판단, 확인한 근거를 설명하는 '+p['name']+' 면접 준비 자료.',BASE+'interview/'+p['id']+'/',icon,prefix)
    h+='<body class="prep-page"><a class="ex-skip" href="#main">본문으로 이동</a><header class="prep-header ex-wrap"><a class="prep-brand" href="../../'+p['id']+'/"><img src="'+logo+'" alt="'+escape(p['name'])+' 현재 로고"><span>'+escape(p['name'])+'</span></a><nav aria-label="설명 노트 메뉴"><a href="../../'+p['id']+'/#problem-solving">문제·해결 사례</a><a href="../">전체 준비 노트</a><button type="button" data-print>인쇄 / PDF</button></nav></header><main id="main" class="ex-wrap"><section class="prep-hero"><span class="ex-kicker">PROJECT INTERVIEW NOTES</span><h1>'+escape(p['name'])+'<br><em>문제와 판단을 설명하는 준비.</em></h1><p>어떤 문제를 다뤘고, 무엇을 선택했으며, 어디까지 확인했는지 설명하는 연습 자료입니다.</p><div class="prep-quicklinks"><a href="#intro">1분 설명</a><a href="#walkthrough">3분 설명 순서</a><a href="#questions">예상 질문 '+str(len(n['questions']))+'개</a><a href="#role">역할·근거 확인</a></div><p class="prep-note">답변 초안입니다. 개인 담당·개발 기간·성과 수치는 실제 수행 경험과 증빙으로 확정해 사용하세요.</p></section>'
    h+='<section class="prep-section" id="intro"><div class="prep-section-title"><span>01 / SHORT STORY</span><h2>약 1분으로 소개하기.</h2></div><div class="prep-script">'+paragraphs(n['intro60'])+'</div></section>'
    h+='<section class="prep-section" id="walkthrough"><div class="prep-section-title"><span>02 / WALKTHROUGH</span><h2>약 3분으로 작업 과정을 설명하기.</h2></div><ol class="prep-walkthrough">'
    for step in n['walkthrough']:
        if isinstance(step,dict):
            h+='<li><h3>'+inline(step.get('focus',step.get('step','설명 순서')))+'</h3>'+paragraphs(step.get('talk',step.get('description','')))+('<p class="prep-evidence">근거 · '+inline(step['evidence'])+'</p>' if step.get('evidence') else '')+'</li>'
        else:h+='<li>'+paragraphs(step)+'</li>'
    h+='</ol><div class="prep-links"><a href="../../'+p['id']+'/">사례를 열어 설명하기 ↗</a><a href="../../screens/#'+p['id']+'">화면 자료와 연결하기 ↗</a></div></section>'
    h+='<section class="prep-section" id="questions"><div class="prep-section-title prep-question-title"><div><span>03 / QUESTIONS & ANSWERS</span><h2>판단의 이유를 묻는 질문.</h2></div><button type="button" data-answer-toggle aria-pressed="false">답변 가리고 연습하기</button></div><div class="prep-questions">'
    for i,q in enumerate(n['questions'],1):
        h+='<details open class="prep-question"><summary><span>Q'+str(i)+'</span>'+inline(q['question'])+'</summary><div class="prep-answer">'+paragraphs(q['answer'])+('<div class="prep-answer-evidence"><strong>함께 제시할 근거</strong>'+paragraphs(q['evidence'])+'</div>' if q.get('evidence') else '')+'</div></details>'
    h+='</div></section><section class="prep-section" id="role"><div class="prep-section-title"><span>04 / ROLE & EVIDENCE</span><h2>내 역할과 확인한 범위를 구체화하기.</h2></div><div class="prep-role">'+paragraphs(n['role'])+'</div><div class="prep-two"><section><h3>면접 전에 확인할 것</h3>'+items(n['checks'])+'</section><section><h3>다음 보강 자료</h3>'+items(n['improvements'])+'</section></div></section><section class="prep-next"><h2>설명은 실제 화면과 근거로 이어집니다.</h2><div class="prep-links"><a href="../../'+p['id']+'/#problem-solving">문제·해결 사례로 돌아가기 ↗</a><a href="../">다른 프로젝트 준비하기 ↗</a></div><p>기록 기준 '+escape(p.get('updated','2026-11-09'))+' · 이후 확인한 담당 범위와 검증 결과에 따라 보완합니다.</p></section></main>'+prep_footer(prefix)+'</body></html>'
    return h

def hub(projects):
    h=prep_head('프로젝트별 면접 설명 노트 | Jayden Song',str(len(projects))+'개 프로젝트의 문제 정의·설계 선택·검증 범위와 면접 질문을 준비하는 설명 노트.',BASE+'interview/','../assets/favicon.svg','../')
    h+='<body class="prep-page"><a class="ex-skip" href="#main">본문으로 이동</a><header class="prep-header ex-wrap"><a class="prep-brand" href="../">Jayden Song <small>PORTFOLIO</small></a><nav><a href="../">전체 프로젝트</a><a href="../screens/">전체 화면</a></nav></header><main class="ex-wrap" id="main"><section class="prep-hero"><span class="ex-kicker">EXPLAIN THE WORK</span><h1>프로젝트를,<br><em>나의 판단으로 설명하기.</em></h1><p>기능 소개를 넘어 문제의 원인, 선택한 이유, 감수한 점과 확인한 근거를 정리했습니다.</p><p class="prep-note">짧게 소개하기 → 작업 과정 설명 → 예상 질문 연습 → 담당 역할·증빙 확인 순서로 준비할 수 있습니다.</p></section><div class="prep-projects">'
    for p in projects:
        h+='<article><div class="prep-project-label">'+escape(p['group'])+'</div><h2><img src="../assets/brands/'+p['favicon']+'" alt="" aria-hidden="true">'+escape(p['name'])+'</h2><p>'+escape(p['summary'])+'</p><small>문제·해결 '+str(len(p['publicSections']))+'건 · 예상 질문 '+str(len(p['interview']['questions']))+'개</small><div class="prep-links"><a href="'+p['id']+'/">면접 설명 준비 ↗</a><a href="../'+p['id']+'/#problem-solving">문제·해결 사례 ↗</a></div></article>'
    h+='</div></main>'+prep_footer('../')+'</body></html>'
    return h

def main():
    index=json.loads((DATA/'index.json').read_text(encoding='utf-8'))
    projects=[]
    for meta in index['projects']:
        p=json.loads((DATA/(meta['id']+'.json')).read_text(encoding='utf-8'));p.update(meta);projects.append(p)
        source=ROOT/p['id']/'index.html';html=source.read_text(encoding='utf-8')
        if 'assets/explanations.css' not in html:html=html.replace('</head>','<link rel="stylesheet" href="../assets/explanations.css"></head>',1)
        content=public_section(p)
        if '<!-- portfolio:reasoning:start -->' in html:html=block_replace(html,'reasoning',content)
        else:html=block_replace(html,'reasoning',content,before=first_section(html,p['insertBefore']))
        source.write_text(html,encoding='utf-8')
        target=ROOT/'interview'/p['id']/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(interview_page(p),encoding='utf-8')
    (ROOT/'interview'/'index.html').write_text(hub(projects),encoding='utf-8')
    homepage=ROOT/'index.html';html=homepage.read_text(encoding='utf-8')
    if 'assets/explanations.css' not in html:html=html.replace('</head>','<link rel="stylesheet" href="assets/explanations.css"></head>',1)
    nav=re.search(r'<nav\b[^>]*aria-label="주 메뉴"[^>]*>.*?</nav>',html,re.S)
    if nav and 'interview/' not in nav.group(0):html=html[:nav.start()]+nav.group(0).replace('</nav>','<a href="interview/">설명·면접 준비</a></nav>')+html[nav.end():]
    intro='<section class="ex-hub-banner"><div class="ex-wrap"><div><span class="ex-kicker">EXPLAIN THE WORK</span><h2>문제의 원인부터,<br>선택의 이유와 근거까지.</h2><p>각 사례의 문제·해결 과정을 읽고 프로젝트별 면접 설명 노트로 이어갈 수 있습니다.</p></div><a class="ex-link" href="interview/">프로젝트별 면접 준비 노트 ↗</a></div></section>'
    html=block_replace(html,'prep-hub',intro,before='</main>');homepage.write_text(html,encoding='utf-8')
    sitemap=ROOT/'sitemap.xml';xml=sitemap.read_text(encoding='utf-8')
    modified={'':index['updated'],'interview/':index['updated']}
    for p in projects:
        modified[p['id']+'/']=p.get('updated',index['updated'])
        modified['interview/'+p['id']+'/']=p.get('updated',index['updated'])
    for route,date in modified.items():
        loc='<loc>'+BASE+route+'</loc>'
        if loc not in xml:xml=xml.replace('</urlset>','<url>'+loc+'<lastmod>'+date+'</lastmod></url></urlset>')
        else:xml=re.sub('(<url>\\s*'+re.escape(loc)+r'\s*<lastmod>)[^<]*(</lastmod>)',lambda m:m.group(1)+date+m.group(2),xml)
    sitemap.write_text(xml,encoding='utf-8')
    print('Rendered',len(projects),'reasoning sections and',len(projects)+1,'interview pages.')

if __name__=='__main__':main()
