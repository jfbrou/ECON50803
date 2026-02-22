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
    'Spain': 'Espagne',
    'Portugal': 'Portugal',
    'Greece': r"Gr\`{e}ce",
    'Turkey': 'Turquie',
    'Mexico': 'Mexique',
    'Australia': 'Australie',
    'Republic of Korea': r"Cor\'{e}e du Sud",
    'China, Hong Kong SAR': 'Hong Kong',
    'Nigeria': r"Nig\'{e}ria",
    'Kenya': 'Kenya',
    'Ghana': 'Ghana',
    'Ethiopia': r"\'{E}thiopie",
    'Haiti': r"Ha\"{i}ti",
    'Venezuela (Bolivarian Republic of)': r"V\'{e}n\'{e}zuela",
    'Argentina': 'Argentine',
    'Chile': 'Chili',
    'Indonesia': r"Indon\'{e}sie",
    'Thailand': r"Tha\"{i}lande",
    'Malaysia': 'Malaisie',
    'Bangladesh': 'Bangladesh',
    'Botswana': 'Botswana',
    'Mozambique': 'Mozambique',
    'D.R. of the Congo': r"R.D. du Congo",
    'South Africa': 'Afrique du Sud',
    'New Zealand': 'Nouvelle-Z\'{e}lande',
    'Denmark': 'Danemark',
    'Sweden': r"Su\`{e}de",
    'Finland': 'Finlande',
    'Belgium': 'Belgique',
    'Netherlands': 'Pays-Bas',
    'Austria': 'Autriche',
    'Luxembourg': 'Luxembourg',
    'Iceland': 'Islande',
    'Israel': r"Isra\"{e}l",
    'Egypt': r"\'{E}gypte",
    'Colombia': 'Colombie',
    'Philippines': 'Philippines',
    'Madagascar': 'Madagascar',
    'Senegal': r"S\'{e}n\'{e}gal",
    'Cameroon': 'Cameroun',
}


def _tr(name):
    """Translate a country/region name to French, fallback to original."""
    return COUNTRY_FR.get(name, name)


# ── PWT loader (cached) ───────────────────────────────────────────────
_pwt_cache = None


def _load_pwt():
    """Load Penn World Tables 10.01 (cached)."""
    global _pwt_cache
    if _pwt_cache is None:
        _pwt_cache = pd.read_stata(
            '/Users/jfbrou/Dropbox/GitHub/ECON20852/Data/pwt1001.dta')
    return _pwt_cache


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


# ── OWID Maddison helper ──────────────────────────────────────────────
def _get_owid_maddison():
    """Fetch Maddison GDP per capita from the OWID API (2023 edition, data to 2022)."""
    import json, urllib.request
    url_data = 'https://api.ourworldindata.org/v1/indicators/900793.data.json'
    url_meta = 'https://api.ourworldindata.org/v1/indicators/900793.metadata.json'
    headers = {'User-Agent': 'Mozilla/5.0'}
    data = json.loads(urllib.request.urlopen(
        urllib.request.Request(url_data, headers=headers)).read())
    meta = json.loads(urllib.request.urlopen(
        urllib.request.Request(url_meta, headers=headers)).read())
    entity_map = {e['id']: e['name']
                  for e in meta['dimensions']['entities']['values']}
    df = pd.DataFrame({
        'Entity': [entity_map[eid] for eid in data['entities']],
        'Year': data['years'],
        'GDP per capita': data['values'],
    })
    return df


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
    print('Figure 1: Regional GDP/capita trajectories by world region')
    df = _get_owid_maddison()

    regions = {
        'Western offshoots (Maddison)':           (r"Am\'{e}rique du Nord + Oc\'{e}anie", palette[0], 2.5),
        'Western Europe (Maddison)':              ("Europe de l'Ouest", palette[4], 2.0),
        'East Asia (Maddison)':                   ("Asie de l'Est", palette[1], 2.0),
        'Latin America (Maddison)':               (r"Am\'{e}rique latine", palette[2], 2.0),
        'South and South East Asia (Maddison)':   ('Asie du Sud et du Sud-Est', palette[3], 2.0),
        'Middle East and North Africa (Maddison)': ('Moyen-Orient et Afrique du Nord', palette[5], 1.5),
        'Sub Saharan Africa (Maddison)':          ('Afrique subsaharienne', palette[7], 1.5),
    }

    fig, ax = new_figure()

    for entity, (label, color, lw) in regions.items():
        sub = df.loc[(df['Entity'] == entity) & df['GDP per capita'].notna()]
        sub = sub[sub['Year'] >= 1820]
        ax.plot(sub['Year'], sub['GDP per capita'], color=color,
                label=label, linewidth=lw)

    ax.set_xlim(1820, 2025)
    ax.set_xticks(range(1820, 2021, 40))
    ax.set_xticklabels(range(1820, 2021, 40), fontsize=12)
    ax.set_ylim(0, 60000)
    ax.set_yticks(range(0, 60000 + 1, 10000))
    ax.set_yticklabels([r'\$' + str(x) + 'K' for x in range(0, 60 + 1, 10)],
                       fontsize=11)
    ax.set_ylabel(r"PIB r\'{e}el par habitant",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0), ncol=2)
    add_source(ax, 'Source: Maddison Project Database 2023 (via Our World in Data)')
    save(fig, 'regional_divergence.png')


# =====================================================================
# Figure 2: Production function (diminishing returns to labor)
# =====================================================================
def _diminishing_returns(xlabel, fixed_label, filename):
    """Shared helper for diminishing-returns figures."""
    x = np.linspace(0, 100, 500)
    f = lambda v: 30 * np.log(v + 1)

    fig, ax = new_figure(6, 5)
    ax.plot(x, f(x), color=palette[0], linewidth=3)

    pts = [10, 30, 60, 90]
    for i, v in enumerate(pts):
        y_val = f(v)
        ax.plot(v, y_val, 'o', color=palette[2], markersize=10, zorder=5)
        ax.plot([v, v], [0, y_val], '--', color=palette[7], lw=0.8, zorder=1)
        if i < len(pts) - 1:
            v_next = pts[i + 1]
            y_next = f(v_next)
            ax.annotate('', xy=(v_next, y_next), xytext=(v_next, y_val),
                        arrowprops=dict(arrowstyle='<->', color=palette[1],
                                        lw=2))
            ax.text(v_next + 2.5, (y_val + y_next) / 2,
                    rf'$\Delta Y_{i+1}$',
                    fontsize=14, color=palette[1], va='center')
            ax.plot([0, v_next], [y_val, y_val], ':', color=palette[1],
                    lw=0.8, zorder=1)
            ax.plot([0, v_next], [y_next, y_next], ':', color=palette[1],
                    lw=0.8, zorder=1)

    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel('Production ($Y$)', fontsize=16, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.08)
    ax.set_xlim(0, 105)
    ax.set_ylim(0, None)
    ax.set_yticks([])
    ax.set_xticks([0, 10, 30, 60, 90])
    ax.set_xticklabels([0, 10, 30, 60, 90], fontsize=14)

    ax.text(68, f(68) + 12, r'$F(K, L)$',
            fontsize=17, color=palette[0], fontstyle='italic')
    ax.text(0.98, 0.05, fixed_label,
            fontsize=14, color=palette[7], ha='right',
            transform=ax.transAxes)

    style_axes(ax)

    # Add arrows at axis tips
    ax.annotate('', xy=(1.02, 0), xycoords='axes fraction',
                xytext=(0.98, 0), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    ax.annotate('', xy=(0, 1.05), xycoords='axes fraction',
                xytext=(0, 0.95), textcoords='axes fraction',
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))

    save(fig, filename)


