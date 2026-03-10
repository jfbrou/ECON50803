"""
ECON50803 — Shared Plot Utilities
==================================

Canonical definitions of colors, helpers, recession dates, and data loaders
used by all session figure scripts (figures_s1.py … figures_s6.py).

Import in each script as:
    from plot_utils import *
"""

__all__ = [
    # Core libraries (re-exported for convenience)
    'os', 'np', 'pd', 'plt', 'requests', 'json', 're', 'datetime',
    # Constants
    'fred_api_key', 'palette', 'FIGURES_DIR',
    'MONTH_FR', 'COUNTRY_FR',
    'recessions_ca', 'recessions_us',
    'THOUSANDS_RX',
    # Plot helpers
    'new_figure', 'style_axes', 'add_source', 'save', 'tick_ceil',
    'french_date_label', '_tr',
    # Data loaders
    'get_fred_data', 'get_valet_series',
    '_get_worldbank', '_get_owid_maddison',
]

import json
import os
import re
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
import requests
import dotenv

# ── Environment ──────────────────────────────────────────────────────────
dotenv.load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))
fred_api_key = os.getenv('fred_api_key')

# ── Font (Fira Sans via LaTeX, matching Beamer slides) ───────────────────
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Fira Sans']})
rc('text', usetex=True)
rc('text.latex', preamble=r'\usepackage[sfdefault,light]{FiraSans}'
                           r'\usepackage[T1]{fontenc}'
                           r'\usepackage[utf8]{inputenc}')

# ── Colour palette (HEC Montréal) ───────────────────────────────────────
palette = ['#002855',   # [0] HECnavy   — primary line/bar color, titles
           '#26d07c',   # [1] HECgreen  — secondary, regression lines, trend
           '#ff585d',   # [2] HECcoral  — alerts, peaks, annotations
           '#f3d03e',   # [3] yellow    — tertiary series
           '#0072ce',   # [4] blue      — additional series
           '#eb6fbd',   # [5] pink      — additional series
           '#00aec7',   # [6] teal      — additional series
           '#888b8d']   # [7] gray      — muted elements, secondary text

# ── Output path ─────────────────────────────────────────────────────────
FIGURES_DIR = os.path.join(Path(__file__).resolve().parent, 'Figures')
os.makedirs(FIGURES_DIR, exist_ok=True)


# ── French month abbreviations (for LaTeX/usetex date labels) ───────────
MONTH_FR = {1: 'janv.', 2: r'févr.', 3: 'mars', 4: 'avr.',
            5: 'mai', 6: 'juin', 7: 'juil.', 8: r'août',
            9: 'sept.', 10: 'oct.', 11: 'nov.', 12: r'déc.'}


def french_date_label(d):
    """Format a datetime as 'month_abbr\\nYYYY' in French."""
    return MONTH_FR[d.month] + '\n' + str(d.year)


# ── Country name translation mapping (English data → French labels) ─────
COUNTRY_FR = {
    'Argentina': 'Argentine',
    'Australia': 'Australie',
    'Austria': 'Autriche',
    'Bangladesh': 'Bangladesh',
    'Belgium': 'Belgique',
    'Botswana': 'Botswana',
    'Brazil': r"Brésil",
    'Cameroon': 'Cameroun',
    'Canada': 'Canada',
    'Chile': 'Chili',
    'China': 'Chine',
    'China, Hong Kong SAR': 'Hong Kong',
    'Colombia': 'Colombie',
    'D.R. of the Congo': r"R.D. du Congo",
    'Denmark': 'Danemark',
    'East Asia': r"Asie de l'Est",
    'Egypt': r"Égypte",
    'Ethiopia': r"Éthiopie",
    'Euro area': 'Zone euro',
    'Finland': 'Finlande',
    'France': 'France',
    'Germany': 'Allemagne',
    'Ghana': 'Ghana',
    'Greece': r"Grèce",
    'Haiti': 'Haïti',
    'Hong Kong': 'Hong Kong',
    'Iceland': 'Islande',
    'India': 'Inde',
    'Indonesia': r"Indonésie",
    'Ireland': 'Irlande',
    'Israel': 'Israël',
    'Italy': 'Italie',
    'Japan': 'Japon',
    'Kenya': 'Kenya',
    'Latin America': r"Amérique latine",
    'Luxembourg': 'Luxembourg',
    'Madagascar': 'Madagascar',
    'Malaysia': 'Malaisie',
    'Mexico': 'Mexique',
    'Mozambique': 'Mozambique',
    'Netherlands': 'Pays-Bas',
    'New Zealand': r"Nouvelle-Zélande",
    'Nigeria': r"Nigéria",
    'Norway': r"Norvège",
    'Philippines': 'Philippines',
    'Portugal': 'Portugal',
    'Republic of Korea': r"Corée du Sud",
    'Russia': 'Russie',
    'Senegal': r"Sénégal",
    'Singapore': 'Singapour',
    'South Africa': 'Afrique du Sud',
    'South Korea': r"Corée du Sud",
    'Spain': 'Espagne',
    'Sub-Saharan Africa': r"Afrique subsaharienne",
    'Sweden': r"Suède",
    'Switzerland': 'Suisse',
    'Taiwan': 'Taïwan',
    'Thailand': 'Thaïlande',
    'Turkey': 'Turquie',
    'United Kingdom': 'Royaume-Uni',
    'United States': r"États-Unis",
    'Venezuela (Bolivarian Republic of)': r"Vénézuela",
    'Vietnam': r"Viêt Nam",
    'Western Europe': r"Europe de l'Ouest",
    'Western Offshoots': r"Ouest (rejetons)",
}


