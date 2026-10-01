from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]
SVG=ROOT/'svg'; SVG.mkdir(exist_ok=True)
word_width, word_path=(ROOT/'source/wordmark-path.txt').read_text().splitlines()[:2]
tag_width, tag_path=(ROOT/'source/tagline-path.txt').read_text().splitlines()[:2]
INK='#15181A'; PINE='#0F2E22'; BRASS='#AD7F3C'; BURG='#7A2036'; PAPER='#FAF8F2'; SKIN='#F4E4CB'

def shell(w,h,body,title):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title>{body}</svg>\n'''

def mascot(mono=False):
 if mono:
  return f'''<g fill="none" stroke="{PINE}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
   <path d="M61 28 L61 13 L69 20 L80 6 L91 20 L99 13 L99 28 Z" fill="{PINE}"/><path d="M69 28H91"/>
   <ellipse cx="80" cy="68" rx="36" ry="38"/><circle cx="93" cy="66" r="11"/><path d="M103 70 C111 83 106 96 100 109"/>
   <path d="M61 57 Q67 53 72 57 M88 56 Q94 53 99 57 M68 78 Q80 89 93 77"/><circle cx="68" cy="66" r="1.8" fill="{PINE}"/><circle cx="93" cy="66" r="1.8" fill="{PINE}"/>
   <path d="M58 102 C41 106 30 118 29 151 Q80 165 131 151 C130 118 117 106 102 102 L80 139 Z"/>
   <path d="M57 105 L80 139 L65 123 L60 133 M103 105 L80 139 L95 123 L100 133"/>
   <path d="M72 113L80 119L88 113L80 116Z" fill="{PINE}"/><path d="M60 153H100"/>
  </g>'''
 return f'''<g stroke-linejoin="round" stroke-linecap="round">
  <path d="M61 28 L61 13 L69 20 L80 6 L91 20 L99 13 L99 28 Z" fill="{BRASS}" stroke="{PINE}" stroke-width="2.5"/><path d="M68 28 H92" stroke="{PINE}" stroke-width="2.5"/>
  <ellipse cx="80" cy="68" rx="37" ry="39" fill="{SKIN}" stroke="{INK}" stroke-width="3.2"/>
  <path d="M51 51 C56 37 68 34 76 35" fill="none" stroke="white" stroke-width="3" opacity=".65"/>
  <path d="M59 57 Q66 53 72 57 M88 57 Q95 53 101 57" fill="none" stroke="{INK}" stroke-width="2.2"/>
  <ellipse cx="68" cy="66" rx="2.3" ry="3" fill="{INK}"/><ellipse cx="93" cy="66" rx="2.3" ry="3" fill="{INK}"/>
  <path d="M67 79 Q80 90 95 77" fill="none" stroke="{INK}" stroke-width="2.7"/>
  <circle cx="93" cy="66" r="11" fill="none" stroke="{BRASS}" stroke-width="3.1"/><path d="M103 70 C111 82 108 96 101 107" fill="none" stroke="{BRASS}" stroke-width="2"/>
  <path d="M58 102 C39 105 29 120 29 153 Q80 167 131 153 C131 120 118 105 102 102 L80 136 Z" fill="{INK}" stroke="{INK}" stroke-width="2.5"/>
  <path d="M67 105 L80 140 L93 105 Z" fill="{PAPER}"/>
  <path d="M57 105 L80 139 L65 121 L58 131 Z M103 105 L80 139 L95 121 L102 131 Z" fill="{PINE}"/>
  <path d="M57 105 L80 139 M103 105 L80 139" fill="none" stroke="{BRASS}" stroke-width="1" opacity=".8"/>
  <path d="M70 111 L80 116 L70 122 Z M90 111 L80 116 L90 122 Z" fill="{BURG}" stroke="{PAPER}" stroke-width="1"/><circle cx="80" cy="116" r="3.2" fill="{BURG}"/>
  <path d="M110 131 L119 129 L119 137 L110 136 Z" fill="{PINE}" stroke="{PAPER}" stroke-width="1"/><circle cx="80" cy="147" r="2.2" fill="{BRASS}"/>
  <path d="M60 154 Q80 160 100 154" fill="none" stroke="{BRASS}" stroke-width="2"/>
 </g>'''

def wordmark(fill=PINE, scale=1, x=0, y=0):
 return f'<path d="{word_path}" fill="{fill}" transform="translate({x} {y}) scale({scale})"/>'
def tagline(fill=BRASS,scale=1,x=0,y=0):
 return f'<path d="{tag_path}" fill="{fill}" transform="translate({x} {y}) scale({scale})"/>'
def icon(scale=1,x=0,y=0,mono=False):
 return f'<g transform="translate({x} {y}) scale({scale})">{mascot(mono)}</g>'
def save(name,w,h,body,title): (SVG/name).write_text(shell(w,h,body,title))

save('symbol-color.svg',160,180,mascot(),'Checkmatela mascot symbol')
save('symbol-one-color.svg',160,180,mascot(True),'Checkmatela one-color mascot symbol')
save('wordmark.svg',700,115,wordmark(PINE,1,16,101),'Checkmatela wordmark')
save('primary-horizontal.svg',1000,215,icon(1.12,14,5)+wordmark(PINE,1.03,213,124)+tagline(BRASS,.72,216,175),'Checkmatela primary logo')
save('primary-horizontal-reverse.svg',1000,215,f'<rect width="1000" height="215" fill="{PINE}"/><rect x="11" y="9" width="180" height="192" rx="90" fill="{PAPER}"/>'+icon(1.12,13,6)+wordmark(PAPER,1.03,213,124)+tagline('#D9B876',.72,216,175),'Checkmatela primary logo on pine')
save('compact-horizontal.svg',940,180,icon(.98,0,0)+wordmark(PINE,1.03,178,115),'Checkmatela compact logo')
save('compact-horizontal-reverse.svg',940,180,f'<rect width="940" height="180" fill="{PINE}"/><rect x="0" y="0" width="157" height="180" rx="78" fill="{PAPER}"/>'+icon(.98,0,0)+wordmark(PAPER,1.03,178,115),'Checkmatela compact logo on pine')
save('stacked.svg',780,495,icon(1.55,266,16)+wordmark(PINE,1.08,32,370)+tagline(BRASS,.88,224,426),'Checkmatela stacked logo')
# Seal: one centered symbol and letterforms, same palette and line language.
seal=f'''<circle cx="300" cy="300" r="282" fill="{PAPER}" stroke="{PINE}" stroke-width="12"/><circle cx="300" cy="300" r="263" fill="none" stroke="{BRASS}" stroke-width="2"/><path d="M75 177H525M75 443H525" stroke="{BRASS}" stroke-width="2"/>{icon(1.65,168,171)}{wordmark(PINE,.58,108,149)}{tagline(BRASS,.66,174,491)}<rect x="279" y="452" width="14" height="14" fill="{PINE}"/><rect x="293" y="452" width="14" height="14" fill="{PAPER}" stroke="{PINE}" stroke-width=".8"/><rect x="307" y="452" width="14" height="14" fill="{PINE}"/>'''
save('seal.svg',600,600,seal,'Checkmatela seal')
# Very small icon removes fine garment detail and keeps the crown, smile, monocle, and bow.
fav=f'''<rect width="128" height="128" rx="24" fill="{PINE}"/><path d="M39 28V12L48 19L64 5L80 19L89 12V28Z" fill="{BRASS}"/><ellipse cx="64" cy="61" rx="34" ry="35" fill="{SKIN}"/><circle cx="77" cy="60" r="10" fill="none" stroke="{BRASS}" stroke-width="3"/><circle cx="51" cy="60" r="2.5" fill="{INK}"/><circle cx="77" cy="60" r="2.5" fill="{INK}"/><path d="M50 74Q64 85 79 73" fill="none" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/><path d="M25 128C29 102 42 92 52 91L64 109L76 91C91 94 101 106 104 128Z" fill="{INK}"/><path d="M50 94L64 111L78 94" fill="none" stroke="{PAPER}" stroke-width="4"/><path d="M55 95L64 100L55 105ZM73 95L64 100L73 105Z" fill="{BURG}"/>'''
save('favicon.svg',128,128,fav,'Checkmatela favicon')
print('Built',len(list(SVG.glob('*.svg'))),'SVG logos')
