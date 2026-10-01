from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
exec((ROOT/'source/build.py').read_text().replace("print('Built',len(list(SVG.glob('*.svg'))),'SVG logos')",''))
OUT=ROOT/'examples';OUT.mkdir(exist_ok=True)
def save_example(name,body):
 (OUT/name).write_text(shell(1800,1200,body,'Checkmatela postcard example'))
# Editable 6 x 4 inch examples, no address or postage fields so they remain useful for campaign adaptation.
checker=''.join(f'<rect x="{i*48}" y="0" width="48" height="48" fill="{INK if i%2 else PAPER}"/>' for i in range(38))
front=f'''<rect width="1800" height="1200" fill="{PAPER}"/>{checker}<rect y="1152" width="1800" height="48" fill="{PINE}"/><path d="M170 270H1630M170 975H1630" stroke="{BRASS}" stroke-width="3"/>
<g transform="translate(540 164) scale(1.2)">{seal}</g>
<text x="900" y="1058" text-anchor="middle" font-family="Helvetica Neue,Arial,sans-serif" font-size="34" letter-spacing="11" fill="{PINE}">MAKE YOUR MOVE.</text>'''
# The seal embedded above is 600 units and shifted/scaled to center.
save_example('postcard-front.svg',front)
back=f'''<rect width="1800" height="1200" fill="{PAPER}"/><rect x="0" width="720" height="1200" fill="{PINE}"/>
<g transform="translate(70 150) scale(.63)">{icon(1.12,14,5)}{wordmark(PAPER,1.03,213,124)}{tagline('#D9B876',.72,216,175)}</g>
<text x="90" y="528" font-family="Didot,Baskerville,serif" font-size="96" fill="{PAPER}">Every move,</text><text x="90" y="624" font-family="Didot,Baskerville,serif" font-size="96" fill="{PAPER}">considered.</text>
<path d="M90 682H600" stroke="{BRASS}" stroke-width="4"/><text x="90" y="775" font-family="Helvetica Neue,Arial,sans-serif" font-size="31" fill="{PAPER}">FORMAL WEAR FOR THE MOMENTS</text><text x="90" y="820" font-family="Helvetica Neue,Arial,sans-serif" font-size="31" fill="{PAPER}">THAT STAY WITH YOU.</text>
<text x="90" y="1100" font-family="Helvetica Neue,Arial,sans-serif" font-size="28" letter-spacing="5" fill="#D9B876">CHECKMATELA.COM</text>
<text x="820" y="260" font-family="Didot,Baskerville,serif" font-size="78" fill="{PINE}">Find your next move.</text>
<text x="820" y="355" font-family="Helvetica Neue,Arial,sans-serif" font-size="34" fill="{INK}">Tailoring for an entrance, a promise,</text><text x="820" y="408" font-family="Helvetica Neue,Arial,sans-serif" font-size="34" fill="{INK}">and every celebration in between.</text>
<path d="M820 510H1680" stroke="{BRASS}" stroke-width="3"/>
<text x="820" y="605" font-family="Helvetica Neue,Arial,sans-serif" font-size="30" letter-spacing="4" fill="{PINE}">EXPLORE THE COLLECTION</text>
<text x="820" y="665" font-family="Didot,Baskerville,serif" font-size="54" fill="{INK}">checkmatela.com</text>
<rect x="820" y="895" width="52" height="52" fill="{PINE}"/><rect x="872" y="895" width="52" height="52" fill="{PAPER}" stroke="{PINE}"/><rect x="924" y="895" width="52" height="52" fill="{PINE}"/><rect x="976" y="895" width="52" height="52" fill="{PAPER}" stroke="{PINE}"/>
'''
save_example('postcard-back.svg',back)
