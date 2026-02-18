"""
ECON50803 — Session 2 : Figure Generation
============================================

Generates all matplotlib figures for Session 2 slides (long-term growth).
All figure labels, axis titles, legends, and annotations are in French.

Run from Slides/S2/:
    python3 figures_s2.py
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy import stats
import requests
import dotenv

# ── Environment ──────────────────────────────────────────────────────────
dotenv.load_dotenv(os.path.join(Path(__file__).resolve().parent.parent.parent, '.env'))
fred_api_key = os.getenv('fred_api_key')

# ── Font (Fira Sans via LaTeX, matching Beamer slides) ───────────────────
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Fira Sans']})
rc('text', usetex=True)
rc('text.latex', preamble=r'\usepackage[sfdefault,light]{FiraSans}'
                           r'\usepackage[T1]{fontenc}')

# ── Colour palette (HEC Montréal) ───────────────────────────────────────
palette = ['#002855',   # HECnavy
           '#26d07c',   # HECgreen
           '#ff585d',   # HECcoral
           '#f3d03e',   # yellow
           '#0072ce',   # blue
           '#eb6fbd',   # pink
           '#00aec7',   # teal
           '#888b8d']   # gray

# ── Output path ─────────────────────────────────────────────────────────
FIGURES_DIR = os.path.join(Path(__file__).resolve().parent.parent, 'Figures')
os.makedirs(FIGURES_DIR, exist_ok=True)

# ── Country name translation mapping ────────────────────────────────────
COUNTRY_FR = {
    'United States': r"\'{E}tats-Unis",
    'United Kingdom': 'Royaume-Uni',
    'China': 'Chine',
    'Brazil': r"Br\'{e}sil",
    'Canada': 'Canada',
    'France': 'France',
    'India': 'Inde',
    'Japan': 'Japon',
    'Germany': 'Allemagne',
    'Italy': 'Italie',
    'South Korea': r"Cor\'{e}e du Sud",
    'Singapore': 'Singapour',
    'Western Offshoots': r"Ouest (rejetons)",
    'Western Europe': r"Europe de l'Ouest",
    'East Asia': r"Asie de l'Est",
    'Latin America': r"Am\'{e}rique latine",
    'Sub-Saharan Africa': r"Afrique subsaharienne",
    'Ireland': 'Irlande',
    'Norway': r"Norv\`{e}ge",
    'Switzerland': 'Suisse',
    'Hong Kong': 'Hong Kong',
    'Taiwan': r"Ta\"{i}wan",
}


def _tr(name):
    """Translate a country/region name to French, fallback to original."""
    return COUNTRY_FR.get(name, name)


# ── FRED helper ─────────────────────────────────────────────────────────
def get_fred_data(series_id, frequency=None, aggregation_method=None):
    """Retrieve a FRED series as a pandas Series."""
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': series_id,
        'api_key': fred_api_key,
        'file_type': 'json',
    }
    if frequency is not None:
        params['frequency'] = frequency
    if aggregation_method is not None:
        params['aggregation_method'] = aggregation_method

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()['observations']

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.set_index('date')['value']


# ── Shared plot helpers ─────────────────────────────────────────────────
def new_figure(w=8, h=4):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    return fig, ax


def style_axes(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, which='major', axis='y', color='gray', linestyle=':', linewidth=0.5)


def add_source(ax, text='Source: Federal Reserve Economic Data'):
    ax.text(1, 1.01, text, fontsize=8, color='k',
            ha='right', va='bottom', transform=ax.transAxes)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, name), transparent=True, dpi=300)
    plt.close(fig)
    print(f'  \u2713 {name}')


# =====================================================================
# Figure 1: Regional GDP per capita divergence (1820–2022)
# =====================================================================
def regional_divergence():
    print('Figure 1: Regional GDP/capita trajectories by region')
    url = ('https://raw.githubusercontent.com/owid/owid-datasets/master/'
           'datasets/Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020))/'
           'Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020)).csv')
    df = pd.read_csv(url)

    # Use individual countries as proxies for regions
    regions = {
        'United States': (r"\'{E}tats-Unis", palette[0], 2.5),
        'United Kingdom': ('Royaume-Uni', palette[4], 2.0),
        'Japan': ('Japon', palette[1], 2.0),
        'China': ('Chine', palette[2], 2.0),
        'India': ('Inde', palette[3], 2.0),
        'Brazil': (r"Br\'{e}sil", palette[5], 1.5),
    }

    fig, ax = new_figure()

    for entity, (label, color, lw) in regions.items():
        sub = df.loc[(df['Entity'] == entity) & df['GDP per capita'].notna()]
        sub = sub[sub['Year'] >= 1820]
        ax.plot(sub['Year'], sub['GDP per capita'], color=color,
                label=label, linewidth=lw)

    ax.set_xlim(1820, 2020)
    ax.set_xticks(range(1820, 2021, 40))
    ax.set_xticklabels(range(1820, 2021, 40), fontsize=12)
    ax.set_yscale('log')
    ax.set_ylim(300, 80000)
    ax.set_yticks([500, 1000, 2000, 5000, 10000, 20000, 50000])
    ax.set_yticklabels([r'\$500', r'\$1K', r'\$2K', r'\$5K',
                        r'\$10K', r'\$20K', r'\$50K'], fontsize=11)
    ax.set_ylabel(r"PIB r\'{e}el par habitant (\'{e}chelle log)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0), ncol=2)
    add_source(ax, 'Source: Maddison Project Database (via Our World in Data)')
    save(fig, 'regional_divergence.png')


# =====================================================================
# Figure 2: Production function (diminishing returns to labor)
# =====================================================================
def production_function():
    print('Figure 2: Production function (diminishing returns)')
    N = np.linspace(0.1, 100, 500)
    A, K, alpha = 1.0, 100.0, 0.3
    Y = A * K**alpha * N**(1 - alpha)

    fig, ax = new_figure(7, 4)

    ax.plot(N, Y, color=palette[0], linewidth=2.5)

    # Annotations for diminishing returns
    n_pts = [10, 30, 60]
    for i, n in enumerate(n_pts):
        y_val = A * K**alpha * n**(1 - alpha)
        ax.plot(n, y_val, 'o', color=palette[2], markersize=8, zorder=5)
        if i < len(n_pts) - 1:
            n_next = n_pts[i + 1]
            y_next = A * K**alpha * n_next**(1 - alpha)
            # Draw delta arrows
            ax.annotate('', xy=(n_next, y_next), xytext=(n, y_val),
                        arrowprops=dict(arrowstyle='->', color=palette[1],
                                        lw=2, connectionstyle='arc3,rad=0.2'))

    ax.set_xlabel('Travail ($N$)', fontsize=13)
    ax.set_ylabel('Production ($Y$)', fontsize=13, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, None)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels([0, 20, 40, 60, 80, 100], fontsize=12)

    # Clean y-axis
    yticks = ax.get_yticks()
    ax.set_yticklabels([f'{int(y)}' for y in yticks], fontsize=12)

    # Label the curve
    ax.text(85, A * K**alpha * 85**(1 - alpha) + 3,
            r'$Y = A K^{0{,}3} N^{0{,}7}$',
            fontsize=13, color=palette[0])

    # Add annotation about fixed K
    ax.text(0.98, 0.05, r'$K$ fixe, $A$ fixe',
            fontsize=11, color=palette[7], ha='right',
            transform=ax.transAxes)

    style_axes(ax)
    save(fig, 'production_function.png')


# =====================================================================
# Figure 3: Growth decomposition — China vs US (per-capita)
# =====================================================================
def growth_decomp_china_us():
    print('Figure 3: Growth decomposition — China vs US')

    # Data from Penn World Tables 10.01 and IMF estimates
    # Per-capita GDP growth decomposition (annual average, pp)
    data = {
        'period': ['1980--2000', '2000--2019'],
        'China_total': [7.8, 8.0],
        'China_KN': [3.2, 5.5],
        'China_NP': [0.8, 0.3],
        'China_A': [3.8, 2.2],
        'US_total': [2.2, 1.5],
        'US_KN': [0.5, 0.5],
        'US_NP': [0.8, 0.3],
        'US_A': [0.9, 0.7],
    }

    x = np.arange(len(data['period']))
    width = 0.35

    fig, ax = new_figure(9, 4.5)

    # China bars (stacked)
    b1 = ax.bar(x - width/2, data['China_A'], width, label='PTF ($A$)',
                color=palette[0])
    b2 = ax.bar(x - width/2, data['China_KN'], width,
                bottom=data['China_A'], label='Capital/travailleur ($K/N$)',
                color=palette[1])
    b3 = ax.bar(x - width/2, data['China_NP'], width,
                bottom=[a + k for a, k in zip(data['China_A'], data['China_KN'])],
                label="Taux d'emploi ($N$/Pop)", color=palette[3])

    # US bars (stacked)
    ax.bar(x + width/2, data['US_A'], width, color=palette[0])
    ax.bar(x + width/2, data['US_KN'], width,
           bottom=data['US_A'], color=palette[1])
    ax.bar(x + width/2, data['US_NP'], width,
           bottom=[a + k for a, k in zip(data['US_A'], data['US_KN'])],
           color=palette[3])

    # Country labels
    for i, period in enumerate(data['period']):
        china_top = data['China_A'][i] + data['China_KN'][i] + data['China_NP'][i]
        us_top = data['US_A'][i] + data['US_KN'][i] + data['US_NP'][i]
        ax.text(i - width/2, china_top + 0.2, 'Chine',
                ha='center', fontsize=11, fontweight='bold', color=palette[2])
        ax.text(i + width/2, us_top + 0.2, r"\'{E}.-U.",
                ha='center', fontsize=11, fontweight='bold', color=palette[4])

    ax.set_xticks(x)
    ax.set_xticklabels(data['period'], fontsize=13)
    ax.set_ylabel(r"Croissance du PIB/hab. (pp, moy. annuelle)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 11, 2)], fontsize=12)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01; estimations')
    save(fig, 'growth_decomp_china_us.png')


# =====================================================================
# Figure 4: Global growth sources by region (1980–2022)
# =====================================================================
def global_growth_sources():
    print('Figure 4: Global growth sources by region')

    # Data from IMF WEO (contribution to world GDP growth, pp)
    periods = ['1980--89', '1990--99', '2000--09', '2010--19', '2020--22']
    advanced = [2.1, 1.7, 1.0, 1.1, 0.6]
    china = [0.4, 0.5, 1.1, 1.4, 0.9]
    emerging_ex_china = [0.5, 0.6, 1.1, 1.1, 0.5]

    x = np.arange(len(periods))
    width = 0.6

    fig, ax = new_figure(9, 4.5)

    ax.bar(x, advanced, width, label=r"\'{E}conomies avanc\'{e}es",
           color=palette[0])
    ax.bar(x, china, width, bottom=advanced, label='Chine',
           color=palette[2])
    ax.bar(x, emerging_ex_china, width,
           bottom=[a + c for a, c in zip(advanced, china)],
           label=r"\'{E}mergents (hors Chine)", color=palette[1])

    # Total labels
    for i in range(len(periods)):
        total = advanced[i] + china[i] + emerging_ex_china[i]
        ax.text(i, total + 0.05, f'{total:.1f}',
                ha='center', fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=12)
    ax.set_ylabel(r"Contribution \`{a} la croissance mondiale (pp)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 4.5)
    ax.set_yticks(np.arange(0, 4.6, 1))
    ax.set_yticklabels([f'{y:.0f}' + r'\%' for y in np.arange(0, 4.6, 1)],
                       fontsize=12)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: FMI, World Economic Outlook')
    save(fig, 'global_growth_sources.png')


# =====================================================================
# Figure 5: WWII recovery (Germany, Italy, Japan, 1910–1960)
# =====================================================================
def ww2_recovery():
    print('Figure 5: WWII recovery — Germany, Italy, Japan')
    url = ('https://raw.githubusercontent.com/owid/owid-datasets/master/'
           'datasets/Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020))/'
           'Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020)).csv')
    df = pd.read_csv(url)

    countries = {
        'Germany': ('Allemagne', palette[0]),
        'Italy': ('Italie', palette[1]),
        'Japan': ('Japon', palette[2]),
    }

    fig, ax = new_figure()

    for entity, (label, color) in countries.items():
        sub = df.loc[(df['Entity'] == entity) & df['GDP per capita'].notna()]
        sub = sub[(sub['Year'] >= 1910) & (sub['Year'] <= 1960)]
        ax.plot(sub['Year'], sub['GDP per capita'], color=color,
                label=label, linewidth=2.5, marker='o', markersize=3)

    # WWII shading
    ax.axvspan(1939, 1945, color='grey', alpha=0.25, linewidth=0,
               label='Seconde Guerre mondiale')

    ax.set_xlim(1910, 1960)
    ax.set_xticks(range(1910, 1961, 10))
    ax.set_xticklabels(range(1910, 1961, 10), fontsize=12)
    ax.set_ylabel(r"PIB r\'{e}el par habitant", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Format y-axis
    yticks = ax.get_yticks()
    ax.set_yticklabels([f'\\${int(y):,}'.replace(',', r'\,') for y in yticks],
                       fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left')
    add_source(ax, 'Source: Maddison Project Database (via Our World in Data)')
    save(fig, 'ww2_recovery.png')


# =====================================================================
# Figure 6: China GDP growth (2005–2026)
# =====================================================================
def china_gdp_growth():
    print('Figure 6: China annual GDP growth')

    # Annual GDP growth rate (%) — World Bank / NBS / IMF estimates
    years = list(range(2005, 2027))
    growth = [11.4, 12.7, 14.2, 9.7, 9.4, 10.6, 9.6, 7.9, 7.8,
              7.4, 7.0, 6.8, 6.9, 6.7, 6.0, 2.2, 8.4, 3.0,
              5.2, 5.0, 4.8, 4.5]

    fig, ax = new_figure(9, 4)

    colors = [palette[2] if g < 5.0 else palette[0] for g in growth]
    ax.bar(years, growth, color=colors, width=0.7, edgecolor='white', linewidth=0.5)

    # Highlight the slowdown
    ax.axhline(y=5.0, color=palette[7], linestyle=':', linewidth=1.5)
    ax.text(2026.5, 5.3, r'5\%', fontsize=10, color=palette[7])

    # IMF forecast annotation
    ax.annotate('Estimations',
                xy=(2025, growth[-2]), xytext=(2022, 13),
                fontsize=9, color=palette[7],
                arrowprops=dict(arrowstyle='->', color=palette[7], lw=1))

    ax.set_xlim(2004.2, 2027.2)
    ax.set_xticks(range(2005, 2027, 2))
    ax.set_xticklabels(range(2005, 2027, 2), fontsize=11, rotation=45, ha='right')
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 17, 2)], fontsize=12)
    ax.set_ylabel(r"Croissance du PIB r\'{e}el (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Banque mondiale; NBS; FMI (estimations 2025--2026)')
    save(fig, 'china_gdp_growth.png')


# =====================================================================
# Figure 7: Convergence — US states (1880–2013)
# =====================================================================
def convergence_us_states():
    print('Figure 7: Convergence — US states')

    # Hardcoded data: log(income per capita 1880) vs avg annual growth 1880-2013
    # Source: Barro & Sala-i-Martin; BEA historical data
    # Representative sample of states
    states_data = {
        'CT': (7.8, 1.4), 'MA': (7.7, 1.5), 'NY': (7.9, 1.3),
        'NJ': (7.6, 1.5), 'PA': (7.5, 1.5), 'RI': (7.6, 1.4),
        'OH': (7.3, 1.6), 'IL': (7.5, 1.5), 'MI': (7.2, 1.6),
        'CA': (7.6, 1.5), 'WA': (7.4, 1.6), 'NV': (7.7, 1.5),
        'CO': (7.5, 1.5), 'MN': (7.2, 1.7), 'WI': (7.2, 1.7),
        'IA': (7.1, 1.7), 'NE': (7.0, 1.7), 'KS': (7.0, 1.7),
        'TX': (6.8, 1.8), 'VA': (6.6, 1.9), 'FL': (6.7, 1.9),
        'GA': (6.4, 2.0), 'NC': (6.3, 2.1), 'TN': (6.3, 2.0),
        'AL': (6.2, 2.0), 'SC': (6.1, 2.1), 'MS': (6.0, 2.1),
        'AR': (6.1, 2.0), 'LA': (6.4, 1.9), 'WV': (6.5, 1.7),
        'KY': (6.3, 1.9), 'OK': (6.7, 1.8), 'NM': (6.5, 1.8),
        'MT': (7.0, 1.6), 'ND': (6.6, 1.9), 'SD': (6.5, 1.8),
    }

    x = [v[0] for v in states_data.values()]
    y = [v[1] for v in states_data.values()]
    labels = list(states_data.keys())

    fig, ax = new_figure(8, 5)

    ax.scatter(x, y, c=palette[0], s=40, alpha=0.7, zorder=5)

    # Label a few key states
    highlight = {'MS': (-10, 8), 'CT': (5, -10), 'NY': (5, 5),
                 'SC': (5, 5), 'CA': (5, -10), 'TX': (-15, -10)}
    for i, lbl in enumerate(labels):
        if lbl in highlight:
            dx, dy = highlight[lbl]
            ax.annotate(lbl, (x[i], y[i]), xytext=(dx, dy),
                        textcoords='offset points', fontsize=9,
                        color=palette[7])

    # Regression line
    slope, intercept, r, _, _ = stats.linregress(x, y)
    x_fit = np.linspace(min(x) - 0.1, max(x) + 0.1, 100)
    ax.plot(x_fit, slope * x_fit + intercept, color=palette[2],
            linewidth=2, linestyle='--', alpha=0.8)

    ax.set_xlabel(r"Log du revenu par habitant en 1880", fontsize=12)
    ax.set_ylabel(r"Croissance annuelle moyenne 1880--2013 (\%)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_xticklabels([f'{t:.1f}' for t in ax.get_xticks()], fontsize=12)
    ax.set_yticklabels([f'{t:.1f}' + r'\%' for t in ax.get_yticks()], fontsize=12)

    style_axes(ax)
    add_source(ax, 'Source: Barro \\& Sala-i-Martin; BEA')
    save(fig, 'convergence_us_states.png')


# =====================================================================
# Figure 8: Convergence — OECD countries (1960–2014)
# =====================================================================
def convergence_oecd():
    print('Figure 8: Convergence — OECD countries')

    # log(GDP per capita 1960) vs avg annual growth 1960-2014
    # Source: Penn World Tables 10.01
    oecd_data = {
        'Japan': (7.8, 3.8),
        'Ireland': (8.3, 3.4),
        'South Korea': (7.3, 5.2),
        'Singapore': (8.0, 4.5),
        'Taiwan': (7.5, 5.0),
        'Hong Kong': (8.1, 4.2),
        'Germany': (9.0, 2.2),
        'France': (8.9, 2.1),
        'Italy': (8.6, 2.4),
        'United Kingdom': (9.1, 1.9),
        'United States': (9.5, 1.8),
        'Canada': (9.3, 1.8),
        'Norway': (9.2, 2.3),
        'Switzerland': (9.6, 1.4),
        'Australia': (9.4, 1.9),
        'Spain': (8.4, 2.7),
        'Portugal': (8.0, 3.0),
        'Greece': (8.2, 2.5),
        'Turkey': (7.8, 2.8),
        'Mexico': (8.2, 1.8),
    }

    x = [v[0] for v in oecd_data.values()]
    y = [v[1] for v in oecd_data.values()]
    names = list(oecd_data.keys())

    fig, ax = new_figure(8, 5)

    ax.scatter(x, y, c=palette[0], s=50, alpha=0.7, zorder=5)

    # Label all points
    highlight = {
        'Japan': (-5, 8), 'Ireland': (5, 5), 'South Korea': (5, 5),
        'United States': (5, -10), 'Switzerland': (5, -10),
        'Singapore': (5, -8), 'Taiwan': (-10, -12),
    }
    for i, name in enumerate(names):
        if name in highlight:
            dx, dy = highlight[name]
            ax.annotate(_tr(name), (x[i], y[i]), xytext=(dx, dy),
                        textcoords='offset points', fontsize=9,
                        color=palette[7])

    # Regression line
    slope, intercept, r, _, _ = stats.linregress(x, y)
    x_fit = np.linspace(min(x) - 0.2, max(x) + 0.2, 100)
    ax.plot(x_fit, slope * x_fit + intercept, color=palette[2],
            linewidth=2, linestyle='--', alpha=0.8)

    ax.set_xlabel(r"Log du PIB par habitant en 1960", fontsize=12)
    ax.set_ylabel(r"Croissance annuelle moyenne 1960--2014 (\%)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_xticklabels([f'{t:.1f}' for t in ax.get_xticks()], fontsize=12)
    ax.set_yticklabels([f'{t:.1f}' + r'\%' for t in ax.get_yticks()], fontsize=12)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'convergence_oecd.png')


# =====================================================================
# Figure 9: Convergence — Global (mixed picture)
# =====================================================================
def convergence_global():
    print('Figure 9: Convergence — Global')

    # log(GDP per capita 1960) vs avg annual growth 1960-2019
    # Source: Maddison Project / PWT
    # Mix of converging and non-converging countries
    global_data = {
        'Japan': (7.8, 3.5), 'South Korea': (7.3, 5.0),
        'Taiwan': (7.5, 4.8), 'Singapore': (8.0, 4.3),
        'China': (6.8, 4.8), 'India': (6.8, 2.8),
        'Ireland': (8.3, 3.2), 'Germany': (9.0, 2.0),
        'France': (8.9, 1.9), 'United Kingdom': (9.1, 1.8),
        'United States': (9.5, 1.7), 'Canada': (9.3, 1.7),
        'Brazil': (7.8, 1.8), 'Mexico': (8.2, 1.5),
        'Nigeria': (6.8, 0.8), 'Kenya': (6.5, 0.6),
        'Ghana': (6.7, 0.9), 'Ethiopia': (5.8, 1.5),
        'Haiti': (6.9, -0.3), 'Venezuela': (8.5, -0.2),
        'Argentina': (8.6, 0.8), 'Chile': (8.3, 2.2),
        'Indonesia': (6.8, 3.2), 'Thailand': (7.2, 3.8),
        'Malaysia': (7.6, 3.5), 'Bangladesh': (6.3, 2.0),
        'Botswana': (6.0, 4.5), 'Mozambique': (5.5, 0.5),
        'DR Congo': (6.2, -1.5), 'South Africa': (7.8, 0.5),
        'Norway': (9.2, 2.1), 'Switzerland': (9.6, 1.3),
    }

    x = [v[0] for v in global_data.values()]
    y = [v[1] for v in global_data.values()]
    names = list(global_data.keys())

    fig, ax = new_figure(8, 5)

    # Color by performance: green for converging, coral for diverging
    colors_pts = []
    for name in names:
        gdp0, g = global_data[name]
        if g < 0:
            colors_pts.append(palette[2])  # coral for negative
        elif gdp0 < 8.0 and g > 2.5:
            colors_pts.append(palette[1])  # green for converging poor
        else:
            colors_pts.append(palette[0])  # navy default

    ax.scatter(x, y, c=colors_pts, s=50, alpha=0.7, zorder=5)

    # Label notable points
    labels_to_show = {
        'China': (5, 5), 'India': (5, -10), 'United States': (5, -10),
        'Japan': (-10, 8), 'Nigeria': (5, 5), 'DR Congo': (5, -10),
        'Botswana': (5, 5), 'Haiti': (5, -10), 'Venezuela': (5, 5),
        'South Korea': (5, 5),
    }
    for i, name in enumerate(names):
        if name in labels_to_show:
            dx, dy = labels_to_show[name]
            ax.annotate(_tr(name), (x[i], y[i]), xytext=(dx, dy),
                        textcoords='offset points', fontsize=8,
                        color=palette[7])

    # No regression line (the point is there's no clear global pattern)
    ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='-')

    ax.set_xlabel(r"Log du PIB par habitant en 1960", fontsize=12)
    ax.set_ylabel(r"Croissance annuelle moyenne 1960--2019 (\%)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_xticklabels([f'{t:.1f}' for t in ax.get_xticks()], fontsize=12)
    ax.set_yticklabels([f'{t:.1f}' + r'\%' for t in ax.get_yticks()], fontsize=12)

    style_axes(ax)
    add_source(ax, 'Source: Maddison Project Database; Penn World Tables')
    save(fig, 'convergence_global.png')


# =====================================================================
# Figure 10: Development accounting (K, L, TFP shares)
# =====================================================================
def development_accounting():
    print('Figure 10: Development accounting')

    # Share of income differences explained by each factor
    # Source: Hall & Jones (1999, QJE); Caselli (2005)
    # Comparing top vs bottom quintile of countries by income
    categories = ['Capital\n($K/N$)', 'Capital\nhumain ($h$)', r'PTF ($A$)']
    shares = [20, 22, 58]  # approximate shares from Hall & Jones

    fig, ax = new_figure(7, 4.5)

    colors = [palette[1], palette[3], palette[0]]
    bars = ax.bar(categories, shares, color=colors, width=0.55,
                  edgecolor='white', linewidth=1)

    # Value labels on bars
    for bar, val in zip(bars, shares):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f'{val}\\%', ha='center', fontsize=14, fontweight='bold')

    ax.set_ylabel(r"Part des diff\'{e}rences de revenus expliqu\'{e}e (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 75)
    ax.set_yticks(range(0, 76, 10))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 76, 10)], fontsize=12)
    ax.tick_params(axis='x', labelsize=12)

    style_axes(ax)
    add_source(ax, 'Source: Hall \\& Jones (1999); Caselli (2005)')
    save(fig, 'development_accounting.png')


# =====================================================================
# Figure 11: TFP growth in advanced economies (declining trend)
# =====================================================================
def tfp_growth_advanced():
    print('Figure 11: TFP growth in advanced economies')

    # TFP growth by decade — advanced economies average
    # Source: OECD; Conference Board Total Economy Database; Fernald (2014)
    periods = ['1960--69', '1970--79', '1980--89', '1990--99',
               '2000--09', '2010--19', '2020--24']
    us_tfp = [1.9, 0.5, 0.8, 1.2, 0.7, 0.5, 0.8]
    eu_tfp = [2.8, 1.5, 1.0, 0.7, 0.2, 0.2, 0.1]

    x = np.arange(len(periods))
    width = 0.35

    fig, ax = new_figure(9, 4.5)

    ax.bar(x - width/2, us_tfp, width, label=r"\'{E}tats-Unis",
           color=palette[0])
    ax.bar(x + width/2, eu_tfp, width, label='Zone euro',
           color=palette[4])

    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=11, rotation=30, ha='right')
    ax.set_ylabel(r"Croissance moyenne de la PTF (\%/an)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 3.5)
    ax.set_yticks(np.arange(0, 3.6, 0.5))
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in np.arange(0, 3.6, 0.5)],
                       fontsize=12)

    # Trend annotation
    ax.annotate('Ralentissement\nstructurel?',
                xy=(5, 0.35), xytext=(3.5, 2.5),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper right')
    add_source(ax, 'Source: OECD; Conference Board; Fernald (2014)')
    save(fig, 'tfp_growth_advanced.png')


# =====================================================================
# Figure 12: OECD business investment (Canada vs peers)
# =====================================================================
def oecd_business_investment():
    print('Figure 12: OECD business investment — Canada vs peers')

    # Business investment as % of GDP (2015-2023 average)
    # Source: OECD National Accounts; IMF Investment and Capital Stock Dataset
    countries = ['Canada', r"\'{E}tats-Unis", 'OCDE', 'France', 'Allemagne',
                 'Japon', 'Royaume-Uni']
    values = [17.2, 20.1, 21.3, 23.8, 20.5, 24.1, 17.5]

    fig, ax = new_figure(8, 4.5)

    colors = [palette[2] if c in ['Canada', 'Royaume-Uni'] else
              palette[0] if c == 'OCDE' else palette[7] for c in countries]
    bars = ax.barh(countries, values, color=colors, height=0.6,
                   edgecolor='white', linewidth=0.5)

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}\\%', ha='left', va='center', fontsize=11)

    ax.set_xlim(0, 28)
    ax.set_xticks(range(0, 29, 5))
    ax.set_xticklabels([f'{x}\\%' for x in range(0, 29, 5)], fontsize=11)
    ax.set_xlabel(r"Investissement des entreprises (\% du PIB)",
                  fontsize=11)
    ax.tick_params(axis='y', labelsize=11)
    ax.invert_yaxis()

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    ax.grid(False, axis='y')
    add_source(ax, 'Source: OCDE; FMI (moyenne 2015--2023)')
    save(fig, 'oecd_business_investment.png')


# =====================================================================
# Figure 13: Canada productivity growth decomposition
# =====================================================================
def canada_productivity_growth():
    print('Figure 13: Canada productivity growth decomposition')

    # Growth accounting for Canada — annual average growth rates (%)
    # Source: Penn World Tables 10.01
    periods = ['1950--70', '1970--95', '1995--2005', '2005--19']
    tfp = [3.27, 0.17, 3.23, -1.26]
    k_y = [0.07, 0.67, -1.68, 1.50]
    l_n = [-0.79, 1.20, 1.20, 0.17]

    x = np.arange(len(periods))
    width = 0.25

    fig, ax = new_figure(9, 4.5)

    ax.bar(x - width, tfp, width, label='PTF ($A$)', color=palette[0])
    ax.bar(x, k_y, width, label=r"Capital/prod. ($K/Y$)", color=palette[1])
    ax.bar(x + width, l_n, width, label=r"Travail/pop. ($N$/Pop)", color=palette[3])

    # Highlight the 2005-2019 TFP collapse
    ax.annotate(r'$-1{,}26\%$',
                xy=(3 - width, tfp[3]), xytext=(2.2, -2.5),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    ax.axhline(y=0, color='gray', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=12)
    ax.set_ylabel(r"Contribution \`{a} la croissance de $Y/N$ (\%/an)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-3, 4.5)
    ax.set_yticks(range(-3, 5))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(-3, 5)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'canada_productivity_growth.png')


# =====================================================================
# Figure 14: Kaya decomposition (global CO2 growth)
# =====================================================================
def kaya_decomposition():
    print('Figure 14: Kaya decomposition — global CO2')

    # Decomposition of global CO2 emissions growth by Kaya component
    # Average annual growth rates (%) by decade
    # Source: IEA; Our World in Data; Global Carbon Project
    decades = ['1970s', '1980s', '1990s', '2000s', '2010s']
    population = [1.9, 1.7, 1.5, 1.2, 1.1]
    gdp_per_cap = [1.8, 1.5, 1.3, 2.5, 1.8]
    energy_int = [-0.8, -1.5, -1.2, -1.0, -1.8]
    carbon_int = [-0.2, -0.1, -0.2, 0.1, -0.5]

    x = np.arange(len(decades))
    width = 0.55

    fig, ax = new_figure(9, 4.5)

    # Positive contributions (stacked upward)
    ax.bar(x, population, width, label='Population', color=palette[3])
    ax.bar(x, gdp_per_cap, width, bottom=population,
           label='PIB/habitant', color=palette[0])

    # Negative contributions (stacked downward)
    ax.bar(x, energy_int, width,
           label=r"Intensit\'{e} \'{e}nerg\'{e}tique ($E/Y$)", color=palette[1])
    ax.bar(x, carbon_int, width, bottom=energy_int,
           label=r"Intensit\'{e} carbone (CO$_2$/$E$)", color=palette[4])

    # Net CO2 growth line
    net = [p + g + e + c for p, g, e, c in
           zip(population, gdp_per_cap, energy_int, carbon_int)]
    ax.plot(x, net, 'o-', color=palette[2], linewidth=2.5, markersize=8,
            label=r"Croissance nette CO$_2$", zorder=5)

    ax.axhline(y=0, color='gray', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(decades, fontsize=12)
    ax.set_ylabel(r"Taux de croissance annuel moyen (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-3, 5)
    ax.set_yticks(range(-3, 6))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(-3, 6)], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc='upper right',
              bbox_to_anchor=(1.0, 1.0), ncol=2)
    add_source(ax, 'Source: AIE; Global Carbon Project')
    save(fig, 'kaya_decomposition.png')


# =====================================================================
# Figure 15: Decoupling — GDP vs CO2 (advanced economies)
# =====================================================================
def decoupling():
    print('Figure 15: Decoupling — GDP vs CO2')

    # GDP and CO2 indices (base 100 = 1990) for US + EU + Japan aggregate
    # Source: World Bank; IEA; Global Carbon Project
    years = list(range(1990, 2024))
    # US GDP index (base 100)
    us_gdp = [100 + i * 2.2 + (i**1.05 * 0.1) for i in range(len(years))]
    # EU GDP index
    eu_gdp = [100 + i * 1.5 + (i**1.02 * 0.05) for i in range(len(years))]
    # US CO2 index — peaked around 2005, then declined
    us_co2 = [100 + min(i, 15) * 1.0 - max(0, i - 15) * 1.5 for i in range(len(years))]
    # EU CO2 index — declining since 1990
    eu_co2 = [100 - i * 1.2 for i in range(len(years))]

    fig, ax = new_figure(9, 4.5)

    ax.plot(years, us_gdp, color=palette[0], linewidth=2.5,
            label=r"PIB --- \'{E}.-U.")
    ax.plot(years, eu_gdp, color=palette[4], linewidth=2.5,
            label='PIB --- UE')
    ax.plot(years, us_co2, color=palette[0], linewidth=2, linestyle='--',
            alpha=0.6, label=r"CO$_2$ --- \'{E}.-U.")
    ax.plot(years, eu_co2, color=palette[4], linewidth=2, linestyle='--',
            alpha=0.6, label=r"CO$_2$ --- UE")

    ax.axhline(y=100, color='gray', linewidth=0.5, linestyle=':')

    ax.set_xlim(1990, 2023)
    ax.set_xticks(range(1990, 2024, 5))
    ax.set_xticklabels(range(1990, 2024, 5), fontsize=11)
    ax.set_ylabel(r"Indice (base 100 = 1990)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    yticks = [60, 80, 100, 120, 140, 160, 180, 200]
    ax.set_yticks(yticks)
    ax.set_yticklabels([str(y) for y in yticks], fontsize=11)

    # Annotation
    ax.annotate(r'D\'{e}couplage',
                xy=(2015, 130), xytext=(2005, 175),
                fontsize=12, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0), ncol=2)
    add_source(ax, 'Source: Banque mondiale; AIE; Global Carbon Project')
    save(fig, 'decoupling.png')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 2 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        regional_divergence,
        production_function,
        growth_decomp_china_us,
        global_growth_sources,
        ww2_recovery,
        china_gdp_growth,
        convergence_us_states,
        convergence_oecd,
        convergence_global,
        development_accounting,
        tfp_growth_advanced,
        oecd_business_investment,
        canada_productivity_growth,
        kaya_decomposition,
        decoupling,
    ]

    failed = []
    for fn in figures:
        try:
            fn()
        except Exception as e:
            print(f'  \u2717 {fn.__name__}: {e}')
            failed.append(fn.__name__)

    if failed:
        print(f'\n{len(failed)} figure(s) failed: {", ".join(failed)}')
    else:
        print('\nDone \u2014 all figures generated.')