def _tr(name):
    """Translate a country/region name to French, fallback to original."""
    return COUNTRY_FR.get(name, name)


# ── Recession dates ────────────────────────────────────────────────────
# Canadian recessions (C.D. Howe Business Cycle Council)
recessions_ca = [
    (datetime(1960, 4, 1), datetime(1961, 3, 1)),
    (datetime(1974, 1, 1), datetime(1975, 3, 1)),
    (datetime(1980, 2, 1), datetime(1980, 6, 1)),
    (datetime(1981, 7, 1), datetime(1982, 11, 1)),
    (datetime(1990, 4, 1), datetime(1992, 4, 1)),
    (datetime(2008, 10, 1), datetime(2009, 5, 1)),
    (datetime(2020, 2, 1), datetime(2020, 5, 1)),
]

# US recessions (NBER)
recessions_us = [
    (datetime(1948, 11, 1), datetime(1949, 10, 1)),
    (datetime(1953, 7, 1), datetime(1954, 5, 1)),
    (datetime(1957, 8, 1), datetime(1958, 4, 1)),
    (datetime(1960, 4, 1), datetime(1961, 2, 1)),
    (datetime(1969, 12, 1), datetime(1970, 11, 1)),
    (datetime(1973, 11, 1), datetime(1975, 3, 1)),
    (datetime(1980, 1, 1), datetime(1980, 7, 1)),
    (datetime(1981, 7, 1), datetime(1982, 11, 1)),
    (datetime(1990, 7, 1), datetime(1991, 3, 1)),
    (datetime(2001, 3, 1), datetime(2001, 11, 1)),
    (datetime(2007, 12, 1), datetime(2009, 6, 1)),
    (datetime(2020, 2, 1), datetime(2020, 4, 1)),
]


# ── Core plot helpers ──────────────────────────────────────────────────

def new_figure(w=8, h=4):
    """Create a new figure with transparent background."""
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    return fig, ax


def style_axes(ax, xgrid=False):
    """Apply standard axis styling: hide top/right spines, add gridlines.

    Args:
        xgrid: If True, also add vertical gridlines. Use for plots where
               the x-axis has specific units (not years/dates).
    """
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, which='major', axis='y', color='gray', linestyle=':', linewidth=0.5)
    if xgrid:
        ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)


def add_source(ax, text='Source: Federal Reserve Economic Data'):
    """Add source attribution text in the top-right corner."""
    ax.text(1, 1.01, text, fontsize=8, color='k',
            ha='right', va='bottom', transform=ax.transAxes)


def save(fig, name):
    """Save figure to Figures/ with tight layout, transparency, 300 dpi."""
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURES_DIR, name), transparent=True, dpi=300)
    plt.close(fig)
    print(f'  \u2713 {name}')


def tick_ceil(value, step):
    """Round up value to the next multiple of step."""
    return int(np.ceil(value / step)) * step


# ── Data source helpers ────────────────────────────────────────────────

def get_fred_data(series_id, frequency=None, aggregation_method=None,
                  observation_start=None, observation_end=None):
    """Retrieve a FRED series as a pandas Series indexed by date."""
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
    if observation_start is not None:
        params['observation_start'] = observation_start
    if observation_end is not None:
        params['observation_end'] = observation_end

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()['observations']

    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    return df.set_index('date')['value']


THOUSANDS_RX = re.compile(r"[,\u202f\u2009\s]")


def get_valet_series(series_id, start='2000-01-01'):
    """Download a Bank of Canada Valet time-series as a pandas Series."""
    url = (f"https://www.bankofcanada.ca/valet/observations/{series_id}/json"
           f"?start_date={start}")
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    obs = resp.json().get("observations", [])
    records = []
    for row in obs:
        raw = row.get(series_id, {})
        val = raw.get("v")
        if val is None:
            continue
        val = float(THOUSANDS_RX.sub("", str(val)))
        records.append((row["d"], val))
    df = (pd.DataFrame(records, columns=["date", "value"])
            .assign(date=lambda x: pd.to_datetime(x.date))
            .set_index("date").sort_index())
    return df["value"]


def _get_worldbank(indicator, country_iso, start=1960, end=2025):
    """Fetch annual data from the World Bank API as a pandas Series.

    Returns a Series indexed by integer year.
    """
    url = (f'https://api.worldbank.org/v2/country/{country_iso}/'
           f'indicator/{indicator}?format=json&per_page=500'
           f'&date={start}:{end}')
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    if len(payload) < 2 or payload[1] is None:
        return pd.Series(dtype=float)
    data = [(int(r['date']), r['value']) for r in payload[1]
            if r['value'] is not None]
    s = pd.Series(dict(data)).sort_index()
    s.index.name = 'year'
    return s


def _get_owid_maddison():
    """Fetch Maddison GDP per capita from the OWID API (2023 edition)."""
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
