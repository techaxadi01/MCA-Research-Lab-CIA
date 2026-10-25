import docx
from docx.shared import Inches, Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION_START
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
import os
import lxml.etree as ET
from latex2mathml.converter import convert
from docx2pdf import convert as docx2pdf_convert

# Initialize MathML to OMML XSLT converter
xslt_path = r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'
xslt = ET.parse(xslt_path)
transform = ET.XSLT(xslt)

def latex_to_omml(latex_str):
    mml = convert(latex_str)
    dom = ET.fromstring(mml)
    omml = transform(dom)
    return parse_xml(ET.tostring(omml).decode())

def set_cell_margins(cell, top=50, bottom=50, left=50, right=50):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_border(cell, **kwargs):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = parse_xml(f'<{tag} xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
                                f'w:val="{edge_data.get("val", "single")}" '
                                f'w:sz="{edge_data.get("sz", 4)}" '
                                f'w:space="0" '
                                f'w:color="{edge_data.get("color", "000000")}"/>')
            tcBorders.append(element)
    tcPr.append(tcBorders)

def build_paper():
    # Load official IEEE conference A4 transitional template
    template_path = 'conference-template-a4-transitional.docx'
    doc = docx.Document(template_path)
    body = doc._body._element

    # Clear dummy content from template body, retaining clean styles
    for child in list(body):
        if not child.tag.endswith('sectPr'):
            body.remove(child)

    # ---------------- SECTION 0: TITLE & AUTHORS (1 COLUMN) ----------------
    # 1. Paper Title
    p_title = doc.add_paragraph(style='paper title')
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r1 = p_title.add_run("Spatio-Temporal Detection and Biogeochemical Profiling of ")
    r_sp = p_title.add_run("Noctiluca scintillans")
    r_sp.font.italic = True
    r2 = p_title.add_run(" Blooms in the Arabian Sea Using Multispectral Imagery and Hydrodynamic Reanalysis")

    # 2. Author Block (2 Authors Side-by-Side in IEEE Format)
    tbl_auth = doc.add_table(rows=1, cols=2)
    tbl_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_auth.autofit = False

    # Zero borders for author table
    tblPr = tbl_auth._tbl.tblPr
    tblBorders = parse_xml(
        '<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>'
        '<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    tblPr.append(tblBorders)

    authors_data = [
        {
            "name": "Aditya Kumar",
            "dept": "Department of Computer Science",
            "inst": "CHRIST (Deemed to be University)",
            "city": "Bengaluru, India",
            "email": "aditya.kumar@mca.christuniversity.in"
        },
        {
            "name": "Chandra J",
            "dept": "Department of Computer Science",
            "inst": "CHRIST (Deemed to be University)",
            "city": "Bengaluru, India",
            "email": "chandra.j@christuniversity.in"
        }
    ]

    for col_idx, auth in enumerate(authors_data):
        cell = tbl_auth.cell(0, col_idx)
        cell.width = Inches(3.4)
        p = cell.paragraphs[0]
        p.style = doc.styles['Author']
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.05
        
        r_name = p.add_run(auth["name"] + "\n")
        r_name.font.name = 'Times New Roman'
        r_name.font.size = Pt(11)
        
        r_dept = p.add_run(auth["dept"] + "\n")
        r_dept.font.name = 'Times New Roman'
        r_dept.font.size = Pt(10)
        r_dept.font.italic = True
        
        r_inst = p.add_run(auth["inst"] + "\n")
        r_inst.font.name = 'Times New Roman'
        r_inst.font.size = Pt(10)
        r_inst.font.italic = True
        
        r_city = p.add_run(auth["city"] + "\n")
        r_city.font.name = 'Times New Roman'
        r_city.font.size = Pt(10)
        
        r_email = p.add_run(auth["email"])
        r_email.font.name = 'Times New Roman'
        r_email.font.size = Pt(10)

    # Continuous Section Break into Two Columns for Main Body
    sec1 = doc.add_section(WD_SECTION_START.CONTINUOUS)
    sec1.page_width = Mm(210)
    sec1.page_height = Mm(297)
    sec1.top_margin = Inches(0.75)
    sec1.bottom_margin = Inches(1.0)
    sec1.left_margin = Inches(0.63)
    sec1.right_margin = Inches(0.63)
    cols1 = sec1._sectPr.find(qn('w:cols'))
    if cols1 is None:
        cols1 = OxmlElement('w:cols')
        sec1._sectPr.append(cols1)
    cols1.set(qn('w:num'), '2')
    cols1.set(qn('w:space'), '360')

    # Helper function for adding body text paragraphs with rich formatting runs
    def add_body_p(content="", space_before=0, space_after=4.0):
        p = doc.add_paragraph(style='Body Text')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        if isinstance(content, str) and content:
            r = p.add_run(content)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)
        elif isinstance(content, (list, tuple)):
            for item in content:
                if isinstance(item, str):
                    r = p.add_run(item)
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(10)
                elif isinstance(item, (tuple, list)):
                    text = item[0]
                    italic = item[1] if len(item) > 1 else False
                    sub = item[2] if len(item) > 2 else False
                    sup = item[3] if len(item) > 3 else False
                    bold = item[4] if len(item) > 4 else False
                    r = p.add_run(text)
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(10)
                    r.font.italic = bool(italic)
                    if sub:
                        r.font.subscript = True
                    if sup:
                        r.font.superscript = True
                    if bold:
                        r.font.bold = True
        return p

    def add_h1(title):
        # Heading 1 style in template automatically adds Roman numeral and small caps
        p = doc.add_paragraph(title, style='Heading 1')
        p.paragraph_format.keep_with_next = True
        return p

    def add_h2(title):
        # Heading 2 style in template automatically adds letter and italics
        p = doc.add_paragraph(title, style='Heading 2')
        p.paragraph_format.keep_with_next = True
        return p

    def add_eq(formula, eq_num):
        # Single column equation table: 3.38 inches total width
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        
        # zero borders
        tblPr = tbl._tbl.tblPr
        tblBorders = parse_xml(
            '<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>'
            '<w:insideH w:val="none"/><w:insideV w:val="none"/>'
            '</w:tblBorders>'
        )
        tblPr.append(tblBorders)
        
        c0 = tbl.cell(0, 0)
        c1 = tbl.cell(0, 1)
        c0.width = Inches(2.95)
        c1.width = Inches(0.43)
        
        # Zero cell padding
        for cell in (c0, c1):
            tcPr = cell._tc.get_or_add_tcPr()
            tcMar = OxmlElement('w:tcMar')
            for m in ['top', 'bottom', 'left', 'right']:
                node = OxmlElement(f'w:{m}')
                node.set(qn('w:w'), '0')
                node.set(qn('w:type'), 'dxa')
                tcMar.append(node)
            tcPr.append(tcMar)
        
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.paragraph_format.space_before = Pt(1.5)
        p0.paragraph_format.space_after = Pt(1.5)
        p0._p.append(latex_to_omml(formula))
        
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_before = Pt(1.5)
        p1.paragraph_format.space_after = Pt(1.5)
        r = p1.add_run(f"({eq_num})")
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        return tbl

    def add_where(runs_data):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0.5)
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.02
        if isinstance(runs_data, str):
            runs_data = [runs_data]
        for item in runs_data:
            if isinstance(item, str):
                r = p.add_run(item)
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.0)
            elif isinstance(item, (tuple, list)):
                text = item[0]
                italic = item[1] if len(item) > 1 else False
                sub = item[2] if len(item) > 2 else False
                sup = item[3] if len(item) > 3 else False
                bold = item[4] if len(item) > 4 else False
                r = p.add_run(text)
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.0)
                r.font.italic = bool(italic)
                if sub:
                    r.font.subscript = True
                if sup:
                    r.font.superscript = True
                if bold:
                    r.font.bold = True
        return p

    # ---------------- SECTION 1: TWO-COLUMN BODY CONTENT ----------------
    # Abstract
    p_abs = doc.add_paragraph(style='Abstract')
    r_absh = p_abs.add_run("Abstract—")
    r_absh.font.bold = True
    r_absh.font.italic = True
    r_abst = p_abs.add_run(
        "In recent years, large recurring winter blooms of the green dinoflagellate "
    )
    r_abst_sp = p_abs.add_run("Noctiluca scintillans")
    r_abst_sp.font.italic = True
    r_abst_post = p_abs.add_run(
        " in the northern Arabian Sea have created major environmental concerns by replacing traditional diatom populations, "
        "lowering dissolved oxygen levels, and harming coastal fisheries. Detecting and tracking these blooms using satellites is "
        "challenging because standard empirical ocean color algorithms struggle to identify mixotrophic cells that contain green "
        "endosymbionts (Pedinomonas noctilucae). In addition, regular satellite images only show surface 2D views without accounting "
        "for deeper water mixing and weather conditions. In this paper, we present an integrated Earth observation and data processing "
        "pipeline that combines multispectral satellite imagery (MODIS-Aqua, VIIRS, and OLCI) with ocean physical data from Copernicus "
        "Marine Service (CMEMS) and meteorological reanalysis from ECMWF ERA5. We use narrow-band remote sensing reflectance (Rrs) ratios "
        "at 531 nm and 510 nm along with a multilayer neural network atmospheric correction (NN-V) to accurately identify Noctiluca cells "
        "and recover satellite images affected by high solar zenith angles. To analyze long-term patterns, we apply Cochrane-Orcutt "
        "autoregression and generalized least squares across multi-band reflectance over a 20-year period, separating genuine ecological "
        "trends from background environmental noise. This framework gives coastal managers a practical diagnostic tool that connects "
        "surface satellite observations with ocean mixing and dust deposition, supporting marine conservation goals under UN Sustainable "
        "Development Goal 14."
    )

    # Keywords
    p_kw = doc.add_paragraph(style='Keywords')
    r_kwh = p_kw.add_run("Keywords—")
    r_kwh.font.bold = True
    r_kwh.font.italic = True
    r_kwt = p_kw.add_run(
        "Noctiluca scintillans, Ocean Color Remote Sensing, Remote Sensing Reflectance, Bio-Optical Inversion, Arabian Sea, Environmental Time-Series."
    )

    # I. INTRODUCTION
    add_h1("Introduction")

    add_body_p([
        "The seasonal reversal of monsoon winds strongly controls ocean physics, chemistry, and biological productivity across the "
        "northern Indian Ocean [2], [3]. During the winter northeast monsoon (from December to March), cold dry winds cool the sea surface "
        "and cause evaporative cooling, which makes surface waters sink and drives convective mixing in the northern Arabian Sea [12]. "
        "This mixing brings essential nutrients such as dissolved nitrate and silicate from deeper layers into the sunlit surface zone. "
        "Historically, these nutrient-rich waters supported large seasonal blooms of diatoms, which served as the primary food source for "
        "copepods and commercial fish species while helping transfer organic carbon to the ocean floor [11]. Over the past twenty years, "
        "however, ship surveys and satellite observations show that the ecosystem is undergoing a major shift: natural diatom communities "
        "are increasingly being replaced by massive blooms of the green dinoflagellate ",
        ("Noctiluca scintillans", True, False, False, False),
        " [1], [15]. Unlike the red variety of ",
        ("Noctiluca", True, False, False, False),
        ", green ",
        ("Noctiluca", True, False, False, False),
        " contains millions of photosynthetic green algae endosymbionts (",
        ("Pedinomonas noctilucae", True, False, False, False),
        "). This allows the organism to grow both by using sunlight for photosynthesis and by actively eating remaining diatoms and microscopic zooplankton [13]. "
        "Because common marine copepods avoid eating ",
        ("Noctiluca", True, False, False, False),
        " due to its large size and cellular ammonia buildup, the bloom biomass is not transferred up the food chain to fish, but instead goes to jellyfish and salps. "
        "When these massive blooms die and sink, bacterial decay consumes large amounts of oxygen, causing severe coastal hypoxia that kills fish and damages coral reefs, conflicting with UN Sustainable Development Goal 14 [14]."
    ])

    add_body_p([
        "Detecting and monitoring these harmful algal blooms is an important challenge in environmental data science and marine informatics. "
        "Satellite visible sensors offer the only practical way to monitor such large marine regions on a regular basis [7], [19]. "
        "However, current satellite processing workflows suffer from three primary limitations. First, standard empirical ocean color algorithms, "
        "such as NASA's OCx band ratios, assume that all water optical properties depend strictly on chlorophyll-",
        ("a", True, False, False, False),
        " concentration. Mixotrophic green ",
        ("Noctiluca", True, False, False, False),
        ", however, has an unusual pigment spectrum with a distinct reflectance peak at 531 nm and strong light absorption at 510 nm due to its endosymbionts; "
        "as a result, standard algorithms misclassify bloom pixels, underestimate cell numbers, or confuse blooms with coastal sediments [17]. "
        "Second, operational remote sensing pipelines usually treat satellite rasters as flat 2D surface images [10]. Spaceborne optical sensors "
        "can only measure light from the top surface layer (",
        ("Z", True, False, False, False),
        ("pd", True, True, False, False),
        " ≈ 1/",
        ("K", True, False, False, False),
        ("d", True, True, False, False),
        "), meaning they cannot observe subsurface vertical velocities, mixed-layer convective deepening, or oxygen minimum zones that trigger bloom growth [9]. "
        "Third, long-term environmental assessments often rely on single-variable chlorophyll time series, which contain heavy year-to-year natural swings "
        "and strong temporal autocorrelation (red noise), meaning it can take thirty to forty years of data before a genuine climate-driven trend can be separated from background noise [5], [6], [8]."
    ])

    add_body_p([
        "To solve these practical issues, this study develops an integrated computational methodology that connects satellite multi-band reflectance with physical "
        "oceanographic reanalysis data. By reviewing twenty foundational and recent papers across bio-optics, satellite calibration, atmospheric correction, and "
        "time-series statistics, we create an end-to-end framework tailored for the northern Arabian Sea. Our approach applies narrow-band reflectance ratios at ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531) and ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(510) to calculate ",
        ("Noctiluca", True, False, False, False),
        " cell densities [1], uses a multilayer neural network atmospheric correction to restore winter satellite images affected by high solar zenith angles [4], "
        "integrates daily Copernicus Marine Service (CMEMS) hydrodynamic mixing layers [2], and applies multivariate autoregressive regression across visible "
        "spectral bands to detect emerging decadal shifts over a 20-year satellite record [5]."
    ])

    # II. RELATED WORKS
    add_h1("Related Works")

    add_body_p(
        "To build a solid methodology, we organize the literature into four connected areas: (A) Regional Arabian Sea Bloom Dynamics and Hydro-Atmospheric Drivers, "
        "(B) Bio-Optical Remote Sensing and Satellite Inversion Modeling, (C) Satellite Data Calibration and Atmospheric Correction Under Complex Geometry, "
        "and (D) Statistical Trend Detection and Climate Time of Emergence."
    )

    add_h2("Regional Arabian Sea Bloom Dynamics and Hydro-Atmospheric Drivers")

    add_body_p([
        "Pandi et al. [1] carried out field experiments in the northeastern Arabian Sea using water samples and optical data collected from the research vessel FORV ",
        ("Sagar Sampada", True, False, False, False),
        ". They showed that the reflectance band ratio ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531)/",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(510) has a very strong linear correlation (",
        ("R", True, False, False, False),
        ("2", False, False, True, False),
        ("adj", True, True, False, False),
        " = 0.99, ",
        ("p", True, False, False, False),
        " < 10⁻⁴) with ",
        ("Noctiluca", True, False, False, False),
        " cell counts. This happens because the green endosymbionts cause a reflectance peak at 531 nm and carotenoid absorption at 510 nm, making this ratio a "
        "reliable index to track bloom density in both coastal and open waters."
    ])

    add_body_p(
        "Shi and Wang [2] analyzed satellite images from the VIIRS sensor between 2012 and 2019, comparing them with earlier SeaWiFS data and GODAS ocean models. "
        "They found that summer blooms near the western Arabian Sea are driven by strong coastal upwelling and upward Ekman pumping, where vertical water velocities "
        "reach around 1 m/day at 70 m depth. On the other hand, winter blooms in the northern Arabian Sea occur because cold northeast monsoon winds cool the surface "
        "and deepen the mixed layer to about 80 m, bringing nutrients up to the surface."
    )

    add_body_p(
        "Kuttippurath et al. [3] examined primary productivity and chlorophyll changes across the north Indian Ocean from 1998 to 2019 using OC-CCI satellite data, "
        "CMEMS models, and MERRA-2 dust records. They observed that primary productivity decreased by -0.048 mg m⁻³ day⁻¹ per year, while sea surface temperature "
        "increased by +0.02 °C per year. They also noted that wind patterns carrying mineral dust from deserts in the Arabian Peninsula supply iron and phosphorus, "
        "which can trigger algae blooms even without strong upwelling."
    )

    add_body_p([
        "Goes et al. [11] explained the broader climate factors behind the ecological shift in the Arabian Sea. They linked declining winter snow cover over the "
        "Himalayan-Tibetan Plateau to changes in monsoon winds. This reduced winter convective mixing and lowered the amount of dissolved silicate reaching the "
        "surface compared to nitrogen. Because diatoms require silicate to build their cell walls, this imbalance allowed green ",
        ("Noctiluca", True, False, False, False),
        ", which does not need silicate, to multiply rapidly."
    ])

    add_body_p(
        "Lakshmi et al. [12] used CTD instruments and water samples to study the conditions that trigger winter blooms. Using Sverdrup critical depth theory, they "
        "showed that bloom formation happens in two stages: winter cooling first mixes the water column deeply to pull nitrate into the surface layer, and then daytime "
        "sunlight warms the upper layer, making it shallow enough for the photosynthetic endosymbionts to get enough light to grow."
    )

    add_body_p([
        "Asha Devi et al. [13] studied how ",
        ("Noctiluca", True, False, False, False),
        " blooms disrupt the local marine food chain in the northeastern Arabian Sea. Under normal conditions, diatoms are eaten by copepods, which are then eaten by "
        "fish. However, copepods avoid eating ",
        ("Noctiluca", True, False, False, False),
        " because of its large cell size and high ammonia content. As a result, the energy moves into jellyfish, salps, and smaller microzooplankton instead of "
        "commercial fish species."
    ])

    add_body_p([
        "Raj et al. [14] reported on the severe impact of decaying ",
        ("Noctiluca", True, False, False, False),
        " blooms along the southern coast of India. When the large bloom died, bacteria consumed huge amounts of oxygen to break down the cells, causing dissolved "
        "oxygen levels to drop below 1.5 mg/L. This sudden drop in oxygen killed local fish and damaged coral reefs, showing why early satellite detection is critical "
        "for coastal areas."
    ])

    add_body_p([
        "Xiang et al. [15] conducted laboratory incubation experiments off the coast of Pakistan to understand why ",
        ("Noctiluca", True, False, False, False),
        " outcompetes diatoms in winter. They observed that diatoms stop growing once dissolved nutrients like silicate run out. In contrast, green ",
        ("Noctiluca", True, False, False, False),
        " can switch between photosynthesis using its green endosymbionts and directly feeding on remaining diatom cells, allowing it to survive and grow even in "
        "nutrient-poor conditions."
    ])

    add_body_p([
        "Sarma et al. [16] investigated water chemistry and oxygen levels during winter blooms in the northeastern Arabian Sea. By measuring carbon and nitrogen "
        "isotopes along with dissolved oxygen, they proved that blooms start in well-oxygenated surface water (oxygen saturation above 85%) during convective mixing. "
        "Hypoxia only develops later when the dead bloom sinks and decomposes, clarifying that low oxygen is a result of the bloom rather than its cause."
    ])

    add_body_p(
        "Kuttippurath et al. [18] investigated how tropical storms and cyclones affect phytoplankton growth in the north Indian Ocean. Strong cyclonic winds create "
        "intense mixing that pulls cold, nutrient-rich water up from deeper layers, triggering large algal blooms in desert ocean areas. This highlights the importance "
        "of including meteorological events in ocean monitoring systems."
    )

    add_h2("Bio-Optical Remote Sensing and Satellite Inversion Modeling")

    add_body_p([
        "Cael et al. [5] showed that satellite trend analysis can be improved by studying full spectral reflectance rather than only chlorophyll-",
        ("a", True, False, False, False),
        ". Analyzing a 20-year dataset (2002–2022) of MODIS-Aqua images across ten visible channels, and applying the Cochrane-Orcutt method to remove serial "
        "autocorrelation, they detected clear climate-driven trends in about 40% of the world's oceans. Their work proved that multi-band reflectance reveals ecosystem "
        "changes decades sooner than single-variable chlorophyll records."
    ])

    add_body_p([
        "Dutkiewicz et al. [6] used a 3D ocean ecosystem model combined with radiative transfer calculations to predict ocean color changes over the 21st century "
        "under climate change. They showed that reflectance in the blue-green range (around 487–512 nm) has less year-to-year variation than chlorophyll-",
        ("a", True, False, False, False),
        ", allowing earlier detection of climate signals. They also found that shifting levels of organic matter cause standard empirical chlorophyll formulas to lose "
        "accuracy over long periods."
    ])

    add_body_p([
        "Bisson et al. [9] validated satellite particulate backscattering (",
        ("b", True, False, False, False),
        ("bp", False, True, False, False),
        ") products from MODIS, VIIRS, and OLCI by comparing them with 2,486 measurements taken by autonomous Biogeochemical Argo (BGC-Argo) floats at 700 nm. Testing "
        "the GSM, QAA, and GIOP models, they found that the standard GSM model overestimates backscattering by up to 50% in low-to-medium biomass waters because it "
        "assumes a fixed spectral slope (",
        ("γ", True, False, False, False),
        " = 1). In contrast, QAA and GIOP calculate ",
        ("γ", True, False, False, False),
        " dynamically based on blue-to-green ratios, providing much higher accuracy."
    ])

    add_body_p([
        "Loisel et al. [20] developed the LS2 semi-analytical inversion model to calculate seawater absorption (",
        ("a", True, False, False, False),
        ") and particulate backscattering (",
        ("b", True, False, False, False),
        ("bp", False, True, False, False),
        ") from remote sensing reflectance (",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        ") and sun angle without making rigid assumptions about the spectral shape of water constituents. Using Hydrolight simulations and global field data, they "
        "demonstrated high retrieval accuracy (",
        ("R", True, False, False, False),
        ("2", False, False, True, False),
        " > 0.96) in both open ocean and coastal waters, making LS2 a reliable inversion method."
    ])

    add_body_p([
        "Baliarsingh et al. [17] designed an optical classification method using MODIS-Aqua satellite data to distinguish between green mixotrophic ",
        ("Noctiluca", True, False, False, False),
        " and red heterotrophic ",
        ("Noctiluca", True, False, False, False),
        " in the northern Indian Ocean. By examining absorption from prasinoxanthin and chlorophyll-",
        ("b", True, False, False, False),
        ", they showed that green ",
        ("Noctiluca", True, False, False, False),
        " has higher reflectance in green wavelengths (",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531), ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(551)) and lower reflectance in blue (",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(443)), which helps separate it from regular diatom blooms in satellite imagery."
    ])

    add_h2("Satellite Data Calibration and Atmospheric Correction Under Complex Geometry")

    add_body_p([
        "Li et al. [4] evaluated VIIRS satellite reflectance data from 2012 to 2021 against the global OC-CCI dataset, finding that high solar zenith angles (>70°) "
        "severely degrade image quality. Under these conditions, the longer atmospheric path and increased scattering cause standard near-infrared atmospheric "
        "correction to underestimate ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        " by up to 50% (-38.59% bias). They built a single-layer neural network model (NN-V) that reduced the error to -5.27% and increased the amount of usable "
        "winter satellite data nearly twenty times."
    ])

    add_body_p(
        "Sathyendranath et al. [7] described how the ESA Ocean Colour Climate Change Initiative (OC-CCI) creates consistent long-term ocean datasets by merging data "
        "from SeaWiFS, MODIS, MERIS, and VIIRS. They applied QAA-based band-shifting to align wavelengths across different sensors, corrected sensor biases over time, "
        "and used fuzzy logic water classification to compute per-pixel uncertainty values based on real field measurements."
    )

    add_body_p([
        "Castant et al. [10] constructed a global 4D dataset of Photosynthetically Active Radiation (PAR) and diffuse attenuation (",
        ("K", True, False, False, False),
        ("d", True, True, False, False),
        "PAR) from 1958 to 2022 at 0.25° resolution. By combining GlobColour satellite data with the Environmental String Model and ERA5 atmospheric reanalysis "
        "using DINEOF interpolation, they proved that weather model data can be used to accurately estimate underwater light and euphotic depth (",
        ("Z", True, False, False, False),
        ("eu", True, True, False, False),
        ") even for historical periods."
    ])

    add_body_p([
        "Kulk et al. [19] used 20 years of OC-CCI satellite observations to assess global marine primary production. Using photosynthesis-irradiance models calibrated "
        "with field ¹⁴C experiment data, they mapped production across various ocean provinces, showing how large-scale climate variations directly influence marine "
        "productivity over time."
    ])

    add_h2("Statistical Trend Detection and Climate Time of Emergence")

    add_body_p([
        "Hammond et al. [8] developed a spatio-temporal Bayesian model to analyze regional chlorophyll trends and uncertainties using 20 years of OC-CCI satellite "
        "data. Using CMIP5 climate models as Bayesian priors and accounting for spatial distance and AR(1) temporal autocorrelation, they found that while the "
        "global average trend was near zero (0.08 ± 0.35% per year), 18 out of 23 ocean regions showed significant regional trends (±1.8% per year), proving that "
        "global averages hide important local changes."
    ])

    add_h2("Synthesis of Literature and Identification of Research Gaps")

    add_body_p(
        "Reviewing these twenty foundational studies reveals four main technical gaps in existing satellite ocean color workflows:"
    )

    # ---------------- TABLE I: SINGLE COLUMN (3.38 INCHES) ----------------
    p_tcap = doc.add_paragraph('THEMATIC LITERATURE FOUNDATION', style='table head')
    p_tcap.paragraph_format.keep_with_next = True
    p_tcap.paragraph_format.space_before = Pt(6)
    p_tcap.paragraph_format.space_after = Pt(2)

    table = doc.add_table(rows=5, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    headers = ["Thematic Pillar", "Key Citations", "Focal Contribution to Pipeline"]
    table_data = [
        ("A. Arabian Sea Bloom Dynamics & Drivers", 
         "Pandi et al. [1], Shi & Wang [2], Kuttippurath et al. [3], Goes et al. [11], Lakshmi et al. [12], Asha Devi et al. [13], Raj et al. [14], Xiang et al. [15], Sarma et al. [16], Kuttippurath et al. [18]",
         "Quantifies NRR band ratios, MLD deepening (70–80 m), vertical velocities (~1 m/day), Sverdrup critical depth shoaling, trophic disruption, hypoxia (<1.5 mg/L), and dust/storm fertilization."),
        ("B. Bio-Optical Inversion & Discrimination",
         "Cael et al. [5], Dutkiewicz et al. [6], Bisson et al. [9], Loisel et al. [20], Baliarsingh et al. [17]",
         "Provides multivariate remote sensing reflectance framework, dynamic γ calculation in QAA, LS2 semi-analytical inversion (R² > 0.96), and optical discrimination of green Noctiluca via 531 nm reflectance peak."),
        ("C. Radiometric Correction & Datasets",
         "Li et al. [4], Sathyendranath et al. [7], Castant et al. [10], Kulk et al. [19]",
         "Formulates NN-V neural atmospheric correction under high solar zenith angles (SZA > 70°), OC-CCI cross-sensor band-shifting, and 4D PAR/euphotic depth reanalysis interpolation."),
        ("D. Statistical Trend Modeling",
         "Hammond et al. [8], Cael et al. [5], Dutkiewicz et al. [6]",
         "Deploys Cochrane-Orcutt AR(1) autoregression, GLS covariance modeling, and multivariate SNR ≥ 2.0 criteria to isolate secular climate signals from red noise decades ahead of scalar chlorophyll.")
    ]

    col_widths = [Inches(0.95), Inches(0.95), Inches(1.48)]

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        p = hdr_cells[i].paragraphs[0]
        p.style = doc.styles['table col head']
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(1.5)
        for r in p.runs:
            r.font.size = Pt(7.0)
        set_cell_border(hdr_cells[i], top={"sz": 10, "val": "single"}, bottom={"sz": 6, "val": "single"})
        set_cell_margins(hdr_cells[i], top=30, bottom=30, left=25, right=25)

    # Data Rows
    for row_idx, data in enumerate(table_data):
        row_cells = table.rows[row_idx + 1].cells
        for col_idx, text in enumerate(data):
            row_cells[col_idx].text = text
            p = row_cells[col_idx].paragraphs[0]
            p.style = doc.styles['table copy']
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1.0)
            p.paragraph_format.space_after = Pt(1.0)
            for r in p.runs:
                r.font.size = Pt(6.8)
            if col_idx == 0:
                for r in p.runs:
                    r.font.bold = True
            border_bottom = {"sz": 10, "val": "single"} if row_idx == len(table_data) - 1 else {"sz": 4, "val": "single", "color": "D3D3D3"}
            set_cell_border(row_cells[col_idx], bottom=border_bottom)
            set_cell_margins(row_cells[col_idx], top=25, bottom=25, left=25, right=25)

    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Prevent Table I rows from splitting across pages
    for r_i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:cantSplit xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))
        if r_i < len(table.rows) - 1:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True

    # The 4 Research Gaps
    add_body_p([
        ("1. Bio-Optical Spectral Misidentification: ", False, False, False, True),
        "Standard operational algorithms [2], [7] rely on simple blue-green ratios that cannot distinguish mixotrophic dinoflagellates from regular diatoms, "
        "causing false-positive biomass detections during bloom events [1], [17]."
    ], space_before=4)

    add_body_p([
        ("2. Surface Optical and Hydrodynamic Decoupling: ", False, False, False, True),
        "Most satellite studies [1], [5], [17] treat imagery as flat 2D surface layers, without connecting surface features to vertical mixing velocities, "
        "mixed-layer deepening, and thermocline shoaling available from ocean reanalysis models [2], [10], [12]."
    ])

    add_body_p([
        ("3. High Data Loss in Winter: ", False, False, False, True),
        "Winter bloom monitoring in the northern basin loses substantial data when solar zenith angles exceed 70°, as standard atmospheric correction algorithms "
        "fail under long atmospheric paths and dust loads, discarding nearly half of the images [3], [4]."
    ])

    add_body_p([
        ("4. Statistical Masking from Univariate Autocorrelation: ", False, False, False, True),
        "Long-term trend analyses [3], [8] often rely on scalar chlorophyll-",
        ("a", True, False, False, False),
        " time series, where natural year-to-year swings and red-noise autocorrelation hide genuine climate trends that multi-band reflectance can reveal decades "
        "earlier [5], [6]."
    ])

    # III. PROPOSED METHODOLOGY
    add_h1("Proposed Methodology")

    add_body_p(
        "Our proposed computational methodology combines satellite image processing, radiative transfer inversion, neural network atmospheric correction, "
        "and multivariate time-series statistics into a complete pipeline. The workflow consists of four sequential stages, as shown in Fig. 1."
    )

    # ---------------- FIGURE 1: SINGLE COLUMN WIDTH (3.38 INCHES) ----------------
    img_path = 'pipeline_architecture.png'
    if not os.path.exists(img_path) and os.path.exists(os.path.join('Final_Submission', 'pipeline_architecture.png')):
        img_path = os.path.join('Final_Submission', 'pipeline_architecture.png')

    if os.path.exists(img_path):
        p_fig = doc.add_paragraph()
        p_fig.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fig.paragraph_format.space_before = Pt(6)
        p_fig.paragraph_format.space_after = Pt(2)
        p_fig.paragraph_format.keep_with_next = True
        run_f = p_fig.add_run()
        run_f.add_picture(img_path, width=Inches(3.38))
        
        # Figure caption in official 'figure caption' style (automatically adds Fig. 1. in IEEE format)
        p_fcap = doc.add_paragraph(
            "End-to-end architecture of the integrated bio-optical and multivariate reanalysis pipeline.",
            style='figure caption'
        )
        p_fcap.paragraph_format.space_before = Pt(2)
        p_fcap.paragraph_format.space_after = Pt(6)

    add_h2("Stage 1: Data Ingestion and Spatial Grid Harmonization")

    add_body_p(
        "The study area covers the northern Arabian Sea between 10°N and 25°N latitude and 50°E and 75°E longitude [1]. Top-of-atmosphere and surface radiances "
        "are downloaded from Level-2 archives of MODIS-Aqua, VIIRS (SNPP and NOAA-20), and Sentinel-3 OLCI [4], [7]. At the same time, daily physical oceanographic "
        "and meteorological variables are obtained from the Copernicus Marine Service (CMEMS GLOBAL_MULTIYEAR_PHY_001_030) and ECMWF ERA5 reanalyses at 0.25° "
        "resolution. These include sea surface temperature (SST), mixed-layer depth (MLD), vertical velocity (w at 70 m depth), wind stress, and surface photosynthetically "
        "active radiation (PAR) [2], [10]."
    )

    add_body_p(
        "Data harmonization across different satellites and models is implemented in Python using libraries such as xarray, numpy, and netCDF4. Orbital swaths are "
        "reprojected onto a standardized 4 km × 4 km sinusoidal equal-area grid using bilinear interpolation [7]. Quality flags are checked to remove cloudy and "
        "corrupted pixels, including land masking (LAND), cloud and ice flags (CLDICE), high solar zenith angles (HISOLZEN), stray light (STRAYLIGHT), and atmospheric "
        "correction failures (ATMFAIL) [4], [9]."
    )

    add_h2("Stage 2: Radiometric Preprocessing and High-SZA Correction")

    add_body_p([
        "During winter in the northern Arabian Sea, low sun angles frequently result in solar zenith angles greater than 70°, causing standard atmospheric correction "
        "methods to fail. Following the approach of Li et al. [4], we implement a Multilayer Perceptron neural network (NN-V) to process top-of-atmosphere "
        "Rayleigh-corrected radiances (",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ")). The network input features include five visible bands (",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        "(412), ",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        "(443), ",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        "(486), ",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        "(551), ",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        "(671)) along with the sun and sensor viewing angles: solar zenith angle (",
        ("θ", True, False, False, False),
        ("s", True, True, False, False),
        "), satellite viewing zenith angle (",
        ("θ", True, False, False, False),
        ("v", True, True, False, False),
        "), and relative azimuth angle (",
        ("Δφ", True, False, False, False),
        "):"
    ])

    # Equation 1 and Term Meanings
    add_eq(r"\vec{X} = [L_{rc}(412), L_{rc}(443), L_{rc}(486), L_{rc}(551), L_{rc}(671), \cos\theta_s, \cos\theta_v, \Delta\phi]", "1")
    add_where([
        "where ",
        ("X", True, False, False, False),
        " is the neural network input feature vector; ",
        ("L", True, False, False, False),
        ("rc", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ") represents the Rayleigh-corrected top-of-atmosphere radiance across five visible bands (412, 443, 486, 551, and 671 nm); ",
        ("θ", True, False, False, False),
        ("s", True, True, False, False),
        " is the solar zenith angle; ",
        ("θ", True, False, False, False),
        ("v", True, True, False, False),
        " is the satellite viewing zenith angle; and ",
        ("Δφ", True, False, False, False),
        " is the relative azimuth angle between the sun and sensor."
    ])

    add_body_p([
        "The neural network uses a hidden layer with 64 neurons and rectified linear unit (ReLU) activation functions. It is trained on clear-sky matchups to predict "
        "normalized water-leaving reflectance (",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ")) [4]:"
    ])

    # Equation 2 and Term Meanings
    add_eq(r"R_{rs}(\lambda) = f_{\text{NN-V}}(\vec{X})", "2")
    add_where([
        "where ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ") is the water-leaving remote sensing reflectance at wavelength ",
        ("λ", True, False, False, False),
        " (in sr⁻¹); ",
        ("f", True, False, False, False),
        ("NN-V", False, True, False, False),
        " is the function learned by the neural network; and ",
        ("X", True, False, False, False),
        " is the combined input vector of radiances and angles."
    ])

    add_body_p([
        "This neural approach removes atmospheric path scattering, recovering valid ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        " values in winter coastal regions and reducing retrieval bias from -38.59% down to -5.27% [4]."
    ])

    add_h2("Stage 3: Bio-Optical Inversion and Narrow-Band Feature Engineering")

    add_body_p([
        "After atmospheric correction, the reflectance spectra are inverted into inherent optical properties using the Quasi-Analytical Algorithm (QAA v6) [7], [20]. "
        "First, above-water remote sensing reflectance (",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        ") is converted to below-surface reflectance (",
        ("r", True, False, False, False),
        ("rs", False, True, False, False),
        ") [9]:"
    ])

    # Equation 3 and Term Meanings
    add_eq(r"r_{rs}(\lambda) = \frac{R_{rs}(\lambda)}{0.52 + 1.7 R_{rs}(\lambda)}", "3")
    add_where([
        "where ",
        ("r", True, False, False, False),
        ("rs", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ") is the below-surface reflectance just beneath the water surface (sr⁻¹); ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ") is above-water reflectance; and 0.52 and 1.7 are standard empirical air-water transmission constants."
    ])

    add_body_p([
        "The ratio of backscattering to total absorption and backscattering, denoted as ",
        ("u", True, False, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        "), is computed analytically as:"
    ])

    # Equation 4 and Term Meanings
    add_eq(r"u(\lambda) = \frac{-g_0 + \sqrt{(g_0)^2 + 4 g_1 r_{rs}(\lambda)}}{2 g_1}", "4")
    add_where([
        "where ",
        ("u", True, False, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ") is the optical ratio defined as ",
        ("b", True, False, False, False),
        ("bp", False, True, False, False),
        " / (",
        ("a", True, False, False, False),
        " + ",
        ("b", True, False, False, False),
        ("bp", False, True, False, False),
        "); ",
        ("g", True, False, False, False),
        ("0", False, True, False, False),
        " = 0.0895 and ",
        ("g", True, False, False, False),
        ("1", False, True, False, False),
        " = 0.1247 are phase-function constants; and ",
        ("r", True, False, False, False),
        ("rs", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ") is the subsurface reflectance."
    ])

    add_body_p([
        "The particulate backscattering coefficient (",
        ("b", True, False, False, False),
        ("bp", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ")) and non-water absorption (",
        ("a", True, False, False, False),
        ("nw", False, True, False, False),
        ("(", False, False, False, False),
        ("λ", True, False, False, False),
        ")) are then calculated using reference wavelengths at ",
        ("λ", True, False, False, False),
        ("0", False, True, False, False),
        " = 555 nm or 670 nm [9], [20]."
    ])

    add_body_p([
        "To target green ",
        ("Noctiluca scintillans", True, False, False, False),
        " specifically, we calculate two diagnostic optical features based on the experimental findings of Pandi et al. [1] and Baliarsingh et al. [17]:"
    ])

    add_body_p([
        ("1. Noctiluca Reflectance Ratio (NRR):", False, False, False, True)
    ], space_before=2, space_after=1)
    
    # Equation 5 and Term Meanings
    add_eq(r"NRR = \frac{R_{rs}(531)}{R_{rs}(510)}", "5")
    add_where([
        "where ",
        ("NRR", True, False, False, False),
        " is the dimensionless Noctiluca Reflectance Ratio; ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531) measures the endosymbiont backscattering peak; and ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(510) captures carotenoid absorption [1]."
    ])

    add_body_p([
        ("2. Empirical Cell Density Formulation:", False, False, False, True)
    ], space_before=2, space_after=1)
    
    # Equation 6 and Term Meanings
    add_eq(r"N_{\text{cells}} = 89,360 - 72,133 \times \left( \frac{R_{rs}(510)}{R_{rs}(531)} \right)", "6")
    add_where([
        "where ",
        ("N", True, False, False, False),
        ("cells", True, True, False, False),
        " is the estimated green Noctiluca cell density (in cells L⁻¹); 89,360 and 72,133 are calibration coefficients; and ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(510) / ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531) is the inverse band ratio, verified for cell counts above 6,800 cells L⁻¹ in the northern Arabian Sea [1]."
    ])

    add_h2("Stage 4: Multivariate Autoregressive Trend Modeling")

    add_body_p(
        "To check whether recent bloom occurrences represent real long-term climate trends or just normal decadal variations, we apply multivariate "
        "linear regression to the 20-year satellite dataset following Cael et al. [5] and Hammond et al. [8]."
    )

    add_body_p([
        "For every grid cell, the annual median reflectance vector across seven visible bands (",
        ("Y", True, False, False, False),
        ("t", True, True, False, False),
        " = [",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(412), ..., ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(678)]",
        ("t", True, True, False, False),
        ") is modeled as a linear function of time ",
        ("t", True, False, False, False),
        " [5]:"
    ])

    # Equation 7 and Term Meanings
    add_eq(r"\vec{Y}_t = \vec{\mu} + \vec{\beta} t + \vec{N}_t", "7")
    add_where([
        "where ",
        ("Y", True, False, False, False),
        ("t", True, True, False, False),
        " is the annual median remote sensing reflectance vector across the seven visible bands in year ",
        ("t", True, False, False, False),
        "; ",
        ("μ", True, False, False, False),
        " is the baseline intercept vector; ",
        ("β", True, False, False, False),
        " is the trend slope vector (sr⁻¹ yr⁻¹); ",
        ("t", True, False, False, False),
        " is time in years; and ",
        ("N", True, False, False, False),
        ("t", True, True, False, False),
        " is the noise vector representing environmental variations [5]."
    ])

    add_body_p([
        "In ocean time series, the noise vector ",
        ("N", True, False, False, False),
        ("t", True, True, False, False),
        " contains first-order autoregressive red noise (AR(1)), meaning each year's error is correlated with the previous year:"
    ])

    # Equation 8 and Term Meanings
    add_eq(r"\vec{N}_t = \mathbf{\Phi} \vec{N}_{t-1} + \vec{\epsilon}_t", "8")
    add_where([
        "where ",
        ("N", True, False, False, False),
        ("t", True, True, False, False),
        " is the noise vector in year ",
        ("t", True, False, False, False),
        "; ",
        ("Φ", False, False, False, True),
        " is the lag-1 autocorrelation matrix; ",
        ("N", True, False, False, False),
        ("t-1", True, True, False, False),
        " is the noise vector from the previous year; and ",
        ("ε", True, False, False, False),
        ("t", True, True, False, False),
        " is uncorrelated Gaussian white noise [5], [8]."
    ])

    add_body_p([
        "We use the Cochrane-Orcutt iterative method to estimate ",
        ("Φ", False, False, False, True),
        " and transform the time series variables, removing autocorrelation:"
    ])

    # Equation 9 and Term Meanings
    add_eq(r"\vec{Y}_t^* = \vec{Y}_t - \mathbf{\Phi} \vec{Y}_{t-1}, \quad t^* = t - \mathbf{\Phi} t_{-1}", "9")
    add_where([
        "where ",
        ("Y", True, False, False, False),
        ("t", True, True, False, False),
        ("*", False, False, True, False),
        " is the transformed reflectance vector with autocorrelation removed; ",
        ("t", True, False, False, False),
        ("*", False, False, True, False),
        " is the transformed time variable; ",
        ("Φ", False, False, False, True),
        " is the estimated lag-1 autocorrelation matrix; and ",
        ("Y", True, False, False, False),
        ("t-1", True, True, False, False),
        " and ",
        ("t", True, False, False, False),
        ("-1", True, True, False, False),
        " represent the lagged reflectance vector and lagged time."
    ])

    add_body_p([
        "Generalized Least Squares (GLS) regression is then run on the transformed data to calculate the parameter covariance matrix ",
        ("C", False, False, False, True),
        " [8]. The multivariate Signal-to-Noise Ratio (",
        ("SNR", True, False, False, False),
        ") is computed by projecting the trend vector onto the covariance uncertainty ellipse [5]:"
    ])

    # Equation 10 and Term Meanings
    add_eq(r"SNR = \frac{\sqrt{\sum_i \beta_i^2}}{\sqrt{\left(\frac{\vec{\beta}}{\Vert{}\vec{\beta}\Vert{}}\right)^T \mathbf{C} \left(\frac{\vec{\beta}}{\Vert{}\vec{\beta}\Vert{}}\right)}}", "10")
    add_where([
        "where ",
        ("SNR", True, False, False, False),
        " is the multivariate Signal-to-Noise Ratio comparing the trend to background red noise; ",
        ("β", True, False, False, False),
        ("i", True, True, False, False),
        " is the trend slope in band ",
        ("i", True, False, False, False),
        "; ‖",
        ("β", True, False, False, False),
        "‖ is the overall magnitude of the trend vector; and ",
        ("C", False, False, False, True),
        " is the GLS covariance matrix [5]."
    ])

    add_body_p([
        "A trend is considered statistically significant at the 95% confidence level if ",
        ("SNR", True, False, False, False),
        " ≥ 2.0, providing an indicator of ecological change that emerges decades sooner than single-variable chlorophyll models [5], [6]."
    ])

    # IV. EXPECTED ANALYTICAL FRAMEWORK AND DISCUSSION
    add_h1("Expected Analytical Framework and Discussion")

    add_body_p(
        "Combining multi-source satellite radiometry with hydrodynamic reanalysis data provides valuable diagnostic results across three main areas:"
    )

    add_h2("Discrimination Accuracy of Mixotrophic Dinoflagellates")

    add_body_p([
        "Using the narrow-band ratio ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531)/",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(510) allows the system to solve the common problem of confusing green ",
        ("Noctiluca", True, False, False, False),
        " with regular diatoms in standard satellite products [1], [17]. In typical diatom blooms, reflectance decreases steadily from 490 nm to 555 nm "
        "because of normal chlorophyll-",
        ("a", True, False, False, False),
        " absorption [7]. In green ",
        ("Noctiluca", True, False, False, False),
        ", however, the green ",
        ("Pedinomonas noctilucae", True, False, False, False),
        " endosymbionts create a distinct reflectance peak near 531 nm and strong absorption near 510 nm. Tracking this specific ratio across winter satellite passes "
        "allows continuous mapping of cell densities in both coastal and offshore areas. In addition, computing dynamic particulate backscattering (",
        ("b", True, False, False, False),
        ("bp", False, True, False, False),
        ") using the QAA model helps filter out false detections caused by mineral sediment runoff in shallow bays, ensuring that detected anomalies are real algal blooms."
    ])

    add_h2("Coupling Surface Optics with Hydrodynamic Mixing Drivers")

    add_body_p([
        "Comparing satellite bloom masks with CMEMS physical reanalysis grids confirms the oceanographic triggers identified by Shi and Wang [2] and Lakshmi "
        "et al. [12]. During the winter northeast monsoon, areas with cooler sea surface temperatures (",
        ("SST", True, False, False, False),
        " < 25 °C) and deeper mixed layers (",
        ("MLD", True, False, False, False),
        " ≈ 70–80 m) show significant nutrient entrainment, which is followed by bloom growth once daytime sunlight warms the surface and makes the mixed layer "
        "shallower than Sverdrup's critical depth. Furthermore, combining satellite rasters with ERA5 aerosol optical depth (AOD) data tracks desert dust storms "
        "from the Arabian Peninsula, supporting the dust fertilization mechanism described by Kuttippurath et al. [3], [18]. This shows that while winter convective "
        "mixing supplies major nutrients like nitrate and phosphate, desert dust provides essential trace metals such as iron that sustain blooms in open waters."
    ])

    add_h2("Emergence of Long-Term Ecological Trends")

    add_body_p([
        "Using Cochrane-Orcutt multivariate regression across multi-band reflectance helps determine whether increased greening in the Arabian Sea is a permanent "
        "climate trend or part of natural decadal cycles [11]. In agreement with Cael et al. [5] and Dutkiewicz et al. [6], multivariate ",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        " vectors reduce natural year-to-year noise, allowing significant trends (",
        ("SNR", True, False, False, False),
        " ≥ 2.0) to be detected within the available 20-year satellite record, whereas single-variable chlorophyll models remain uncertain [8]. By tracking "
        "multi-wavelength reflectance patterns, our system can detect subtle changes in plankton optical characteristics—such as rising endosymbiont carotenoids—much "
        "earlier than traditional chlorophyll indexes, providing an early warning signal for regional ecosystem shifts."
    ])

    # V. CONCLUSION
    add_h1("Conclusion")

    add_body_p([
        "In this study, we presented an integrated computational Earth observation framework that connects satellite bio-optical inversion with physical "
        "hydrodynamic reanalysis to detect and monitor ",
        ("Noctiluca scintillans", True, False, False, False),
        " blooms in the northern Arabian Sea. By synthesizing twenty key papers across marine optics, radiative transfer, atmospheric correction, and time-series "
        "statistics, the proposed pipeline directly addresses four major challenges: empirical algorithm misclassification, the gap between surface satellite data "
        "and subsurface mixing, high data loss under large solar zenith angles in winter, and statistical noise in single-variable time series. Our pipeline applies "
        "diagnostic narrow-band ratios (",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(531)/",
        ("R", True, False, False, False),
        ("rs", False, True, False, False),
        "(510)) to estimate cell density, uses neural network atmospheric correction to recover low-sun winter images, connects surface blooms with convective "
        "mixing reanalysis, and applies multivariate autoregressive regression to detect long-term decadal shifts. In future work, we plan to incorporate "
        "Physics-Informed Neural Networks (PINNs) into the pipeline to model 3D subsurface oxygen depletion and predict coastal hypoxia before blooms collapse, "
        "providing a practical early warning system to support marine conservation under UN Sustainable Development Goal 14."
    ])

    # REFERENCES
    doc.add_paragraph("References", style='Heading 5')

    refs = [
        "S. R. Pandi, S. K. Baliarsingh, A. A. Lotliker, N. S. Sarma, and S. C. Tripathy, \"Empirical relationships for remote sensing reflectance and Noctiluca scintillans cell density in the northeastern Arabian Sea,\" Marine Pollution Bulletin, vol. 161, p. 111770, 2020.",
        "W. Shi and M. Wang, \"Phytoplankton biomass dynamics in the Arabian Sea from VIIRS observations,\" Journal of Marine Systems, vol. 227, p. 103670, 2022.",
        "J. Kuttippurath, S. Maishal, P. Anjaneyan, N. Sunanda, and K. Chakraborty, \"Recent changes in atmospheric input and primary productivity in the north Indian Ocean,\" Heliyon, vol. 9, no. 7, p. e17940, 2023.",
        "H. Li, X. He, P. Shanmugam, Y. Bai, D. Wang, T. Li, and F. Gong, \"Assessing and improving the accuracy of Visible Infrared Imaging Radiometer Suite ocean color products in environments with high solar zenith angles,\" Remote Sensing, vol. 16, no. 2, p. 339, 2024.",
        "B. B. Cael, K. Bisson, E. Boss, S. Dutkiewicz, and S. Henson, \"Global climate-change trends detected in indicators of ocean ecology,\" Nature, vol. 619, no. 7970, pp. 551–554, 2023.",
        "S. Dutkiewicz, A. E. Hickman, O. Jahn, S. Henson, C. Beaulieu, and E. Monier, \"Ocean colour signature of climate change,\" Nature Communications, vol. 10, no. 1, p. 578, 2019.",
        "S. Sathyendranath, R. J. W. Brewin, C. Brockmann, V. Brotas, B. Calton, A. Chuprin, et al., \"An ocean-colour time series for use in climate studies: The experience of the Ocean-Colour Climate Change Initiative (OC-CCI),\" Sensors, vol. 19, no. 19, p. 4285, 2019.",
        "M. L. Hammond, C. Beaulieu, S. A. Henson, and S. K. Sahu, \"Regional surface chlorophyll trends and uncertainties in the global ocean,\" Scientific Reports, vol. 10, no. 1, p. 15273, 2020.",
        "K. M. Bisson, E. Boss, T. K. Westberry, and M. J. Behrenfeld, \"Evaluating satellite estimates of particulate backscatter in the global open ocean using autonomous profiling floats,\" Optics Express, vol. 27, no. 21, pp. 30191–30203, 2019.",
        "J. Castant, V. Vantrepotte, R. Frouin, and G. Beaugrand, \"Comprehensive gridded dataset of photosynthetically active radiation in the upper ocean from 1958 to 2022,\" Remote Sensing of Environment, vol. 311, p. 114305, 2024.",
        "J. I. Goes, H. Tian, H. do R. Gomes, O. R. Anderson, K. Al-Hashmi, S. deRada, et al., \"Ecosystem state change in the Arabian Sea fuelled by the recent loss of snow over the Himalayan-Tibetan plateau region,\" Scientific Reports, vol. 10, no. 1, p. 7422, 2020.",
        "R. S. Lakshmi, S. Prakash, P. N. Vinayachandran, and A. Chatterjee, \"Physicochemical controls on the initiation of phytoplankton bloom during the winter monsoon in the Arabian Sea,\" Scientific Reports, vol. 11, no. 1, p. 13247, 2021.",
        "C. R. Asha Devi, K. B. Padmakumar, and V. N. Sanjeevan, \"Understanding the microzooplankton mediated food web of the winter–spring Noctiluca bloom in the Northeastern Arabian Sea Ecosystem,\" Regional Studies in Marine Science, vol. 42, p. 101623, 2021.",
        "K. D. Raj, G. Mathews, D. Obura, R. L. Laju, M. S. Bharath, P. Dilipan, et al., \"Low oxygen levels caused by Noctiluca scintillans bloom kills corals in Gulf of Mannar, India,\" Scientific Reports, vol. 10, no. 1, p. 22216, 2020.",
        "C. Xiang, J. Qi, M. M. R. Sarker, and Z. Chen, \"The key to dinoflagellate (Noctiluca scintillans) blooming and outcompeting diatoms in winter off Pakistan, northern Arabian Sea,\" Science of The Total Environment, vol. 695, p. 133887, 2019.",
        "V. V. S. S. Sarma, J. S. Patil, D. Shankar, and A. C. Anil, \"Shallow convective mixing promotes massive Noctiluca scintillans bloom in the northeastern Arabian Sea,\" Marine Pollution Bulletin, vol. 138, pp. 428–436, 2019.",
        "S. K. Baliarsingh, R. M. Dwivedi, A. A. Lotliker, K. C. Sahu, T. S. Kumar, and S. S. C. Shenoi, \"An optical remote sensing approach for ecological monitoring of red and green Noctiluca scintillans,\" Environmental Monitoring and Assessment, vol. 189, no. 7, p. 330, 2017.",
        "J. Kuttippurath, N. Sunanda, M. V. Martin, and K. Chakraborty, \"Tropical storms trigger phytoplankton blooms in the deserts of north Indian Ocean,\" npj Climate and Atmospheric Science, vol. 4, no. 1, p. 11, 2021.",
        "G. Kulk, T. Platt, J. Dingle, T. Jackson, B. F. Jönsson, H. A. Bouman, et al., \"Primary production, an index of climate change in the ocean: satellite-based estimates over two decades,\" Remote Sensing, vol. 12, no. 5, p. 826, 2020.",
        "H. Loisel, D. Stramski, D. Dessailly, C. Jamet, L. Li, and R. A. Reynolds, \"An inverse model for estimating the optical absorption and backscattering coefficients of seawater from remote-sensing reflectance over a broad range of oceanic and coastal marine environments,\" Journal of Geophysical Research: Oceans, vol. 123, no. 3, pp. 2141–2171, 2018."
    ]

    for ref in refs:
        # Template 'references' style automatically provides [1], [2], ... and exact IEEE indentation
        p_ref = doc.add_paragraph(ref, style='references')

    # Continuous section break at end to balance columns on final page per IEEE guidelines
    doc.add_section(WD_SECTION_START.CONTINUOUS)



    os.makedirs('Final_Submission', exist_ok=True)
    docx_out = os.path.join('Final_Submission', 'Spatio_Temporal_Detection_Noctiluca_scintillans.docx')
    pdf_out = os.path.join('Final_Submission', 'Spatio_Temporal_Detection_Noctiluca_scintillans.pdf')

    doc.save(docx_out)
    print(f"Document saved to {docx_out}")

    docx2pdf_convert(docx_out, pdf_out)
    print(f"Exported PDF to {pdf_out}")

if __name__ == '__main__':
    build_paper()
