"""Build the one-page EMBA course plan with the course's HEC visual identity."""
from pathlib import Path
import subprocess

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "tmp/pdfs/emba"
BUILD.mkdir(parents=True, exist_ok=True)
OUTPUT = Path(__file__).with_suffix(".pdf")

for weight in ("Light", "Regular", "SemiBold", "Bold"):
    font = f"FiraSans-{weight}"
    pfb = subprocess.check_output(["kpsewhich", font + ".pfb"], text=True).strip()
    if not pfb:
        raise RuntimeError(f"Missing course font: {font}")
    afm = BUILD / (font + ".afm")
    with afm.open("w") as handle:
        subprocess.run(["t1rawafm", pfb], stdout=handle, check=True)
    metrics = afm.read_text()
    if "\nFamilyName " not in metrics:
        afm.write_text(metrics.replace("StartFontMetrics 2.0\n", "StartFontMetrics 2.0\nFamilyName Fira Sans\n"))
    face = pdfmetrics.EmbeddedType1Face(str(afm), pfb)
    pdfmetrics.registerTypeFace(face)
    pdfmetrics.registerFont(pdfmetrics.Font(font, face.name, "WinAnsiEncoding"))

pdfmetrics.registerFontFamily("FiraSans-Light", normal="FiraSans-Light", bold="FiraSans-SemiBold")
pdfmetrics.registerFontFamily("FiraSans-Regular", normal="FiraSans-Regular", bold="FiraSans-SemiBold")

NAVY = HexColor("#002855")
GREEN = HexColor("#26D07C")
TEXT = HexColor("#2D3748")
GRAY = HexColor("#64748B")
PALE = HexColor("#F1F5F9")
LINE = HexColor("#DEE5ED")
PAGE_W, PAGE_H = 612, 792
LEFT, RIGHT = 49, 45
WIDTH = PAGE_W - LEFT - RIGHT

styles = {
    "title": ParagraphStyle("title", fontName="FiraSans-Bold", fontSize=23.5, leading=27.5, textColor=NAVY),
    "body": ParagraphStyle("body", fontName="FiraSans-Light", fontSize=10.8, leading=14.0, textColor=TEXT),
    "small": ParagraphStyle("small", fontName="FiraSans-Light", fontSize=10.0, leading=13.0, textColor=TEXT),
    "section": ParagraphStyle("section", fontName="FiraSans-SemiBold", fontSize=11.5, leading=14.5, textColor=NAVY),
    "theme": ParagraphStyle("theme", fontName="FiraSans-SemiBold", fontSize=11.0, leading=14.0, textColor=NAVY),
    "meta": ParagraphStyle("meta", fontName="FiraSans-Regular", fontSize=9.2, leading=12.0, textColor=GRAY),
}

canvas = Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
canvas.setTitle("L’environnement macroéconomique au cœur des décisions stratégiques")
canvas.setAuthor("Jean-Félix Brouillette")
canvas.setSubject("Plan de séance - EMBA, HEC Montréal - Janvier 2027")
canvas.setCreator("HEC Montréal - EMBA")
canvas.setFillColor(NAVY)
canvas.rect(0, 0, 8, PAGE_H, fill=1, stroke=0)
canvas.setFillColor(GREEN)
canvas.rect(8, 0, 2, PAGE_H, fill=1, stroke=0)

boxes = []


def para(text, top, x=LEFT, width=WIDTH, style="body"):
    item = Paragraph(text, styles[style])
    _, height = item.wrap(width, PAGE_H)
    item.drawOn(canvas, x, PAGE_H - top - height)
    boxes.append((x, top, x + width, top + height, text[:70]))
    return top + height


def section(text, top):
    return para(text, top, style="section") + 5


canvas.setFont("FiraSans-Bold", 10)
canvas.setFillColor(NAVY)
canvas.drawString(LEFT, PAGE_H - 40, "HEC MONTRÉAL  |  EMBA")
canvas.setFont("FiraSans-Regular", 8.5)
canvas.setFillColor(GRAY)
canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 40, "PLAN DE SÉANCE")

y = para("L’environnement macroéconomique<br/>au cœur des décisions stratégiques", 52, style="title")
y = para("Jean-Félix Brouillette  |  Janvier 2027  |  Durée : 3 heures", y + 8, style="meta")
canvas.setFillColor(GREEN)
canvas.rect(LEFT, PAGE_H - y - 10, 74, 2.2, fill=1, stroke=0)
y += 22

y = para(
    "Relier l’actualité canadienne et internationale aux décisions stratégiques à travers trois thèmes "
    "et trois cliniques sectorielles. <b>Fil conducteur : l’analyse de scénarios et la veille économique</b> "
    "pour expliciter les hypothèses, comparer les réponses et définir les signaux de révision.", y)

y = section("Objectifs d’apprentissage", y + 12)
objectives = [
    "<b>Interpréter</b> la conjoncture à l’aide des modèles macroéconomiques et des indicateurs pertinents.",
    "<b>Analyser</b> les effets directs et indirects des chocs sur son industrie et son organisation.",
    "<b>Comparer</b> les risques, occasions d’affaires et réponses stratégiques selon différents scénarios.",
    "<b>Formuler</b> une recommandation, ses hypothèses et les indicateurs à suivre pour la réévaluer.",
]
for text in objectives:
    canvas.setFillColor(GREEN)
    canvas.circle(LEFT + 2.5, PAGE_H - y - 6.6, 1.7, fill=1, stroke=0)
    y = para(text, y, x=LEFT + 12, width=WIDTH - 12) + 2.0

