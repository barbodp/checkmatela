from pathlib import Path
from runpy import run_path
R=Path(__file__).resolve().parents[1]
b=run_path(str(R/'source/build.py'))
PINE=b['PINE'];PAPER=b['PAPER'];BRASS=b['BRASS'];INK=b['INK']
mark=b['mark'];word=b['word'];tag=b['tag'];svg=b['svg']
O=R/'examples';O.mkdir(exist_ok=True)
# Six-by-four postcard art, 1800 x 1200 pixels at export. Allow printer-specific bleed.
checkers=''.join(f'<rect x="{i*30}" y="0" width="30" height="30" fill="{INK if i%2 else PAPER}"/>' for i in range(60))
front=f'''<rect width="1800" height="1200" fill="{PAPER}"/>{checkers}
<path d="M120 139H1680" stroke="{BRASS}" stroke-width="2"/>
{mark(93,209,3.36)}
{word(760,647,1.20)}{tag(765,739,1.37)}
<path d="M123 1030H1677" stroke="{BRASS}" stroke-width="2"/>
<text x="125" y="1100" fill="{PINE}" font-family="Helvetica Neue,Arial,sans-serif" font-size="26" letter-spacing="8">THE ART OF THE NEXT MOVE</text>
<text x="1678" y="1100" text-anchor="end" fill="{PINE}" font-family="Helvetica Neue,Arial,sans-serif" font-size="26" letter-spacing="5">CHECKMATELA.COM</text>'''
(O/'postcard-front.svg').write_text(svg(1800,1200,'Checkmatela postcard front',front))
back=f'''<rect width="1800" height="1200" fill="{PAPER}"/><rect width="636" height="1200" fill="{PINE}"/>
{mark(144,118,1.68,PAPER,'#D9B876')}
<path d="M98 600H538" stroke="#D9B876" stroke-width="2"/>
<text x="98" y="702" fill="{PAPER}" font-family="Didot,Baskerville,serif" font-size="74">Every move,</text>
<text x="98" y="792" fill="{PAPER}" font-family="Didot,Baskerville,serif" font-size="74">considered.</text>
<text x="98" y="1090" fill="#D9B876" font-family="Helvetica Neue,Arial,sans-serif" font-size="25" letter-spacing="6">CHECKMATELA.COM</text>
{word(728,245,1.27)}<path d="M731 304H1687" stroke="{BRASS}" stroke-width="2"/>
<text x="731" y="459" fill="{PINE}" font-family="Didot,Baskerville,serif" font-size="93">Made for the moment.</text>
<text x="731" y="561" fill="{INK}" font-family="Helvetica Neue,Arial,sans-serif" font-size="31">Formal wear for the entrance, the promise,</text>
<text x="731" y="608" fill="{INK}" font-family="Helvetica Neue,Arial,sans-serif" font-size="31">and everything worth remembering.</text>
<path d="M731 727H1687" stroke="{BRASS}" stroke-width="2"/>
<text x="731" y="830" fill="{PINE}" font-family="Helvetica Neue,Arial,sans-serif" font-size="27" letter-spacing="6">EXPLORE THE COLLECTION</text>
<text x="731" y="910" fill="{PINE}" font-family="Didot,Baskerville,serif" font-size="57">checkmatela.com</text>
<rect x="731" y="1055" width="25" height="25" fill="{PINE}"/><rect x="756" y="1055" width="25" height="25" fill="{PAPER}" stroke="{PINE}"/><rect x="781" y="1055" width="25" height="25" fill="{PINE}"/><rect x="806" y="1055" width="25" height="25" fill="{PAPER}" stroke="{PINE}"/>'''
(O/'postcard-back.svg').write_text(svg(1800,1200,'Checkmatela postcard back',back))
print('Built postcard examples')
