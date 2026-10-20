from pathlib import Path
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw

root = Path(__file__).resolve().parents[1]
out = root / "output/project2"
qa = root / "tmp/pdfs/project2"
qa.mkdir(parents=True, exist_ok=True)
path = out / "Laporan_BAB_4_sampai_7.pdf"
pdf = pdfium.PdfDocument(str(path))
text = PdfReader(path)
thumbs=[]
for i,page in enumerate(pdf):
    im=page.render(scale=1.5).to_pil().convert("RGB")
    im.save(qa/f"page-{i+1:02}.png")
    t=ImageOps.contain(im,(298,421))
    tile=Image.new("RGB",(310,448),"#dddddd")
    tile.paste(t,((310-t.width)//2,8))
    ImageDraw.Draw(tile).text((12,431),str(i+1),fill="black")
    thumbs.append(tile)
    s=text.pages[i].extract_text()
    print(i+1,len(s),s[:90].replace("\n"," | "))
for batch in range((len(thumbs)+7)//8):
    sheet=Image.new("RGB",(1240,896),"white")
    for j,t in enumerate(thumbs[batch*8:(batch+1)*8]):
        sheet.paste(t,((j%4)*310,(j//4)*448))
    sheet.save(qa/f"contact-{batch+1}.jpg")
print("Total pages:",len(pdf))
