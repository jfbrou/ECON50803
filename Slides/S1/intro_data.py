"""Refresh and archive the official inputs for Session 1 slides 7--13.

Run ``python intro_data.py`` to replace the snapshot with current source data,
then ``python figures_s1.py --intro-only`` to render the seven vector figures.
The manifest records retrieval dates, source URLs, units and transformations.
No live-download failure silently falls back to an older snapshot.
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin
import hashlib
import json
import sys

import pandas as pd
import requests
from stats_can import StatsCan
from stats_can.sc import vectors_to_df

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'plot-common'))
import teaching_plot_utils as plot

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / 'Slides/Data/s1_intro'
YALE_APP = 'https://interactives.budgetlab.yale.edu/tools/state-of-tariffs/'


def load_series(name):
    """Read a date-indexed, untransformed source series from the snapshot."""
    return pd.read_csv(DATA_DIR / f'{name}.csv', parse_dates=['date']).set_index('date')['value']


def load_frame(name, **kwargs):
    return pd.read_csv(DATA_DIR / f'{name}.csv', **kwargs)


def manifest():
    return json.loads((DATA_DIR / 'manifest.json').read_text())


def _statcan_vector(vector, cutoff):
    s = vectors_to_df(str(vector), periods=1500).iloc[:, 0].dropna().sort_index()
    return s.loc[:cutoff].rename('value')


def _unemployment(cutoff):
    # The current LFS starts in 1976; keep the older OECD history before it.
    current = _statcan_vector(2062815, cutoff)
    history = plot.get_fred_data('LRUNTTTTCAM156S', observation_end='1975-12-31').dropna()
    return pd.concat([history, current]).sort_index().rename('value')


def _fed_rate(cutoff):
    history = plot.get_fred_data('DFF', observation_start='2006-01-01',
                                 observation_end=str(cutoff.date())).dropna()
    # The New York Fed publishes the prior business day's EFFR at 9 a.m.;
    # this can be one observation ahead of the FRED mirror.
    url = 'https://markets.newyorkfed.org/api/rates/unsecured/effr/last/5.json'
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    records = r.json()['refRates']
    latest = pd.Series({pd.Timestamp(row['effectiveDate']): row['percentRate']
                        for row in records if row['type'] == 'EFFR'})
    combined = pd.concat([history, latest.loc[latest.index <= cutoff]])
    return combined[~combined.index.duplicated(keep='last')].sort_index().rename('value')


def _employment(cutoff):
    sc = StatsCan(data_folder=Path(__file__).resolve().parent)
    sc.update_tables(['14-10-0355-01'])
    d = sc.table_to_df('14-10-0355-01')
    d = d[(d['GEO'] == 'Canada') & (d['Statistics'] == 'Estimate') &
          (d['Data type'] == 'Seasonally adjusted') &
          (d['REF_DATE'] >= '2023-01-01') & (d['REF_DATE'] <= cutoff)]
    return d[['REF_DATE', 'North American Industry Classification System (NAICS)', 'VALUE']].copy()


def _maddison():
    d = plot._get_owid_maddison()
    return d[d['Entity'].isin(['United States', 'United Kingdom', 'Canada', 'France'])].copy()


def _tariffs(cutoff):
    r = requests.get(urljoin(YALE_APP, 'data/manifest.json'), timeout=60)
    r.raise_for_status()
    m = r.json()
    vintage_date = pd.to_datetime(m['release']['updated'])
    if vintage_date > cutoff:
        raise ValueError('The tariff release is later than the requested cutoff')
    tab = next(t for t in m['tabs'] if t['id'] == 'statutory-rates')
    series = []
    urls = []
    for figure_id, label in [('daily-rate-overall', 'total'), ('daily-rate-by-country', 'Canada')]:
        spec = next(f for f in tab['figures'] if f['id'] == figure_id)
        scenario = next(s for s in spec['selectors'] if s['id'] == 'scenario')['default']
        url = urljoin(urljoin(YALE_APP, m['data_base_url']), spec['data'])
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        from io import StringIO
        d = pd.read_csv(StringIO(r.text), parse_dates=['time'])
        # These are policy-based statutory estimates, not customs revenue rates.
        # Exclude all dates after the source vintage, even if already in the past
        # on retrieval: they remain projections from that older policy vintage.
        d = d[(d['scenario'] == scenario) & (d['series'] == label) & (d['time'] <= vintage_date)]
        if d.empty or d['time'].duplicated().any():
            raise ValueError(f'Invalid Yale tariff series: {label}')
        series.append(d.set_index('time')['value'].rename(label))
        urls.append(url)
    d = pd.concat(series, axis=1).rename_axis('date').reset_index()
    return d, {'source_urls': urls, 'source_release': m['release'],
               'units': 'Percent; statutory estimates with fixed 2024 import weights',
               'transformation': 'Current-law scenario; dates at or before the source vintage only. Not collected duties or annual averages.'}


def refresh():
    plot.init(figures_dir=str(ROOT / 'Slides/Figures'), env_file=str(ROOT / '.env'))
    cutoff = pd.Timestamp.today().normalize()
    jobs = {
        'unemployment': lambda: _unemployment(cutoff),
        'cpi': lambda: _statcan_vector(41690973, cutoff),
        'fed_rate': lambda: _fed_rate(cutoff),
        'boc_rate': lambda: plot.get_valet_series('V39079', start='2006-01-01').loc[:cutoff],
        'inflation_expectations': lambda: plot.get_valet_series('CES_C1_SHORT_TERM', start='2014-01-01').loc[:cutoff],
        'employment': lambda: _employment(cutoff),
        'maddison': _maddison,
        'tariffs': lambda: _tariffs(cutoff),
    }
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {name: pool.submit(fn) for name, fn in jobs.items()}
        results = {name: future.result() for name, future in futures.items()}
    tariff_frame, tariff_meta = results['tariffs']
    results['tariffs'] = tariff_frame
    # Historical all-import revenue rates retained from the original Yale workbook.
    history = pd.read_excel(ROOT / 'Slides/Data/tariff_data.xlsx', sheet_name='F1', header=None,
                            skiprows=5, names=['year', 'value', 'proj_post', 'cur_post', 'proj_pre', 'cur_pre'])
    history = history[history['year'].notna() & history['value'].notna()][['year', 'value']]
    history['year'] = history['year'].astype(int)
    results['tariffs_history'] = history
    metadata = {
        'unemployment': {'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410028701', 'https://fred.stlouisfed.org/series/LRUNTTTTCAM156S'], 'vector': 'v2062815', 'units': 'Percent, seasonally adjusted; Canada, total gender, age 15+', 'transformation': 'Statistics Canada from 1976; OECD/FRED history through 1975.'},
        'cpi': {'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401'], 'vector': 'v41690973', 'units': 'CPI index, 2002=100, all-items Canada, not seasonally adjusted', 'transformation': 'Plot inflation as index / index lagged 12 months - 1; do not fill missing months.'},
        'fed_rate': {'source_urls': ['https://fred.stlouisfed.org/series/DFF', 'https://markets.newyorkfed.org/api/rates/unsecured/effr/last/5.json'], 'units': 'Percent, daily effective federal funds rate', 'transformation': 'FRED history supplemented by the latest official New York Fed observations; prefer the latter on overlapping dates.'},
        'boc_rate': {'source_urls': ['https://www.bankofcanada.ca/valet/observations/V39079/json'], 'units': 'Percent, daily target overnight rate'},
        'inflation_expectations': {'source_urls': ['https://www.bankofcanada.ca/valet/observations/CES_C1_SHORT_TERM/json'], 'units': 'Percent, consumer expectations over next 12 months', 'transformation': 'Quarter-start reference dates shifted forward one year to display expectation horizon; divide by 100.'},
        'employment': {'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410035501'], 'units': 'Thousands of persons, seasonally adjusted estimates, Canada only', 'transformation': 'Disjoint selected industries; sum employment levels within each group, then index to January 2023=100. Groups are exposure proxies, not a causal estimate of tariff effects.'},
        'maddison': {'source_urls': ['https://api.ourworldindata.org/v1/indicators/900793.data.json', 'https://ourworldindata.org/grapher/gdp-per-capita-maddison-project-database'], 'units': 'GDP per capita in constant 2011 international dollars', 'source_release': 'Maddison Project Database 2023; latest available edition verified 2026-10-15'},
        'tariffs': tariff_meta,
        'tariffs_history': {'source_urls': ['https://budgetlab.yale.edu/research/state-us-tariffs-january-19-2026'], 'units': 'Percent; annual collected duties divided by total import value, through 2024', 'local_source': 'Slides/Data/tariff_data.xlsx, F1'},
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.now(tz='UTC').isoformat()
    for name, value in results.items():
        if isinstance(value, pd.Series):
            d = value.rename('value').rename_axis('date').reset_index()
        else:
            d = value
        path = DATA_DIR / f'{name}.csv'
        d.to_csv(path, index=False)
        metadata[name]['retrieved_at_utc'] = stamp
        metadata[name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        date_column = next((c for c in ['date', 'REF_DATE', 'Year', 'year'] if c in d.columns), None)
        if date_column:
            metadata[name]['last_observation'] = str(d[date_column].max())
        print(f'{name}: {metadata[name].get("last_observation", "saved")}', flush=True)
    (DATA_DIR / 'manifest.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    refresh()