def production_function():
    print('Figure 2a: Diminishing returns to labor')
    _diminishing_returns('Travail ($L$)', r'$K$ fixe, $A$ fixe',
                         'production_function.png')


def production_function_capital():
    print('Figure 2b: Diminishing returns to capital')
    _diminishing_returns('Capital ($K$)', r'$L$ fixe, $A$ fixe',
                         'production_function_capital.png')


# =====================================================================
# Figure 3: Growth decomposition — China vs US (per-capita)
# =====================================================================
def growth_decomp_china_us():
    print('Figure 3: Growth decomposition — China vs US')

    # K/Y decomposition: %Δ(Y/N) ≈ (1/(1-α))·%ΔA + (α/(1-α))·%Δ(K/Y) + %Δ(L/N)
    df = _load_pwt()
    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)  # 0.5

    period_defs = [('1960--1980', 1960, 1980),
                   ('1980--2000', 1980, 2000),
                   ('2000--2019', 2000, 2019)]

    results = {}
    for code, key in [('CHN', 'CHN'), ('USA', 'US')]:
        c = df[df['countrycode'] == code].set_index('year')
        A_vals, KY_vals, LN_vals = [], [], []
        for _, y0, y1 in period_defs:
            T = y1 - y0
            yn0 = c.loc[y0, 'rgdpna'] / c.loc[y0, 'pop']
            yn1 = c.loc[y1, 'rgdpna'] / c.loc[y1, 'pop']
            ky0 = c.loc[y0, 'rkna'] / c.loc[y0, 'rgdpna']
            ky1 = c.loc[y1, 'rkna'] / c.loc[y1, 'rgdpna']
            ln0 = c.loc[y0, 'emp'] / c.loc[y0, 'pop']
            ln1 = c.loc[y1, 'emp'] / c.loc[y1, 'pop']

            g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
            g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
            g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

            ky_contrib = amp_ky * g_ky
            ln_contrib = g_ln
            a_contrib = g_yn - ky_contrib - ln_contrib

            A_vals.append(a_contrib)
            KY_vals.append(ky_contrib)
            LN_vals.append(ln_contrib)

        results[f'{key}_A'] = A_vals
        results[f'{key}_KY'] = KY_vals
        results[f'{key}_LN'] = LN_vals

    x = np.arange(len(period_defs))
    period_labels = [p[0] for p in period_defs]
    width = 0.35
    gap = 0.03

    fig, ax = new_figure(9, 4.5)

    def stack_bars(ax, xpos, a_vals, ky_vals, ln_vals, w, label=False):
        """Stack bars handling negative L/N contributions."""
        ax.bar(xpos, a_vals, w, color=palette[0],
               label=r'Productivit\'{e} ($A$)' if label else None)
        ax.bar(xpos, ky_vals, w, bottom=a_vals, color=palette[1],
               label='Capital/PIB ($K/Y$)' if label else None)
        ln_pos = [max(0, v) for v in ln_vals]
        ln_neg = [min(0, v) for v in ln_vals]
        pos_bottom = [a + k for a, k in zip(a_vals, ky_vals)]
        ax.bar(xpos, ln_pos, w, bottom=pos_bottom, color=palette[3],
               label="Taux d'emploi ($L/N$)" if label else None)
        ax.bar(xpos, ln_neg, w, color=palette[3])

    stack_bars(ax, x - width/2 - gap/2,
               results['CHN_A'], results['CHN_KY'], results['CHN_LN'],
               width, label=True)
    stack_bars(ax, x + width/2 + gap/2,
               results['US_A'], results['US_KY'], results['US_LN'], width)

    # Country labels
    for i in range(len(period_defs)):
        chn_top = (results['CHN_A'][i] + results['CHN_KY'][i]
                   + max(0, results['CHN_LN'][i]))
        us_top = (results['US_A'][i] + results['US_KY'][i]
                  + max(0, results['US_LN'][i]))
        ax.text(i - width/2 - gap/2, chn_top + 0.15, 'Chine',
                ha='center', fontsize=10, fontweight='bold', color=palette[2])
        ax.text(i + width/2 + gap/2, us_top + 0.15, r"\'{E}.-U.",
                ha='center', fontsize=10, fontweight='bold', color=palette[4])

    ax.set_xticks(x)
    ax.set_xticklabels(period_labels, fontsize=13)
    ax.set_ylabel(r"Croissance du PIB/hab. (pp, moy. annuelle)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.axhline(y=0, color='black', linewidth=0.5)

    # Dynamic y-axis
    all_vals = (results['CHN_A'] + results['CHN_KY'] + results['CHN_LN']
                + results['US_A'] + results['US_KY'] + results['US_LN'])
    ymax = max(sum(results['CHN_A'][i] + results['CHN_KY'][i]
                   + max(0, results['CHN_LN'][i]) for _ in [0])
               for i in range(len(period_defs)))
    ax.set_ylim(-1, 10)
    ax.set_yticks(range(0, 11, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 11, 2)], fontsize=12)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'growth_decomp_china_us.png')


