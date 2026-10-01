import Foundation
import CoreText
import CoreGraphics
let args=CommandLine.arguments
let font = CTFontCreateWithName(args[1] as CFString, CGFloat(Double(args[2])!), nil)
let attrs:[NSAttributedString.Key:Any]=[NSAttributedString.Key(kCTFontAttributeName as String):font,NSAttributedString.Key(kCTKernAttributeName as String):Double(args[3])!]
let line=CTLineCreateWithAttributedString(NSAttributedString(string:args[4],attributes:attrs))
var all=""
for run in CTLineGetGlyphRuns(line) as! [CTRun] {
 let n=CTRunGetGlyphCount(run)
 var glyphs=Array(repeating:CGGlyph(),count:n), pos=Array(repeating:CGPoint.zero,count:n)
 CTRunGetGlyphs(run,CFRangeMake(0,0),&glyphs); CTRunGetPositions(run,CFRangeMake(0,0),&pos)
 for i in 0..<n {
  guard let path=CTFontCreatePathForGlyph(font,glyphs[i],nil) else {continue}
  let x=pos[i].x,y=pos[i].y
  path.applyWithBlock { ptr in
   let e=ptr.pointee
   func pt(_ p:CGPoint)->String {String(format:"%.2f %.2f",p.x+x,-p.y-y)}
   switch e.type {
   case .moveToPoint:all += "M"+pt(e.points[0])
   case .addLineToPoint:all += "L"+pt(e.points[0])
   case .addQuadCurveToPoint:all += "Q"+pt(e.points[0])+" "+pt(e.points[1])
   case .addCurveToPoint:all += "C"+pt(e.points[0])+" "+pt(e.points[1])+" "+pt(e.points[2])
   case .closeSubpath:all += "Z"
   @unknown default:break
   }
  }
 }
}
print(String(format:"%.2f",CTLineGetTypographicBounds(line,nil,nil,nil)))
print(all)
