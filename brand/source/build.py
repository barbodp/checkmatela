from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
SVG=ROOT/'svg'; SVG.mkdir(exist_ok=True)
_, c_path=(ROOT/'source/monogram-c-path.txt').read_text().splitlines()[:2]
_, word_path=(ROOT/'source/wordmark-path.txt').read_text().splitlines()[:2]
_, tag_path=(ROOT/'source/tagline-path.txt').read_text().splitlines()[:2]
PINE='#0F2E22'; PAPER='#FAF8F2'; BRASS='#AD7F3C'; INK='#15181A'

def svg(w,h,title,body):
 return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n'
def save(name,w,h,body,title):
 (SVG/name).write_text(svg(w,h,title,body))
def mark(x=0,y=0,s=1,color=PINE,tile=BRASS):
 return f'<g transform="translate({x} {y}) scale({s})"><path d="{c_path}" fill="{color}" transform="translate(14 184)"/><rect x="153" y="72" width="20" height="20" fill="{tile}"/></g>'
def word(x,y,s=1,color=PINE):
 return f'<path d="{word_path}" transform="translate({x} {y}) scale({s})" fill="{color}"/>'
def tag(x,y,s=1,color=BRASS):
 return f'<path d="{tag_path}" transform="translate({x} {y}) scale({s})" fill="{color}"/>'

save('symbol-color.svg',210,220,mark(), 'Checkmatela lifted-square monogram')
save('symbol-one-color.svg',210,220,mark(color=PINE,tile=PINE),'Checkmatela single-ink monogram')
save('wordmark.svg',785,135,word(22,111),'Checkmatela wordmark')
save('primary-horizontal.svg',1160,230,mark(11,17,.82)+word(194,139,1.23)+tag(200,194,1),'Checkmatela primary logo')
save('primary-horizontal-reverse.svg',1160,230,mark(11,17,.82,PAPER,'#D9B876')+word(194,139,1.23,PAPER)+tag(200,194,1,'#D9B876'),'Checkmatela reverse logo')
save('compact-horizontal.svg',970,205,mark(4,8,.78)+word(190,132,1.0),'Checkmatela compact website logo')
save('compact-horizontal-reverse.svg',970,205,mark(4,8,.78,PAPER,'#D9B876')+word(190,132,1.0,PAPER),'Checkmatela compact reverse logo')
save('stacked.svg',820,520,mark(279,14,1.25)+word(32,402,1.02)+tag(252,462,1),'Checkmatela stacked logo')
seal=f'''<circle cx="310" cy="310" r="284" fill="none" stroke="{PINE}" stroke-width="4"/><circle cx="310" cy="310" r="270" fill="none" stroke="{BRASS}" stroke-width="1.4"/>{mark(191,88,1.13)}<path d="M119 390H501" stroke="{BRASS}" stroke-width="1.5"/>{word(111,460,.54)}{tag(183,515,.8)}'''
save('seal.svg',620,620,seal,'Checkmatela editorial seal')
# The favicon retains the exact lifted-square relationship with stronger contrast on a pine tile.
favicon=f'<rect width="128" height="128" fill="{PINE}"/>'+mark(5,1,.55,PAPER,'#D9B876')
save('favicon.svg',128,128,favicon,'Checkmatela favicon')
print('Built',len(list(SVG.glob('*.svg'))),'SVG masters')