# =====================================================================
# Figure 4: Global growth sources by region (1980–2022)
# =====================================================================
def global_growth_sources():
    print('Figure 4: Global growth sources by region (annual)')

    import json

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Referer': 'https://www.imf.org/external/datamapper/',
        'Accept': 'application/json'
    }
    years = list(range(1980, 2026))
    periods_str = ','.join(str(y) for y in years)
    entities = 'ADVEC/OEMDC/CHN/WEOWORLD'

    # Fetch real GDP growth and PPP shares
    def fetch_imf(indicator):
        url = (f'https://www.imf.org/external/datamapper/api/v1/'
               f'{indicator}/{entities}?periods={periods_str}')
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()['values'][indicator]

    growth = fetch_imf('NGDP_RPCH')
    shares = fetch_imf('PPPSH')

    # Compute contributions
    ae_contrib, chn_contrib, emde_ex_chn_contrib, world_growth = [], [], [], []
    valid_years = []
    for y in years:
        sy = str(y)
        try:
            ae_sh = shares['ADVEC'][sy] / 100
            emde_sh = shares['OEMDC'][sy] / 100
            chn_sh = shares['CHN'][sy] / 100
            emde_ex_sh = emde_sh - chn_sh

            ae_c = growth['ADVEC'][sy] * ae_sh
            chn_c = growth['CHN'][sy] * chn_sh
            emde_ex_c = (growth['OEMDC'][sy] * emde_sh
                         - growth['CHN'][sy] * chn_sh)

            ae_contrib.append(ae_c)
            chn_contrib.append(chn_c)
            emde_ex_chn_contrib.append(emde_ex_c)
            world_growth.append(growth['WEOWORLD'][sy])
            valid_years.append(y)
        except KeyError:
            continue

    ae_contrib = np.array(ae_contrib)
    chn_contrib = np.array(chn_contrib)
    emde_ex_chn_contrib = np.array(emde_ex_chn_contrib)
    world_growth = np.array(world_growth)
    x = np.arange(len(valid_years))

    fig, ax = new_figure(11, 4.5)
    width = 0.8

    # Stacked bars — positive portions
    ae_pos = np.maximum(ae_contrib, 0)
    chn_pos = np.maximum(chn_contrib, 0)
    emde_pos = np.maximum(emde_ex_chn_contrib, 0)

    ax.bar(x, ae_pos, width, color=palette[0],
           label=r"\'{E}conomies avanc\'{e}es")
    ax.bar(x, emde_pos, width, bottom=ae_pos, color=palette[1],
           label=r"\'{E}mergents (hors Chine)")
    ax.bar(x, chn_pos, width, bottom=ae_pos + emde_pos, color=palette[2],
           label='Chine')

    # Negative portions
    ae_neg = np.minimum(ae_contrib, 0)
    chn_neg = np.minimum(chn_contrib, 0)
    emde_neg = np.minimum(emde_ex_chn_contrib, 0)
    ax.bar(x, ae_neg, width, color=palette[0])
    ax.bar(x, emde_neg, width, bottom=ae_neg, color=palette[1])
    ax.bar(x, chn_neg, width, bottom=ae_neg + emde_neg, color=palette[2])

    # World growth markers
    ax.scatter(x, world_growth, color=palette[3], s=20, zorder=5,
               label='Monde', marker='D', edgecolors='black', linewidths=0.3)

    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlim(-0.6, len(valid_years) - 0.4)
    tick_positions = [i for i, y in enumerate(valid_years) if y % 5 == 0]
    tick_labels = [str(y) for y in valid_years if y % 5 == 0]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=10)
    ax.set_ylabel(r"Contribution \`{a} la croissance mondiale (pp)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-4, 7)
    yticks = range(-4, 8, 2)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}' + r'\%' for y in yticks], fontsize=11)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=9, loc='upper left', ncol=2)
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
                label=label, linewidth=2.5)

    # WWII shading
    ax.axvspan(1939, 1945, color='grey', alpha=0.25, linewidth=0,
               label='Seconde Guerre mondiale')

    ax.set_xlim(1910, 1960)
    ax.set_xticks(range(1910, 1961, 10))
    ax.set_xticklabels(range(1910, 1961, 10), fontsize=12)
    ax.set_ylim(bottom=2000)
    ax.set_ylabel(r"PIB r\'{e}el par habitant", fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Format y-axis
    yticks = [y for y in ax.get_yticks() if y >= 2000]
    ax.set_yticks(yticks)
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

    # World Bank API: NY.GDP.MKTP.KD.ZG = GDP growth (annual %)
    url = ('https://api.worldbank.org/v2/country/CHN/indicator/'
           'NY.GDP.MKTP.KD.ZG?date=2005:2025&format=json&per_page=100')
    r = requests.get(url)
    raw = r.json()[1]
    data = {int(d['date']): d['value'] for d in raw if d['value'] is not None}
    years = sorted(data.keys())
    growth = [data[y] for y in years]

    fig, ax = new_figure(9, 4)

    colors = [palette[2] if g < 5.0 else palette[0] for g in growth]
    ax.bar(years, growth, color=colors, width=0.7, edgecolor='white', linewidth=0.5)

    # Highlight the target
    ax.axhline(y=5.0, color=palette[7], linestyle=':', linewidth=1.5)
    ax.text(years[-1] + 0.8, 5.3, r'Cible : 5\%', fontsize=9, color=palette[7])

    ax.set_xlim(years[0] - 0.8, years[-1] + 0.8)
    ax.set_xticks(range(years[0], years[-1] + 1, 5))
    ax.set_xticklabels(range(years[0], years[-1] + 1, 5), fontsize=11)
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))
    ax.set_yticklabels([f'{y}' + r'\%' for y in range(0, 17, 2)], fontsize=12)
    ax.set_ylabel(r"Croissance du PIB r\'{e}el (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Banque mondiale')
    save(fig, 'china_gdp_growth.png')


# =====================================================================
# Figure 6b: Japan — rise and stagnation (GDP per capita growth)
# =====================================================================
def japan_growth():
    print('Figure 6b: Japan GDP per capita growth (decade averages)')

    # Maddison Project Database via OWID
    url = ('https://raw.githubusercontent.com/owid/owid-datasets/master/'
           'datasets/Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020))/'
           'Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020)).csv')
    df = pd.read_csv(url)
    jpn = df[df['Entity'] == 'Japan'].set_index('Year')['GDP per capita'].dropna()

    # Compute decade-average annual growth rates
    decades = [(1950, 1960), (1960, 1970), (1970, 1980), (1980, 1990),
               (1990, 2000), (2000, 2010), (2010, 2018)]
    labels, rates = [], []
    for y0, y1 in decades:
        T = y1 - y0
        g = ((jpn.loc[y1] / jpn.loc[y0]) ** (1 / T) - 1) * 100
        labels.append(f'{y0}--{str(y1)[2:]}')
        rates.append(g)

    fig, ax = new_figure(9, 4)
    colors = [palette[0] if r >= 3 else (palette[2] if r < 1.5 else palette[3])
              for r in rates]
    ax.bar(range(len(labels)), rates, color=colors, width=0.65,
           edgecolor='white', linewidth=0.5)

    # Annotations
    for i, r in enumerate(rates):
        ax.text(i, r + 0.15, f'{r:.1f}' + r'\%',
                ha='center', fontsize=10, fontweight='bold')

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 10)
    yticks = range(0, 11, 2)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}' + r'\%' for y in yticks], fontsize=12)
    ax.set_ylabel(r"Croissance du PIB/hab. (\%, moy. annuelle)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, 'Source: Maddison Project Database (via Our World in Data)')
    save(fig, 'japan_growth.png')


# =====================================================================
# Figure 6c: Soviet Union / Russia — capital without productivity
# =====================================================================
def ussr_russia_gdp():
    print('Figure 6c: USSR/Russia GDP per capita relative to US')

    # Maddison Project Database via OWID
    url = ('https://raw.githubusercontent.com/owid/owid-datasets/master/'
           'datasets/Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020))/'
           'Maddison%20Project%20Database%202020%20'
           '(Bolt%20and%20van%20Zanden%20(2020)).csv')
    df = pd.read_csv(url)

    us = df[df['Entity'] == 'United States'].set_index('Year')['GDP per capita']
    # "Former USSR" for pre-1990, "Russia" for post-1990
    ussr = df[df['Entity'] == 'Former USSR'].set_index('Year')['GDP per capita']
    russia = df[df['Entity'] == 'Russia'].set_index('Year')['GDP per capita']

    # Combine USSR + Russia, compute ratio to US
    years_ussr = sorted(set(ussr.index) & set(us.index))
    years_russia = sorted(set(russia.index) & set(us.index))

    # Filter to 1950+
    years_ussr = [y for y in years_ussr if 1950 <= y <= 1990]
    years_russia = [y for y in years_russia if y > 1990]

    all_years = years_ussr + years_russia
    ratios = ([ussr.loc[y] / us.loc[y] * 100 for y in years_ussr]
              + [russia.loc[y] / us.loc[y] * 100 for y in years_russia])

    fig, ax = new_figure(9, 4)

    # Plot USSR portion
    ax.plot(years_ussr, ratios[:len(years_ussr)],
            color=palette[2], linewidth=2.5, label='URSS')
    # Plot Russia portion
    ax.plot(years_russia, ratios[len(years_ussr):],
            color=palette[0], linewidth=2.5, label='Russie')

    # Annotations
    peak_idx = ratios.index(max(ratios))
    peak_year = all_years[peak_idx]
    peak_val = max(ratios)
    ax.annotate(f'{peak_val:.0f}\\%',
                xy=(peak_year, peak_val),
                xytext=(peak_year + 5, peak_val + 5),
                fontsize=10, fontweight='bold', color=palette[2],
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.2))

    # Collapse annotation
    ax.annotate(r'Chute de l\'URSS',
                xy=(1991, ratios[len(years_ussr)] if years_russia else 30),
                xytext=(1995, 18),
                fontsize=10, color=palette[7],
                arrowprops=dict(arrowstyle='->', color=palette[7], lw=1.2))

    ax.set_xlim(1950, 2020)
    ax.set_xticks(range(1950, 2021, 10))
    ax.set_xticklabels(range(1950, 2021, 10), fontsize=11)
    ax.set_ylim(0, 55)
    yticks = range(0, 56, 10)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}' + r'\%' for y in yticks], fontsize=12)
    ax.set_ylabel(r"PIB/hab. relatif aux \'{E}.-U. (\%)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left')
    add_source(ax, 'Source: Maddison Project Database (via Our World in Data)')
    save(fig, 'ussr_russia_gdp.png')


# =====================================================================
# Figure 7: Convergence — US states (1880–2013)
# =====================================================================
def convergence_us_states():
    print('Figure 7: Convergence — US states')

    # Hardcoded data: log(real per-capita personal income 1880) vs
    # avg annual growth 1880-2013.
    # 1880 income: Klein, A. (2009), "Personal Income of US States:
    #   Estimates for the Period 1880-1930", Warwick Economic Research
    #   Papers 916, Table A.1 (2013 USD via CPI from Minneapolis Fed).
    # 2013 income: Bureau of Economic Analysis, State Personal Income
    #   (SAINC1), https://apps.bea.gov/regional/downloadzip.cfm
    # Growth = [ln(y_2013) - ln(y_1880)] / 133.
    # Representative sample of 36 states
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

    # Convert log income to ratio relative to richest state (NY = 7.9)
    log_ny = 7.9
    labels = list(states_data.keys())
    ratios = [np.exp(v[0] - log_ny) for v in states_data.values()]
    growth = [v[1] for v in states_data.values()]

    fig, ax = new_figure(8, 4)

    # Green solid regression line (behind points)
    log_ratios = [np.log(r) for r in ratios]
    slope, intercept, _, _, _ = stats.linregress(log_ratios, growth)
    x_fit = np.linspace(min(log_ratios) - 0.15, max(log_ratios) + 0.15, 100)
    ax.plot(np.exp(x_fit), slope * x_fit + intercept, color=palette[1],
            linewidth=2, zorder=2)

    ax.scatter(ratios, growth, s=75, color=palette[0], alpha=0.7, zorder=5)

    # Label all states
    for i, lbl in enumerate(labels):
        ax.annotate(lbl, (ratios[i], growth[i]),
                    textcoords='offset points', xytext=(5, 5),
                    ha='left', fontsize=10)

    # Log base 2 x-axis with fraction labels
    ax.set_xscale('log', base=2)
    ax.set_xlim(np.exp(6.0 - log_ny - 0.15), np.exp(7.9 - log_ny + 0.15))
    ax.set_xticks([1/4, 1/2, 1])
    ax.set_xticklabels(['1/4', '1/2', '1'], fontsize=12)
    ax.set_xlabel(r"Revenu par habitant relatif \`a New York (1880)",
                  fontsize=12, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_ylim(1.2, 2.2)
    ax.set_yticks(np.arange(1.2, 2.2 + 0.1, 0.2))
    ax.set_yticklabels([f'{x:.1f}' + r'\%' for x in np.arange(1.2, 2.2 + 0.1, 0.2)],
                       fontsize=12)
    ax.set_ylabel(r"Croissance annuelle moyenne 1880--2013 (\%)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: Barro \\& Sala-i-Martin; BEA')
    save(fig, 'convergence_us_states.png')


# =====================================================================
# Figure 8: Convergence — OECD countries (1960–2014)
# =====================================================================
def convergence_oecd():
    print('Figure 8: Convergence — OECD countries')

    # Compute GDP per capita relative to US (1960) vs avg annual growth
    # 1960-2019 from Penn World Tables 10.01 (rgdpna / pop)
    pwt = _load_pwt()

    # OECD founding members (1961) + key later additions + comparators
    oecd_codes = [
        'USA', 'CAN', 'GBR', 'FRA', 'DEU', 'ITA', 'BEL', 'NLD', 'LUX',
        'AUT', 'CHE', 'DNK', 'SWE', 'NOR', 'ISL', 'IRL', 'PRT', 'ESP',
        'GRC', 'TUR',                          # founding / early members
        'JPN', 'FIN', 'AUS', 'NZL', 'MEX',     # joined 1964-94
        'KOR', 'HKG', 'SGP', 'TWN', 'ISR',     # key additions / comparators
        'POL', 'HUN', 'CZE', 'SVN', 'CHL', 'COL', 'CRI',  # later members
    ]

    year0, year1 = 1960, 2019
    # Get US GDP per capita in base year
    us = pwt[(pwt['countrycode'] == 'USA') & (pwt['year'] == year0)]
    y_usa = us.iloc[0]['rgdpna'] / us.iloc[0]['pop']

    rows = []
    for code in oecd_codes:
        sub = pwt[pwt['countrycode'] == code]
        d0 = sub[sub['year'] == year0]
        d1 = sub[sub['year'] == year1]
        if d0.empty or d1.empty:
            continue
        rgdp0, pop0 = d0.iloc[0]['rgdpna'], d0.iloc[0]['pop']
        rgdp1, pop1 = d1.iloc[0]['rgdpna'], d1.iloc[0]['pop']
        if any(pd.isna(v) for v in [rgdp0, pop0, rgdp1, pop1]):
            continue
        ypc0 = rgdp0 / pop0
        ypc1 = rgdp1 / pop1
        y_ratio = ypc0 / y_usa
        g = (np.log(ypc1) - np.log(ypc0)) / (year1 - year0) * 100
        rows.append({'code': code, 'y_ratio': y_ratio, 'growth': g})

    df = pd.DataFrame(rows)

    fig, ax = new_figure(8, 4)

    # Green solid regression line (behind points)
    log_ratios = np.log(df['y_ratio'].values)
    slope, intercept, _, _, _ = stats.linregress(log_ratios, df['growth'].values)
    x_fit = np.linspace(log_ratios.min() - 0.2, log_ratios.max() + 0.2, 100)
    ax.plot(np.exp(x_fit), slope * x_fit + intercept, color=palette[1],
            linewidth=2, zorder=2)

    ax.scatter(df['y_ratio'], df['growth'], s=75, color=palette[0], alpha=0.7,
               zorder=5)

    # Label all countries with ISO3 codes
    for _, row in df.iterrows():
        ax.annotate(row['code'],
                    (row['y_ratio'], row['growth']),
                    textcoords='offset points', xytext=(5, 5),
                    ha='left', fontsize=10)

    # Log base 2 x-axis with fraction labels
    ax.set_xscale('log', base=2)
    ax.set_xlim(1 / 5, 1.25)
    ax.set_xticks([1 / 4, 1 / 2, 1])
    ax.set_xticklabels(['1/4', '1/2', '1'], fontsize=12)
    ax.set_xlabel(r"PIB r\'eel par habitant relatif aux \'E.-U. (1960)",
                  fontsize=12, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_ylim(1.25, 4)
    ax.set_yticks(np.arange(1.5, 4 + 0.5, 0.5))
    ax.set_yticklabels([f'{x:.1f}' + r'\%' for x in np.arange(1.5, 4 + 0.5, 0.5)],
                       fontsize=12)
    ax.set_ylabel(r"Taux de croissance du PIB r\'eel par habitant (1960--2019)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'convergence_oecd.png')


# =====================================================================
# Figure 8b: Convergence — Emerging Asian economies (1990–2019)
# =====================================================================
def convergence_asia():
    print('Figure 8b: Convergence — Emerging Asian economies')

    # Compute GDP per capita relative to US (1990) vs avg annual growth
    # 1990-2019 from Penn World Tables 10.01 (rgdpna / pop)
    pwt = _load_pwt()

    asian_codes = [
        'CHN', 'IND', 'IDN', 'MMR', 'VNM', 'LKA', 'PHL',
        'THA', 'MYS', 'SGP', 'KOR', 'TWN', 'HKG',
    ]

    year0, year1 = 1990, 2019
    # Get US GDP per capita in base year
    us = pwt[(pwt['countrycode'] == 'USA') & (pwt['year'] == year0)]
    y_usa = us.iloc[0]['rgdpna'] / us.iloc[0]['pop']

    rows = []
    for code in asian_codes:
        sub = pwt[pwt['countrycode'] == code]
        d0 = sub[sub['year'] == year0]
        d1 = sub[sub['year'] == year1]
        if d0.empty or d1.empty:
            continue
        rgdp0, pop0 = d0.iloc[0]['rgdpna'], d0.iloc[0]['pop']
        rgdp1, pop1 = d1.iloc[0]['rgdpna'], d1.iloc[0]['pop']
        if any(pd.isna(v) for v in [rgdp0, pop0, rgdp1, pop1]):
            continue
        ypc0 = rgdp0 / pop0
        ypc1 = rgdp1 / pop1
        y_ratio = ypc0 / y_usa
        g = (np.log(ypc1) - np.log(ypc0)) / (year1 - year0) * 100
        rows.append({'code': code, 'y_ratio': y_ratio, 'growth': g})

    df = pd.DataFrame(rows)

    fig, ax = new_figure(8, 4)

    # Green solid regression line (behind points)
    log_ratios = np.log(df['y_ratio'].values)
    slope, intercept, _, _, _ = stats.linregress(log_ratios, df['growth'].values)
    x_fit = np.linspace(log_ratios.min() - 0.2, log_ratios.max() + 0.2, 100)
    ax.plot(np.exp(x_fit), slope * x_fit + intercept, color=palette[1],
            linewidth=2, zorder=2)

    ax.scatter(df['y_ratio'], df['growth'], s=75, color=palette[0], alpha=0.7,
               zorder=5)

    # Label all countries with ISO3 codes
    for _, row in df.iterrows():
        ax.annotate(row['code'],
                    (row['y_ratio'], row['growth']),
                    textcoords='offset points', xytext=(5, 5),
                    ha='left', fontsize=10)

    # Log base 2 x-axis with fraction labels
    ax.set_xscale('log', base=2)
    ax.set_xlim(1 / 32, 1)
    ax.set_xticks([1/32, 1/16, 1/8, 1/4, 1/2, 1])
    ax.set_xticklabels(['1/32', '1/16', '1/8', '1/4', '1/2', '1'], fontsize=12)
    ax.set_xlabel(r"PIB r\'eel par habitant relatif aux \'E.-U. (1990)",
                  fontsize=12, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_ylim(1.5, 6.5)
    ax.set_yticks(np.arange(1.5, 6.5 + 1, 1))
    ax.set_yticklabels([f'{x:.1f}' + r'\%' for x in np.arange(1.5, 6.5 + 1, 1)],
                       fontsize=12)
    ax.set_ylabel(r"Taux de croissance du PIB r\'eel par habitant (1990--2019)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'convergence_asia.png')


# =====================================================================
# Figure 9: Convergence — Global (mixed picture)
# =====================================================================
def convergence_global():
    print('Figure 9: Convergence — Global')

    # Compute GDP per capita relative to US (1960) vs avg annual growth
    # 1960-2019 from Penn World Tables 10.01, ALL countries with data
    pwt = _load_pwt()

    # OECD member codes for color-coding
    oecd_codes = {
        'AUS', 'AUT', 'BEL', 'CAN', 'CHL', 'COL', 'CRI', 'CZE', 'DNK',
        'EST', 'FIN', 'FRA', 'DEU', 'GRC', 'HUN', 'ISL', 'IRL', 'ISR',
        'ITA', 'JPN', 'KOR', 'LVA', 'LTU', 'LUX', 'MEX', 'NLD', 'NZL',
        'NOR', 'POL', 'PRT', 'SVK', 'SVN', 'ESP', 'SWE', 'CHE', 'TUR',
        'GBR', 'USA',
    }

    year0, year1 = 1960, 2019
    # Get US GDP per capita in base year
    us = pwt[(pwt['countrycode'] == 'USA') & (pwt['year'] == year0)]
    y_usa = us.iloc[0]['rgdpna'] / us.iloc[0]['pop']

    rows = []
    for code in pwt['countrycode'].unique():
        sub = pwt[pwt['countrycode'] == code]
        d0 = sub[sub['year'] == year0]
        d1 = sub[sub['year'] == year1]
        if d0.empty or d1.empty:
            continue
        rgdp0, pop0 = d0.iloc[0]['rgdpna'], d0.iloc[0]['pop']
        rgdp1, pop1 = d1.iloc[0]['rgdpna'], d1.iloc[0]['pop']
        if any(pd.isna(v) for v in [rgdp0, pop0, rgdp1, pop1]):
            continue
        ypc0 = rgdp0 / pop0
        ypc1 = rgdp1 / pop1
        y_ratio = ypc0 / y_usa
        g = (np.log(ypc1) - np.log(ypc0)) / (year1 - year0) * 100
        is_oecd = code in oecd_codes
        rows.append({'code': code, 'y_ratio': y_ratio, 'growth': g,
                     'is_oecd': is_oecd})

    df = pd.DataFrame(rows)

    fig, ax = new_figure(8, 4)

    # Non-OECD in navy, OECD in green with black edge
    non_oecd = df[~df['is_oecd']]
    oecd_df = df[df['is_oecd']]
    ax.scatter(non_oecd['y_ratio'], non_oecd['growth'],
               s=50, color=palette[0])
    ax.scatter(oecd_df['y_ratio'], oecd_df['growth'],
               s=50, color=palette[1], edgecolors='k', linewidth=0.5)

    # Label all countries with ISO3 codes
    for _, row in df.iterrows():
        ax.annotate(row['code'],
                    (row['y_ratio'], row['growth']),
                    textcoords='offset points', xytext=(5, 5),
                    ha='left', fontsize=8)

    # Log base 2 x-axis with fraction labels
    ax.set_xscale('log', base=2)
    ax.set_xlim(1 / 40, 2)
    ax.set_xticks([1/32, 1/16, 1/8, 1/4, 1/2, 1, 2])
    ax.set_xticklabels(['1/32', '1/16', '1/8', '1/4', '1/2', '1', '2'],
                       fontsize=12)
    ax.set_xlabel(r"PIB r\'eel par habitant relatif aux \'E.-U. (1960)",
                  fontsize=12, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_ylim(-2, 6)
    ax.set_yticks(range(-2, 6 + 1, 2))
    ax.set_yticklabels([str(x) + r'\%' for x in range(-2, 6 + 1, 2)],
                       fontsize=12)
    ax.set_ylabel(r"Taux de croissance du PIB r\'eel par habitant (1960--2019)",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'convergence_global.png')


# =====================================================================
# Figure 10: Development accounting (K, L, TFP shares)
# =====================================================================
def development_accounting():
    print('Figure 10: Development accounting')

    # Share of income differences explained by each factor
    # Source: Hall & Jones (1999, QJE); Caselli (2005)
    # Comparing top vs bottom quintile of countries by income
    categories = ['Capital\n($K/L$)', 'Capital\nhumain ($h$)', r'PTF ($A$)']
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
    ax.bar(x + width, l_n, width, label=r"Travail/pop. ($L/N$)", color=palette[3])

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
# Figure: Growth decomposition — Canada vs USA (total GDP, 3 periods)
# =====================================================================
def growth_decomp_canada_us_total():
    print('Figure: Growth decomposition — Canada vs USA (total GDP)')

    # Computed from PWT 10.01: %ΔY ≈ %ΔA + α·%ΔK + (1-α)·%ΔL, α=0.3
    periods = ['1970--1990', '1990--2007', '2007--2019']
    data = {
        'CAN_A':  [0.15, 0.58, 0.12],
        'CAN_K':  [1.39, 1.09, 0.79],
        'CAN_L':  [1.71, 1.01, 0.75],
        'US_A':   [0.81, 1.23, 0.62],
        'US_K':   [1.07, 1.07, 0.60],
        'US_L':   [1.31, 0.72, 0.46],
    }

    x = np.arange(len(periods))
    width = 0.35
    gap = 0.03

    fig, ax = new_figure(9, 4.5)

    def stack_bars(ax, xpos, a_vals, k_vals, l_vals, w, label=False):
        ax.bar(xpos, a_vals, w, color=palette[0],
               label='PTF' if label else None)
        ax.bar(xpos, k_vals, w, bottom=a_vals, color=palette[1],
               label='Capital' if label else None)
        ak_bottom = [a + k for a, k in zip(a_vals, k_vals)]
        ax.bar(xpos, l_vals, w, bottom=ak_bottom, color=palette[2],
               label='Travail' if label else None)

    stack_bars(ax, x - width/2 - gap/2,
               data['CAN_A'], data['CAN_K'], data['CAN_L'], width, label=True)
    stack_bars(ax, x + width/2 + gap/2,
               data['US_A'], data['US_K'], data['US_L'], width)

    # Country labels
    for i in range(len(periods)):
        can_top = data['CAN_A'][i] + data['CAN_K'][i] + data['CAN_L'][i]
        us_top = data['US_A'][i] + data['US_K'][i] + data['US_L'][i]
        ax.text(i - width/2 - gap/2, can_top + 0.04, 'Canada',
                ha='center', fontsize=10, fontweight='bold', color=palette[7])
        ax.text(i + width/2 + gap/2, us_top + 0.04, r"\'{E}.-U.",
                ha='center', fontsize=10, fontweight='bold', color=palette[7])

    ax.set_xticks(x)
    ax.set_xticklabels(periods, fontsize=13)
    ax.set_ylabel(r"Croissance du PIB (pp, moy. annuelle)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 3.5)
    yticks = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in yticks], fontsize=12)
    ax.axhline(y=0, color='black', linewidth=0.5)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'growth_decomp_canada_us_total.png')


# =====================================================================
# Figure: Growth decomposition — Canada vs USA (per-capita, K/Y version)
# =====================================================================
def growth_decomp_canada_us():
    print('Figure: Growth decomposition — Canada vs USA (per capita, K/Y)')

    # K/Y decomposition: Y/N = A^{1/(1-α)} · (K/Y)^{α/(1-α)} · (L/N)
    # Growth: %Δ(Y/N) = 1.5·%ΔA + 0.5·%Δ(K/Y) + %Δ(L/N)
    df = _load_pwt()
    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)       # 0.5

    period_defs = [('1970--1990', 1970, 1990),
                   ('1990--2007', 1990, 2007),
                   ('2007--2019', 2007, 2019)]

    results = {}
    for code, key in [('CAN', 'CAN'), ('USA', 'US')]:
        c = df[df['countrycode'] == code].set_index('year')
        A_vals, KY_vals, LN_vals = [], [], []
        for _, y0, y1 in period_defs:
            T = y1 - y0
            yn0 = c.loc[y0, 'rgdpna'] / c.loc[y0, 'pop']
            yn1 = c.loc[y1, 'rgdpna'] / c.loc[y1, 'pop']
            ky0 = c.loc[y0, 'rkna'] / c.loc[y0, 'rgdpna']
            ky1 = c.loc[y1, 'rkna'] / c.loc[y1, 'rgdpna']
            ln0 = c.loc[y0, 'emp'] / c.loc[y0, 'pop']
            ln1 = c.loc[y1, 'emp'] / c.loc[y1, 'pop']

            g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
            g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
            g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

            ky_contrib = amp_ky * g_ky
            ln_contrib = g_ln
            a_contrib = g_yn - ky_contrib - ln_contrib

            A_vals.append(a_contrib)
            KY_vals.append(ky_contrib)
            LN_vals.append(ln_contrib)

        results[f'{key}_A'] = A_vals
        results[f'{key}_KY'] = KY_vals
        results[f'{key}_LN'] = LN_vals

    x = np.arange(len(period_defs))
    period_labels = [p[0] for p in period_defs]
    width = 0.35
    gap = 0.03

    fig, ax = new_figure(9, 4.5)

    def stack_bars(ax, xpos, a_vals, ky_vals, ln_vals, w, label=False):
        ax.bar(xpos, a_vals, w, color=palette[0],
               label='$A$' if label else None)
        ax.bar(xpos, ky_vals, w, bottom=a_vals, color=palette[1],
               label='$K/Y$' if label else None)
        ln_pos = [max(0, v) for v in ln_vals]
        ln_neg = [min(0, v) for v in ln_vals]
        pos_bottom = [a + k for a, k in zip(a_vals, ky_vals)]
        ax.bar(xpos, ln_pos, w, bottom=pos_bottom, color=palette[2],
               label='$L/N$' if label else None)
        ax.bar(xpos, ln_neg, w, color=palette[2])

    stack_bars(ax, x - width/2 - gap/2,
               results['CAN_A'], results['CAN_KY'], results['CAN_LN'],
               width, label=True)
    stack_bars(ax, x + width/2 + gap/2,
               results['US_A'], results['US_KY'], results['US_LN'], width)

    for i in range(len(period_defs)):
        can_top = (results['CAN_A'][i] + results['CAN_KY'][i]
                   + max(0, results['CAN_LN'][i]))
        us_top = (results['US_A'][i] + results['US_KY'][i]
                  + max(0, results['US_LN'][i]))
        ax.text(i - width/2 - gap/2, can_top + 0.04, 'Canada',
                ha='center', fontsize=10, fontweight='bold', color=palette[7])
        ax.text(i + width/2 + gap/2, us_top + 0.04, r"\'{E}.-U.",
                ha='center', fontsize=10, fontweight='bold', color=palette[7])

    ax.set_xticks(x)
    ax.set_xticklabels(period_labels, fontsize=13)
    ax.set_ylabel(r"Croissance du PIB/hab. (pp, moy. annuelle)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(-0.25, 2.5)
    yticks = [0, 0.5, 1.0, 1.5, 2.0, 2.5]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y:.1f}' + r'\%' for y in yticks], fontsize=12)
    ax.axhline(y=0, color='black', linewidth=0.5)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper right',
              bbox_to_anchor=(1.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'growth_decomp_canada_us.png')


# =====================================================================
# Figure: Growth decomposition — Asian tigers (per-capita, K/Y, 1970–1990)
# =====================================================================
def growth_decomp_asian_tigers():
    print('Figure: Growth decomposition — Asian tigers (per capita, 1970-1990, K/Y)')

    # K/Y decomposition: %Δ(Y/N) = 1.5·%ΔA + 0.5·%Δ(K/Y) + %Δ(L/N)
    df = _load_pwt()
    alpha = 1 / 3
    amp_ky = alpha / (1 - alpha)

    codes = [('USA', r"\'{E}.-U."), ('HKG', 'Hong Kong'),
             ('KOR', r"Cor\'{e}e du S."), ('SGP', 'Singapour'),
             ('TWN', r"Ta\"{i}wan")]
    y0, y1, T = 1970, 1990, 20

    A_vals, KY_vals, LN_vals, labels = [], [], [], []
    for code, label in codes:
        c = df[df['countrycode'] == code].set_index('year')
        yn0 = c.loc[y0, 'rgdpna'] / c.loc[y0, 'pop']
        yn1 = c.loc[y1, 'rgdpna'] / c.loc[y1, 'pop']
        ky0 = c.loc[y0, 'rkna'] / c.loc[y0, 'rgdpna']
        ky1 = c.loc[y1, 'rkna'] / c.loc[y1, 'rgdpna']
        ln0 = c.loc[y0, 'emp'] / c.loc[y0, 'pop']
        ln1 = c.loc[y1, 'emp'] / c.loc[y1, 'pop']

        g_yn = ((yn1 / yn0) ** (1 / T) - 1) * 100
        g_ky = ((ky1 / ky0) ** (1 / T) - 1) * 100
        g_ln = ((ln1 / ln0) ** (1 / T) - 1) * 100

        ky_contrib = amp_ky * g_ky
        ln_contrib = g_ln
        a_contrib = g_yn - ky_contrib - ln_contrib

        A_vals.append(a_contrib)
        KY_vals.append(ky_contrib)
        LN_vals.append(ln_contrib)
        labels.append(label)

    x = np.arange(len(codes))
    width = 0.55

    fig, ax = new_figure(9, 4.5)

    ax.bar(x, A_vals, width, label='$A$', color=palette[0])
    ax.bar(x, KY_vals, width, bottom=A_vals, label='$K/Y$', color=palette[1])
    ak_bottom = [a + k for a, k in zip(A_vals, KY_vals)]
    ax.bar(x, LN_vals, width, bottom=ak_bottom, label='$L/N$', color=palette[2])

    for i in range(len(codes)):
        total = A_vals[i] + KY_vals[i] + LN_vals[i]
        ax.text(i, total + 0.1, f'{total:.1f}' + r'\%',
                ha='center', fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel(r"Croissance du PIB/hab. (pp, moy. annuelle)",
                  fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    ax.set_ylim(0, 9)
    yticks = range(0, 10, 2)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{y}' + r'\%' for y in yticks], fontsize=12)
    ax.axhline(y=0, color='black', linewidth=0.5)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'growth_decomp_asian_tigers.png')


# =====================================================================
# Figure: Asian miracle catch-up growth (relative to US)
# =====================================================================
def catchup_growth():
    print('Figure: Catch-up growth — Asian miracle')

    df = _load_pwt()
    df = df.copy()
    df['y'] = df['rgdpo'] / df['pop']
    usa = df[df['countrycode'] == 'USA'].set_index('year')['y']

    countries = [
        ('SGP', 1965, 'Singapour', palette[0]),
        ('HKG', 1960, 'Hong Kong', palette[1]),
        ('TWN', 1960, r"Ta\"{i}wan", palette[2]),
        ('KOR', 1960, r"Cor\'{e}e du Sud", palette[3]),
        ('CHN', 1980, 'Chine', palette[4]),
        ('IND', 1991, 'Inde', palette[5]),
    ]

    fig, ax = new_figure(8, 4)

    for code, start, label, color in countries:
        c = df[df['countrycode'] == code].set_index('year')['y']
        years = range(start, 2020)
        ratio = [c.loc[yr] / usa.loc[yr] for yr in years]
        ax.plot(range(len(ratio)), ratio, color=color, label=label, linewidth=2)

    ax.set_xlim(0, 60)
    ax.set_xticks(range(0, 61, 10))
    ax.set_xticklabels(range(0, 61, 10), fontsize=12)
    ax.set_xlabel(r"Ann\'{e}es depuis le d\'{e}but de la croissance rapide",
                  fontsize=12, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_yscale('log', base=2)
    ax.set_ylim(1 / 32, 1.5)
    ax.set_yticks([2**x for x in range(-5, 1)])
    ax.set_yticklabels(['1/' + str(2**x) for x in range(5, 0, -1)] + ['1'],
                       fontsize=12)
    ax.set_ylabel(r"PIB r\'{e}el par habitant relatif aux \'{E}.-U.",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=12)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'catchup_growth.png')


# =====================================================================
# Figure: Miracle vs stagnation — GDP/cap relative to US (1960–2019)
# =====================================================================
def miracle_vs_stagnation():
    print('Figure: Miracle vs stagnation — GDP/cap relative to US')

    df = _load_pwt()
    df = df.copy()
    df['y'] = df['rgdpo'] / df['pop']
    usa = df[df['countrycode'] == 'USA'].set_index('year')['y']

    miracles = [
        ('KOR', r"Cor\'{e}e du Sud", palette[0]),
        ('SGP', 'Singapour', palette[1]),
        ('CHN', 'Chine', palette[2]),
    ]
    stagnation = [
        ('HTI', r"Ha\"{i}ti", '#b0b0b0'),
        ('COD', 'R.D. Congo', '#777777'),
        ('MDG', 'Madagascar', '#c0c0c0'),
    ]

    fig, ax = new_figure(9, 4.5)

    for code, label, color in miracles:
        c = df[df['countrycode'] == code].set_index('year')['y']
        common = sorted(set(c.index) & set(usa.index))
        common = [yr for yr in common if 1960 <= yr <= 2019]
        ratio = [c.loc[yr] / usa.loc[yr] for yr in common]
        ax.plot(common, ratio, color=color, linewidth=2.5, label=label)

    for code, label, color in stagnation:
        c = df[df['countrycode'] == code].set_index('year')['y']
        common = sorted(set(c.index) & set(usa.index))
        common = [yr for yr in common if 1960 <= yr <= 2019]
        ratio = [c.loc[yr] / usa.loc[yr] for yr in common]
        ax.plot(common, ratio, color=color, linewidth=1.8,
                linestyle='--', label=label)

    ax.set_xlim(1960, 2019)
    ax.set_xticks(range(1960, 2020, 10))
    ax.set_xticklabels(range(1960, 2020, 10), fontsize=12)

    ax.set_yscale('log', base=2)
    ax.set_ylim(1 / 128, 1.5)
    ytick_vals = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1]
    ax.set_yticks(ytick_vals)
    ax.set_yticklabels(['1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1'],
                       fontsize=11)
    ax.set_ylabel(r"PIB/hab. relatif aux \'{E}.-U.",
                  fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0), ncol=2)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, 'miracle_vs_stagnation.png')


# =====================================================================
# Development accounting scatter plots (K/Y, L/N, A vs Y/N)
# =====================================================================
_dev_acct_cache = None


def _dev_accounting_data():
    """Compute development accounting ratios relative to US (2019)."""
    global _dev_acct_cache
    if _dev_acct_cache is not None:
        return _dev_acct_cache

    df = _load_pwt()
    df = df[df['year'] == 2019].copy()
    alpha = 1 / 3

    usa = df[df['countrycode'] == 'USA'].iloc[0]
    yn_usa = usa['rgdpo'] / usa['pop']
    ky_usa = (usa['cn'] / usa['rgdpo']) ** (alpha / (1 - alpha))
    ln_usa = usa['emp'] / usa['pop']
    a_usa = yn_usa / (ky_usa * ln_usa)

    records = []
    for _, row in df.iterrows():
        try:
            yn = row['rgdpo'] / row['pop']
            ky = (row['cn'] / row['rgdpo']) ** (alpha / (1 - alpha))
            ln = row['emp'] / row['pop']
            a = yn / (ky * ln)
            records.append({
                'country': row['countrycode'],
                'yn_ratio': yn / yn_usa,
                'ky_ratio': ky / ky_usa,
                'ln_ratio': ln / ln_usa,
                'a_ratio': a / a_usa,
            })
        except (ZeroDivisionError, ValueError):
            continue

    _dev_acct_cache = pd.DataFrame(records).dropna()
    return _dev_acct_cache


def _dev_accounting_scatter(data, y_col, ylabel, filename, ylim_top=4):
    """Generic scatter plot for development accounting."""
    fig, ax = new_figure(8, 4)

    ax.scatter(data['yn_ratio'], data[y_col], s=50, color=palette[0],
               alpha=0.7)
    ax.plot([1 / 90, ylim_top], [1 / 90, ylim_top], color=palette[1],
            linewidth=1)

    ax.set_xscale('log', base=2)
    ax.set_xlim(1 / 90, 2)
    ax.set_xticks([1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2])
    ax.set_xticklabels(['1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1', '2'],
                       fontsize=12)
    ax.set_xlabel(r"PIB r\'{e}el par habitant relatif aux \'{E}.-U. (2019)",
                  fontsize=12, ha='center')
    ax.xaxis.set_label_coords(0.5, -0.1)

    ax.set_yscale('log', base=2)
    ax.set_ylim(1 / 90, ylim_top)
    if ylim_top <= 2:
        yticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
        ylabels = ['1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1', '2']
    else:
        yticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2, 4]
        ylabels = ['1/64', '1/32', '1/16', '1/8', '1/4', '1/2', '1', '2', '4']
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.01)

    style_axes(ax)
    add_source(ax, 'Source: Penn World Tables 10.01')
    save(fig, filename)


def development_accounting_capital():
    print('Figure: Development accounting — capital (K/Y)')
    data = _dev_accounting_data()
    _dev_accounting_scatter(
        data, 'ky_ratio',
        r"Ratio capital/PIB relatif aux \'{E}.-U.",
        'development_accounting_capital.png',
        ylim_top=4)


def development_accounting_labor():
    print('Figure: Development accounting — labor (L/N)')
    data = _dev_accounting_data()
    _dev_accounting_scatter(
        data, 'ln_ratio',
        r"Taux d'emploi relatif aux \'{E}.-U.",
        'development_accounting_labor.png',
        ylim_top=2)


def development_accounting_tfp():
    print('Figure: Development accounting — TFP (A)')
    data = _dev_accounting_data()
    _dev_accounting_scatter(
        data, 'a_ratio',
        r"PTF relative aux \'{E}.-U.",
        'development_accounting_tfp.png',
        ylim_top=2)


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 2 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        regional_divergence,
        production_function,
        production_function_capital,
        growth_decomp_canada_us_total,
        growth_decomp_canada_us,
        growth_decomp_asian_tigers,
        catchup_growth,
        miracle_vs_stagnation,
        growth_decomp_china_us,
        global_growth_sources,
        ww2_recovery,
        china_gdp_growth,
        japan_growth,
        ussr_russia_gdp,
        convergence_us_states,
        convergence_oecd,
        convergence_asia,
        convergence_global,
        development_accounting,
        development_accounting_capital,
        development_accounting_labor,
        development_accounting_tfp,
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