y = section("Ouverture : portrait de la conjoncture", y + 10)
y = para(
    "Bref rappel de l’offre et de la demande agrégées (AD-AS), du marché du travail et du marché "
    "du capital, puis lecture de la conjoncture à l’aide de ces trois cadres. Le diagnostic et les "
    "perspectives seront actualisés avant la séance.", y)

y = section("Trois thèmes, trois cliniques sectorielles", y + 10)
themes = [
    (
        "Fragmentation commerciale et incertitude géopolitique",
        "Tensions commerciales, droits de douane, devises et chaînes d’approvisionnement. "
        "Conséquences pour l’accès aux marchés, la localisation et la diversification. "
        "Arbitrage entre efficacité et résilience.",
        "Comparer deux scénarios commerciaux pour une industrie : effets sur ses clients, fournisseurs "
        "et concurrents, réponse stratégique et indicateur à surveiller.",
    ),
    (
        "Inflation, taux d’intérêt et endettement",
        "Demande, coûts et réaction des autorités économiques. Endettement des ménages, entreprises "
        "et gouvernements, vulnérabilités financières et implications pour les prix, l’investissement "
        "et les liquidités.",
        "Évaluer une industrie sous deux scénarios de demande ou de financement. Identifier ses "
        "fragilités, une réponse et un signal qui déclencherait sa révision.",
    ),
    (
        "Productivité canadienne, IA et transformations structurelles",
        "Défi de productivité au Canada : investissement, adoption technologique et environnement "
        "d’affaires. Effets de l’IA sur le travail, la concurrence et le partage des gains de productivité.",
        "Comparer deux trajectoires de gains de productivité dans une industrie. Proposer un "
        "investissement ou un positionnement et les indicateurs permettant de l’ajuster.",
    ),
]
for idx, (title, content, clinic) in enumerate(themes, 1):
    if idx > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.5)
        canvas.line(LEFT, PAGE_H - y - 3, PAGE_W - RIGHT, PAGE_H - y - 3)
        y += 11
    canvas.setFillColor(NAVY)
    canvas.roundRect(LEFT, PAGE_H - y - 20, 21, 21, 4, fill=1, stroke=0)
    canvas.setFillColor(white)
    canvas.setFont("FiraSans-SemiBold", 10)
    canvas.drawCentredString(LEFT + 10.5, PAGE_H - y - 14.5, str(idx))
    y = para(title, y, x=LEFT + 31, width=WIDTH - 31, style="theme") + 4
    y = para(content, y, x=LEFT + 31, width=WIDTH - 31) + 4
    y = para(f'<font color="#002855"><b>Clinique {idx}.</b></font> {clinic}', y,
             x=LEFT + 31, width=WIDTH - 31, style="small")

y += 13
method = (
    "<b>Modalités.</b> Équipes stables de 3 ou 4. Chaque clinique porte sur l’industrie d’un membre, "
    "en favorisant la rotation. La recommandation précise hypothèses, expositions, compromis "
    "et indicateurs de veille.<br/>"
    "<b>Déroulement.</b> Rappels et conjoncture&nbsp;: 30&nbsp;min. Trois blocs de 40&nbsp;min&nbsp;: discussion (20), "
    "clinique (15) et restitution (5). Pause&nbsp;: 10&nbsp;min. Synthèse et application individuelle&nbsp;: 20&nbsp;min."
)
method_para = Paragraph(method, styles["small"])
_, method_h = method_para.wrap(WIDTH - 24, PAGE_H)
canvas.setFillColor(PALE)
canvas.roundRect(LEFT, PAGE_H - y - method_h - 18, WIDTH, method_h + 18, 6, fill=1, stroke=0)
canvas.setFillColor(GREEN)
canvas.roundRect(LEFT, PAGE_H - y - method_h - 18, 3, method_h + 18, 1.5, fill=1, stroke=0)
y = para(method, y + 9, x=LEFT + 12, width=WIDTH - 24, style="small") + 9

if y > 742:
    raise RuntimeError(f"Content exceeds the one-page content area: {y:.1f} pt")

canvas.setStrokeColor(LINE)
canvas.setLineWidth(0.6)
canvas.line(LEFT, 32, PAGE_W - RIGHT, 32)
canvas.setFont("FiraSans-Regular", 8)
canvas.setFillColor(GRAY)
canvas.drawString(LEFT, 19, "EMBA  |  Environnement macroéconomique et stratégie")
canvas.drawRightString(PAGE_W - RIGHT, 19, "Janvier 2027")
canvas.showPage()
canvas.save()

reader = PdfReader(OUTPUT)
assert len(reader.pages) == 1
text = reader.pages[0].extract_text()
for required in ["Objectifs", "Clinique 1.", "Clinique 2.", "Clinique 3.", "Janvier 2027", "Jean-Félix",
                 "AD-AS", "marché du travail", "marché du capital", "veille économique",
                 "Endettement", "productivité au Canada", "deux scénarios", "deux trajectoires"]:
    assert required in text, required
for x0, y0, x1, y1, label in boxes:
    assert 0 <= x0 < x1 <= PAGE_W and 0 <= y0 < y1 <= 742, label
(BUILD / "extracted.txt").write_text(text)
print(f"Created {OUTPUT}\nPages: 1\nContent bottom: {y:.1f} pt\nExtracted words: {len(text.split())}")
