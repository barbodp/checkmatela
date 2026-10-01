from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
W,H=2600,1900
paper='#FAF8F2';pine='#0F2E22';brass='#AD7F3C';ink='#15181A';white='#FFFFFF'
im=Image.new('RGB',(W,H),paper);d=ImageDraw.Draw(im)
ser='/System/Library/Fonts/Supplemental/Didot.ttc';sans='/System/Library/Fonts/Helvetica.ttc'
def F(path,size):return ImageFont.truetype(path,size)
def paste(name,box):
 p=R/name;a=Image.open(p).convert('RGBA');x,y,w,h=box;a.thumbnail((w,h),Image.Resampling.LANCZOS);im.paste(a,(x+(w-a.width)//2,y+(h-a.height)//2),a)
def label(x,y,s,color=brass):d.text((x,y),s,font=F(sans,23),fill=color)
# Editorial top rail
d.rectangle((0,0,W,17),fill=pine)
d.text((130,70),'CHECKMATELA',font=F(ser,100),fill=pine)
d.text((1820,120),'THE NEXT MOVE   /   IDENTITY SYSTEM 02',font=F(sans,24),fill=brass)
d.line((130,225,2470,225),fill=brass,width=2)
# Main lockup on ivory
label(135,273,'01   PRIMARY LOCKUP')
paste('png/primary-horizontal.png',(150,344,1400,245))
d.line((130,632,1560,632),fill='#D8CEBC',width=2)
# Reverse bar
d.rectangle((130,690,1560,955),fill=pine)
label(167,723,'02   REVERSE',color='#D9B876')
paste('png/primary-horizontal-reverse.png',(185,768,1320,145))
# Large mark panel, no gimmicks
d.rectangle((1625,266,2470,955),fill=pine)
label(1665,300,'THE LIFTED SQUARE',color='#D9B876')
paste('png/favicon.png',(1780,370,550,520))
# Application rail
d.line((130,1015,2470,1015),fill=brass,width=2)
label(130,1040,'03   THE MARK IN USE')
# Seal
d.rectangle((130,1115,680,1690),fill='#EFEADD')
label(159,1142,'SEAL / STAMP')
paste('png/seal.png',(186,1215,445,445))
# Cards
d.rectangle((725,1115,1570,1690),fill=white)
label(752,1142,'POSTCARD FRONT')
paste('examples/postcard-front.png',(756,1214,784,431))
d.rectangle((1615,1115,2470,1690),fill=white)
label(1644,1142,'POSTCARD BACK')
paste('examples/postcard-back.png',(1645,1214,795,431))
# Footer / color notation
d.line((130,1760,2470,1760),fill=brass,width=2)
d.text((130,1793),'ONE MARK. ONE WORDMARK. A SQUARE READY FOR THE NEXT MOVE.',font=F(sans,25),fill=pine)
for i,c in enumerate((pine,ink,paper,brass)):
 x=2206+i*62;d.rectangle((x,1790,x+44,1834),fill=c,outline=pine,width=2)
im.save(R/'brand-board.png',optimize=True)
