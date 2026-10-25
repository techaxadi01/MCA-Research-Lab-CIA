import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

def generate_tight_diagram(output_path='pipeline_architecture.png', dpi=500):
    # Palette: IEEE Academic Navy, Cyan, Slate, White
    C_OUTER = '#0f172a'
    C_BANNER = '#0f172a'
    C_BORDER = '#334155'
    C_LEFT_HEAD = '#1e293b'       # Radiometry / Algorithm Pipeline (Dark Slate Navy)
    C_RIGHT_HEAD = '#0369a1'      # Reanalysis Pipeline (Deep Blue)
    C_OUT_HEAD = '#0f172a'        # Operational Output Engine (Dark Navy)
    C_TEXT = '#0f172a'
    C_ARROW = '#0f172a'
    C_BUS = '#0284c7'             # Reanalysis bus line (Cyan-Blue)
    C_BADGE_BG = '#f0f9ff'
    C_BADGE_BORDER = '#0ea5e9'

    fig_w = 3.38
    margin_x = 0.07
    usable_w = fig_w - 2 * margin_x  # 3.24 in

    # Columns
    w_left = 1.86
    x_left = margin_x               # 0.07 in
    x_left_end = x_left + w_left    # 1.93 in

    w_right = 1.25
    x_right = fig_w - margin_x - w_right  # 2.06 in
    x_bus = 2.15                    # Vertical bus line x-coord

    # Vertical heights & spacing (compact and tight)
    banner_h = 0.28
    r1_h = 0.40      # Row 1 source boxes
    r2_h = 0.54      # Row 2 (Stage 1 & NetCDF-4)
    r3_h = 0.54      # Row 3 (Stage 2)
    r4_h = 0.54      # Row 4 (Stage 3)
    r5_h = 0.54      # Row 5 (Stage 4)
    r6_h = 0.62      # Row 6 (Bottom Output Engine)

    gap_v = 0.065
    margin_top = 0.06
    margin_bot = 0.06

    fig_h = (margin_top + banner_h + gap_v +
             r1_h + gap_v +
             r2_h + gap_v +
             r3_h + gap_v +
             r4_h + gap_v +
             r5_h + gap_v +
             r6_h + margin_bot)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Outer border
    outer = FancyBboxPatch((margin_x * 0.4, margin_bot * 0.4),
                           fig_w - margin_x * 0.8, fig_h - margin_bot * 0.8,
                           boxstyle='round,pad=0.015,rounding_size=0.04',
                           ec=C_OUTER, fc='#ffffff', lw=0.85, zorder=1)
    ax.add_patch(outer)

    # 1. TOP MASTER BANNER (image.txt Lines 1-3)
    banner_y = fig_h - margin_top - banner_h
    banner = FancyBboxPatch((margin_x, banner_y), usable_w, banner_h,
                            boxstyle='round,pad=0.01,rounding_size=0.035',
                            ec=C_BANNER, fc=C_BANNER, lw=0.6, zorder=2)
    ax.add_patch(banner)
    ax.text(fig_w / 2.0, banner_y + banner_h * 0.52, 'INTEGRATED COMPUTATIONAL PIPELINE',
            ha='center', va='center', fontsize=7.6, fontweight='bold',
            fontfamily='serif', color='#ffffff', zorder=3)

    # Helper function to draw cards with larger text and tight line spacing
    def draw_card(x, y, w, h, title, items, head_color=C_LEFT_HEAD, z=2,
                  title_size=5.4, text_size=4.7, line_gap=0.082):
        # Card body
        card = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.01,rounding_size=0.03',
                              ec=C_BORDER, fc='#ffffff', lw=0.55, zorder=z)
        ax.add_patch(card)

        # Header bar
        h_head = 0.17
        head = FancyBboxPatch((x, y + h - h_head), w, h_head, boxstyle='round,pad=0.01,rounding_size=0.03',
                              ec=C_BORDER, fc=head_color, lw=0.55, zorder=z+1)
        ax.add_patch(head)

        ax.text(x + w / 2.0, y + h - h_head / 2.0, title, ha='center', va='center',
                fontsize=title_size, fontweight='bold', fontfamily='serif', color='#ffffff', zorder=z+2)

        # Centered block of items with tight line spacing
        n_items = len(items)
        block_h = (n_items - 1) * line_gap
        body_mid_y = y + (h - h_head) / 2.0
        start_y = body_mid_y + block_h / 2.0

        for i, item in enumerate(items):
            cur_y = start_y - i * line_gap
            if isinstance(item, tuple):
                prefix, text = item
                ax.text(x + 0.05, cur_y, prefix, ha='left', va='center',
                        fontsize=text_size, fontweight='bold', color=head_color, zorder=z+2)
                ax.text(x + 0.135, cur_y, text, ha='left', va='center',
                        fontsize=text_size, fontfamily='serif', color=C_TEXT, zorder=z+2)
            else:
                ax.text(x + w / 2.0, cur_y, item, ha='center', va='center',
                        fontsize=text_size, fontfamily='serif', color=C_TEXT, zorder=z+2)

    # 2. ROW 1: DUAL INPUT SOURCES (image.txt Line 4)
    r1_y = banner_y - gap_v - r1_h
    # Left Input: Satellite Radiometry
    draw_card(x_left, r1_y, w_left, r1_h,
              "Satellite Radiometry: MODIS, VIIRS, OLCI",
              ["TOA / Rayleigh Radiances (412–671 nm)",
               "Continuous multi-sensor archive (2002–2023)"],
              head_color=C_LEFT_HEAD, title_size=4.9, text_size=4.5, line_gap=0.08)

    # Right Input: Ocean-Atmosphere Reanalysis
    draw_card(x_right, r1_y, w_right, r1_h,
              "Ocean-Atmosphere Reanalysis",
              ["CMEMS Daily Ocean Physics",
               "ECMWF ERA5 Reanalysis"],
              head_color=C_RIGHT_HEAD, title_size=4.8, text_size=4.5, line_gap=0.08)

    # Downward arrows Row 1 -> Row 2
    r2_y = r1_y - gap_v - r2_h
    ax.annotate('', xy=(x_left + w_left / 2.0, r2_y + r2_h),
                xytext=(x_left + w_left / 2.0, r1_y),
                arrowprops=dict(facecolor=C_ARROW, edgecolor=C_ARROW, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))
    ax.annotate('', xy=(x_right + w_right / 2.0, r2_y + r2_h),
                xytext=(x_right + w_right / 2.0, r1_y),
                arrowprops=dict(facecolor=C_ARROW, edgecolor=C_ARROW, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    # 3. ROW 2: STAGE 1 & NETCDF-4 SPATIAL SLICING (image.txt Lines 7-11)
    # Left: STAGE 1
    draw_card(x_left, r2_y, w_left, r2_h,
              "STAGE 1: Data Ingestion & Preprocessing",
              [("•", "L2 Quality Flags: LAND, CLDICE, SZA, GLINT"),
               ("•", "Extracts Rayleigh radiances L_rc(λ)"),
               ("•", "Projected to 4 × 4 km sinusoidal grid")],
              head_color=C_LEFT_HEAD, title_size=5.1, text_size=4.7, line_gap=0.086)

    # Right: NetCDF-4 Spatial Slicing
    draw_card(x_right, r2_y, w_right, r2_h,
              "NetCDF-4 Spatial Slicing",
              [("•", "Domain: 10°–25°N, 50°–75°E"),
               ("•", "Daily MLD, SST, w (70m), Wind"),
               ("•", "Surface PAR & Euphotic Depth")],
              head_color=C_RIGHT_HEAD, title_size=5.0, text_size=4.5, line_gap=0.086)

    # Downward arrow Stage 1 -> Stage 2
    r3_y = r2_y - gap_v - r3_h
    ax.annotate('', xy=(x_left + w_left / 2.0, r3_y + r3_h),
                xytext=(x_left + w_left / 2.0, r2_y),
                arrowprops=dict(facecolor=C_ARROW, edgecolor=C_ARROW, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    # 4. ROW 3: STAGE 2 ATMOSPHERIC CORRECTION (image.txt Lines 14-18)
    draw_card(x_left, r3_y, w_left, r3_h,
              "STAGE 2: Geometric & Atmospheric Correction",
              [("•", "NN-V Multilayer Perceptron (64 ReLU)"),
               ("•", "Recovers winter high zenith (θ₀ > 70°)"),
               ("•", "Inverts water-leaving reflectance R_rs(λ)")],
              head_color=C_LEFT_HEAD, title_size=5.0, text_size=4.7, line_gap=0.086)

    # Downward arrow Stage 2 -> Stage 3
    r4_y = r3_y - gap_v - r4_h
    ax.annotate('', xy=(x_left + w_left / 2.0, r4_y + r4_h),
                xytext=(x_left + w_left / 2.0, r3_y),
                arrowprops=dict(facecolor=C_ARROW, edgecolor=C_ARROW, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    # 5. ROW 4: STAGE 3 BIO-OPTICAL FEATURE ENGINEERING (image.txt Lines 21-25)
    draw_card(x_left, r4_y, w_left, r4_h,
              "STAGE 3: Bio-Optical Feature Engineering",
              [("•", "QAA v6: b_bp(λ) & a_nw(λ) inversion"),
               ("•", "Noctiluca Ratio: R_rs(531) / R_rs(510)"),
               ("•", "Empirical Cell Density Formula (N_cells)")],
              head_color=C_LEFT_HEAD, title_size=5.0, text_size=4.7, line_gap=0.086)

    # Downward arrow Stage 3 -> Stage 4
    r5_y = r4_y - gap_v - r5_h
    ax.annotate('', xy=(x_left + w_left / 2.0, r5_y + r5_h),
                xytext=(x_left + w_left / 2.0, r4_y),
                arrowprops=dict(facecolor=C_ARROW, edgecolor=C_ARROW, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    # 6. ROW 5: STAGE 4 MULTIVARIATE TREND MODELING (image.txt Lines 28-32)
    draw_card(x_left, r5_y, w_left, r5_h,
              "STAGE 4: Multivariate Trend Modeling",
              [("•", "Cochrane-Orcutt AR(1) red-noise filter"),
               ("•", "Generalized Least Squares (GLS) trend solver"),
               ("•", "Time of Emergence verified (SNR ≥ 2.0)")],
              head_color=C_LEFT_HEAD, title_size=5.0, text_size=4.7, line_gap=0.086)

    # -------------------------------------------------------------
    # LATERAL COUPLING BUS LINE FROM REANALYSIS (image.txt Lines 15 & 29)
    # -------------------------------------------------------------
    stg2_center_y = r3_y + r3_h / 2.0
    stg4_center_y = r5_y + r5_h / 2.0

    netcdf_bot_x = x_right + 0.12
    ax.plot([netcdf_bot_x, x_bus], [r2_y, r2_y - 0.025], color=C_BUS, lw=0.9, ls='--', zorder=4)
    ax.plot([x_bus, x_bus], [r2_y - 0.025, stg4_center_y], color=C_BUS, lw=0.9, ls='--', zorder=4)

    # Junction dots
    ax.scatter([x_bus, x_bus], [stg2_center_y, stg4_center_y], s=14, color=C_BUS, zorder=5)

    # Branch 1 into Stage 2: Arrow pointing LEFT from bus into Stage 2 box
    ax.annotate('', xy=(x_left_end, stg2_center_y),
                xytext=(x_bus, stg2_center_y),
                arrowprops=dict(facecolor=C_BUS, edgecolor=C_BUS, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    # Pill label for Branch 1 (image.txt Line 15: "(ERA5 Aerosol & Optical Inputs)")
    lbl_w = usable_w - (x_bus - margin_x) - 0.05
    lbl_h = 0.30
    lbl1_box = FancyBboxPatch((x_bus + 0.04, stg2_center_y - lbl_h / 2.0), lbl_w, lbl_h,
                              boxstyle='round,pad=0.008,rounding_size=0.025',
                              ec=C_BADGE_BORDER, fc=C_BADGE_BG, lw=0.55, zorder=5)
    ax.add_patch(lbl1_box)
    ax.text(x_bus + 0.04 + lbl_w / 2.0, stg2_center_y + 0.052, 'ERA5 Aerosol &',
            ha='center', va='center', fontsize=4.6, fontweight='bold', fontfamily='serif', color='#0369a1', zorder=6)
    ax.text(x_bus + 0.04 + lbl_w / 2.0, stg2_center_y - 0.052, 'Optical Inputs',
            ha='center', va='center', fontsize=4.4, fontfamily='serif', color='#0369a1', zorder=6)

    # Branch 2 into Stage 4: Arrow pointing LEFT from bus into Stage 4 box
    ax.annotate('', xy=(x_left_end, stg4_center_y),
                xytext=(x_bus, stg4_center_y),
                arrowprops=dict(facecolor=C_BUS, edgecolor=C_BUS, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    # Pill label for Branch 2 (image.txt Line 29: "(CMEMS MLD & w Physical Covariates)")
    lbl2_box = FancyBboxPatch((x_bus + 0.04, stg4_center_y - lbl_h / 2.0), lbl_w, lbl_h,
                              boxstyle='round,pad=0.008,rounding_size=0.025',
                              ec=C_BADGE_BORDER, fc=C_BADGE_BG, lw=0.55, zorder=5)
    ax.add_patch(lbl2_box)
    ax.text(x_bus + 0.04 + lbl_w / 2.0, stg4_center_y + 0.052, 'CMEMS MLD & w',
            ha='center', va='center', fontsize=4.6, fontweight='bold', fontfamily='serif', color='#0369a1', zorder=6)
    ax.text(x_bus + 0.04 + lbl_w / 2.0, stg4_center_y - 0.052, 'Physical Covariates',
            ha='center', va='center', fontsize=4.2, fontfamily='serif', color='#0369a1', zorder=6)

    # 7. ROW 6: OPERATIONAL OUTPUT ENGINE (image.txt Line 35)
    r6_y = r5_y - gap_v - r6_h
    # Downward arrow Stage 4 -> Row 6
    ax.annotate('', xy=(x_left + w_left / 2.0, r6_y + r6_h),
                xytext=(x_left + w_left / 2.0, r5_y),
                arrowprops=dict(facecolor=C_ARROW, edgecolor=C_ARROW, arrowstyle='-|>', lw=1.1, mutation_scale=5.5))

    draw_card(margin_x, r6_y, usable_w, r6_h,
              "Operational Bloom Mapping & Climate Trend Attribution Engine",
              [("1.", "Synoptic Bloom Masks: Discriminates green Noctiluca via 531 nm peak"),
               ("2.", "Quantitative Density: Inverts Pandi empirical model (> 6,800 cells L⁻¹)"),
               ("3.", "Hydrodynamic Trend: Validates convective mixing & decadal bloom shifts")],
              head_color=C_OUT_HEAD, title_size=5.2, text_size=4.7, line_gap=0.088)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.01)
    plt.close()
    print(f"Generated Tight Spacing Diagram: {output_path} (width={fig_w:.2f} in, height={fig_h:.2f} in)")

if __name__ == '__main__':
    generate_tight_diagram()
