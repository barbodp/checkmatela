from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
W,H=2400,1700
paper='#FAF8F2';pine='#0F2E22';ink='#15181A';brass='#AD7F3C'
im=Image.new('RGB',(W,H),paper);d=ImageDraw.Draw(im)
ser='/System/Library/Fonts/Supplemental/Didot.ttc'; sans='/System/Library/Fonts/Helvetica.ttc'
def font(path,size):return ImageFont.truetype(path,size)
def place(path,box):
 a=Image.open(path).convert('RGBA');x,y,w,h=box;a.thumbnail((w,h),Image.Resampling.LANCZOS);im.paste(a,(x+(w-a.width)//2,y+(h-a.height)//2),a)
d.rectangle((0,0,W,17),fill=pine)
d.text((105,68),'CHECKMATELA',font=font(ser,83),fill=pine)
d.text((108,157),'THE MARK SYSTEM  /  2026',font=font(sans,23),fill=brass,spacing=7)
d.line((107,211,W-107,211),fill=brass,width=2)
# Primary horizontal
D=(107,260,1515,590);d.rounded_rectangle(D,radius=22,fill='#FFFFFF',outline='#DDD7C9',width=2)
d.text((150,288),'01  PRIMARY LOCKUP',font=font(sans,22),fill=brass)
place(R/'png/primary-horizontal.png',(175,345,1320,230))
# Reverse
D=(107,675,1515,990);d.rounded_rectangle(D,radius=22,fill=pine)
d.text((150,704),'02  REVERSE',font=font(sans,22),fill='#D9B876')
place(R/'png/primary-horizontal-reverse.png',(150,742,1390,225))
# Badge right
D=(1580,260,2293,990);d.rounded_rectangle(D,radius=22,fill='#EDE7D8')
d.text((1622,288),'03  SEAL',font=font(sans,22),fill=brass)
place(R/'png/seal.png',(1620,348,636,610))
# Bottom strip
D=(107,1050,742,1575);d.rounded_rectangle(D,radius=22,fill='#FFFFFF',outline='#DDD7C9',width=2)
d.text((145,1084),'04  MASCOT MARK',font=font(sans,22),fill=brass)
place(R/'png/symbol-color.png',(275,1150,300,315))
D=(786,1050,1421,1575);d.rounded_rectangle(D,radius=22,fill='#FFFFFF',outline='#DDD7C9',width=2)
d.text((823,1084),'05  SMALL ICON',font=font(sans,22),fill=brass)
place(R/'png/favicon.png',(947,1160,300,300))
D=(1465,1050,2293,1575);d.rounded_rectangle(D,radius=22,fill='#EDE7D8')
d.text((1503,1084),'06  POSTCARD APPLICATION',font=font(sans,22),fill=brass)
place(R/'examples/postcard-front.png',(1506,1170,746,348))
d.text((107,1633),'ONE CHARACTER. ONE WORDMARK. MANY PLACES TO REMEMBER IT.',font=font(sans,23),fill=pine)
im.save(R/'brand-board.png',optimize=True)
