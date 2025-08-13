from pathlib import Path

from docx import Document
from docx.enum.text import WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
from docx.styles.style import ParagraphStyle
from docx.text.run import Run

from step_1_1 import OUT_DIR 
OUT_3_1 = OUT_DIR / f"{Path(__file__).stem}.docx"


def apply_font(arg: Run | ParagraphStyle, face: str = "Malgun Gothic", size_pt: int = None, is_bold: bool = None, rgb: str = None):
    if face is not None:
        arg.font.name = face 
        for prop in ["asciiTheme", "cstheme", "eastAsia", "eastAsiaTheme", "hAnsiTheme"]:
            arg.element.rPr.rFonts.set(qn(f"w:{prop}"), face) 
    if size_pt is not None:
        arg.font.size = Pt(size_pt)  
    if is_bold is not None:
        arg.font.bold = is_bold  
    if rgb is not None:
        arg.font.color.rgb = RGBColor.from_string(rgb) 


def init_docx():
    doc = Document() 
    section = doc.sections[0] 
    section.page_width, section.page_height = Mm(210), Mm(297) 
    section.top_margin = section.bottom_margin = Mm(20) 
    section.left_margin = section.right_margin = Mm(12.7) 
    style = doc.styles["Normal"] 
    p_format = style.paragraph_format  
    p_format.space_before = p_format.space_after = 0  
    p_format.line_spacing_rule = WD_LINE_SPACING.SINGLE 
    apply_font(style, size_pt=10)  
    doc.save(OUT_3_1)  


if __name__ == "__main__":
    init_docx()