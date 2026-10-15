"""Refresh and archive the inputs for Session 1's remaining data figures.

Run this script to refresh sources, then figures_s1.py --remaining-only to
regenerate offline. Source dates, hashes, definitions and transformations are
recorded beside the CSV snapshots. No forecasts or population extrapolations.
"""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO, StringIO
from pathlib import Path
import hashlib
import json
import sys

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from stats_can import StatsCan
from stats_can.sc import vectors_to_df

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'plot-common'))
import teaching_plot_utils as plot

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / 'Slides/Data/s1_remaining'
INDICATORS = ['NE.CON.PRVT.ZS', 'NE.GDI.TOTL.ZS', 'NE.CON.GOVT.ZS',
              'NE.RSB.GNFS.ZS', 'NY.GDP.MKTP.PP.KD', 'NY.GDP.PCAP.PP.KD',
              'SP.POP.TOTL', 'PA.NUS.PPP', 'PA.NUS.FCRF',
              'NY.GDP.MKTP.CD', 'NY.GNP.MKTP.CD']


# Table 36-10-0123-01: Canada, seasonally adjusted at annual rates,
# millions of CAD at fixed 2017 prices. Match responses by vector ID, not order.
CONSTANT_ACCOUNT_VECTORS = {
    62306859: 'Household final consumption expenditure',
    62306867: "Non-profit institutions serving households' final consumption expenditure",
    62306868: 'General governments final consumption expenditure',
    62306870: 'Gross fixed capital formation',
    62306882: 'Investment in inventories',
    62306896: 'Gross domestic product at market prices',
}


def constant_accounts_from_response(payload, cutoff):
    records = []
    for entry in payload:
        if entry['status'] != 'SUCCESS':
            raise ValueError('StatCan constant-price series request failed.')
        obj = entry['object']
        vector = obj['vectorId']
        if vector not in CONSTANT_ACCOUNT_VECTORS:
            continue
        for point in obj['vectorDataPoint']:
            records.append({'REF_DATE': point['refPer'],
                            'Estimates': CONSTANT_ACCOUNT_VECTORS[vector],
                            'VALUE': point['value']})
    df = pd.DataFrame(records)
    df['REF_DATE'] = pd.to_datetime(df['REF_DATE'])
    df = df.loc[df['REF_DATE'] <= cutoff].sort_values(['REF_DATE', 'Estimates'])
    if df['Estimates'].nunique() != len(CONSTANT_ACCOUNT_VECTORS):
        raise ValueError('Incomplete constant-price accounts.')
    return df


def fetch_constant_accounts(cutoff):
    response = requests.post(
        'https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods',
        json=[{'vectorId': vector, 'latestN': 400} for vector in CONSTANT_ACCOUNT_VECTORS],
        timeout=60)
    response.raise_for_status()
    return constant_accounts_from_response(response.json(), cutoff)


def load_frame(name, **kwargs):
    return pd.read_csv(DATA_DIR / f'{name}.csv', **kwargs)


def load_series(name):
    return load_frame(name, parse_dates=['date']).set_index('date')['value']


def worldbank_series(indicator, country_iso, start=1960, end=None):
    d = load_frame('worldbank')
    d = d[(d.iso == country_iso) & (d.year >= start)]
    if end is not None:
        d = d[d.year <= end]
    return d.set_index('year')[indicator].dropna().sort_index()


def worldbank_panel(indicators, countries=None, min_countries=150):
    """Latest complete common year, excluding World Bank aggregates."""
    d = load_frame('worldbank').dropna(subset=indicators)
    if countries is not None:
        d = d[d.iso.isin(countries)]
        min_countries = len(countries)
    counts = d.groupby('year').iso.nunique()
    years = counts[counts >= min_countries].index
    if not len(years):
        raise ValueError(f'No complete World Bank comparison for {indicators}')
    year = int(years.max())
    return d[d.year == year].copy(), year


def get(url):
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    r = session.get(url, timeout=90, headers={'User-Agent': 'Mozilla/5.0',
                    'Referer': 'https://www.pricinglab.org/tariff-tracker/'})
    r.raise_for_status()
    return r


def refresh():
    plot.init(str(ROOT / 'Slides/Figures'), str(ROOT / '.env'))
    cutoff = pd.Timestamp.today().normalize()
    metadata = {}
    results = {}
    sc = StatsCan(data_folder=Path(__file__).resolve().parent)
    sc.update_tables(['36-10-0104-01', '36-10-0706-01'])
    accounts = sc.table_to_df('36-10-0104-01')
    accounts = accounts[(accounts.GEO == 'Canada') &
                        (accounts['Seasonal adjustment'] == 'Seasonally adjusted at annual rates') &
                        accounts.Prices.isin(['Current prices', 'Chained (2017) dollars']) &
                        (accounts.REF_DATE <= cutoff)]
    results['gdp_accounts'] = accounts[['REF_DATE', 'Prices', 'Estimates', 'VALUE']]
    metadata['gdp_accounts'] = {
        'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610010401'],
        'units': 'Millions of Canadian dollars; seasonally adjusted at annual rates',
        'transformation': 'Current prices for expenditure shares and annual decomposition; chained 2017 dollars for real GDP and the implicit deflator. Annual pie uses only years with all four quarters. C includes households and NPISH; I includes all fixed capital formation and inventories; G is government consumption; NX = exports minus imports. Statistical discrepancy is reported separately.'}
    pc = sc.table_to_df('36-10-0706-01')
    pc = pc[(pc.Prices == 'Chained (2017) dollars') &
            (pc.Estimates == 'Gross domestic product per capita') & (pc.REF_DATE <= cutoff)]
    results['can_gdp_per_capita'] = pc.set_index('REF_DATE').VALUE.rename('value')
    metadata['can_gdp_per_capita'] = {
        'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610070601'],
        'units': 'Chained 2017 CAD per person; quarterly, seasonally adjusted at annual rates',
        'transformation': 'Official per-capita GDP, indexed to 2000Q1 = 100; no interpolation or extrapolation of annual population.'}

    def wb(ind):
        url = (f'https://api.worldbank.org/v2/country/all/indicator/{ind}'
               f'?format=json&per_page=20000&date=2007:{cutoff.year}')
        p = get(url).json()
        if len(p) < 2 or p[1] is None or p[0]['pages'] != 1:
            raise ValueError(f'Incomplete World Bank response for {ind}')
        d = pd.DataFrame([{'iso': x['countryiso3code'], 'year': int(x['date']),
                           ind: x['value']} for x in p[1]
                          if x['value'] is not None and x['countryiso3code']])
        return d, url, p[0]['lastupdated']

    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {ind: pool.submit(wb, ind) for ind in INDICATORS}
        fetched = {ind: future.result() for ind, future in jobs.items()}
    country_url = 'https://api.worldbank.org/v2/country?format=json&per_page=500'
    countries = get(country_url).json()[1]
    valid = {r['id']: r['name'] for r in countries if r['region']['id'] != 'NA'}
    wb_data = None
    for d, _, _ in fetched.values():
        wb_data = d if wb_data is None else wb_data.merge(d, on=['iso', 'year'], how='outer', validate='one_to_one')
    wb_data = wb_data[wb_data.iso.isin(valid)].sort_values(['iso', 'year'])
    wb_data['name'] = wb_data.iso.map(valid)
    results['worldbank'] = wb_data
    metadata['worldbank'] = {
        'source_urls': [country_url] + [x[1] for x in fetched.values()],
        'source_last_updated': {ind: x[2] for ind, x in fetched.items()},
        'units': 'As defined by the WDI indicator codes in the CSV header; PPP amounts at constant 2021 international dollars',
        'transformation': 'Exclude region/income aggregates using country metadata. Cross-sections use the latest common year with complete variables and at least 150 countries, or every selected country for small comparisons. No mixing indicator years. Price level = PPP conversion factor / exchange rate, normalized to the US value in the same year.'}

    urls = {
        'big_mac': 'https://raw.githubusercontent.com/TheEconomist/big-mac-data/master/output-data/big-mac-full-index.csv',
        'pricinglab': 'https://www.pricinglab.org/files/Cavallo_Llamas_Vazquez_domestic_imported_trend_line.csv',
        'hdi': 'https://ourworldindata.org/grapher/human-development-index.csv?tab=table',
        'jones_klenow': 'https://web.stanford.edu/~chadj/BeyondGDP500.xls',
    }
    def download(name, url):
        r = get(url)
        if name == 'jones_klenow':
            d = pd.read_excel(BytesIO(r.content), sheet_name='Levels in 2007',
                              skiprows=8, usecols=[0, 1, 2])
            d.columns = ['country', 'welfare', 'y']
            return d.dropna(subset=['welfare', 'y'])
        return pd.read_csv(StringIO(r.text))
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {name: pool.submit(download, name, url) for name, url in urls.items()}
        for name, future in jobs.items():
            results[name] = future.result()
            metadata[name] = {'source_urls': [urls[name]]}
    results['pricinglab']['date'] = pd.to_datetime(results['pricinglab']['date'], format='%d%b%Y')
    results['pricinglab'] = results['pricinglab'].loc[results['pricinglab']['date'] <= cutoff].sort_values('date')
    # New official CPI inputs replace retired OECD/FRED monthly series.
    core = vectors_to_df('41691233', periods=1500).iloc[:, 0].dropna().sort_index().loc[:cutoff]
    results['core_cpi'] = core.rename('value')
    metadata['core_cpi'] = {
        'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401'],
        'vector': 'v41691233', 'units': 'CPI excluding food and energy, index 2002=100, Canada, NSA',
        'transformation': '12-month percent change; no filling missing observations.'}
    for name, code in [('us_gdp', 'GDPC1'), ('us_gdp_per_capita', 'A939RX0Q048SBEA')]:
        results[name] = plot.get_fred_data(code, observation_end=str(cutoff.date())).dropna().rename('value')
        metadata[name] = {'source_urls': [f'https://fred.stlouisfed.org/series/{code}'],
                          'units': 'BEA real GDP (chained 2017 USD), quarterly, seasonally adjusted at annual rates; per person for A939RX0Q048SBEA',
                          'transformation': 'Indexed to 2000Q1 = 100 for the comparison plot.'}
    results['gdp_constant_prices'] = fetch_constant_accounts(cutoff)
    metadata['gdp_constant_prices'] = {
        'source_urls': ['https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610012301'],
        'vectors': CONSTANT_ACCOUNT_VECTORS,
        'units': 'Millions of CAD at fixed 2017 prices, quarterly, seasonally adjusted at annual rates',
        'transformation': 'C = households + NPISH; I = fixed capital formation + investment in inventories; G = government consumption. HP filter of levels (lambda=1600) on full sample; display 1981 onward. C/I/G deviations divided by own trend. Fixed/inventory cycle contributions divided by total investment trend, so they sum exactly to the total cycle.'}
    metadata['big_mac']['transformation'] = 'Use the two latest published dates from the official file; USD_raw times 100, dollar_price in current USD. Dates and axis range derived from the file.'
    metadata['pricinglab']['transformation'] = 'Raw daily domestic and imported indices, cumulative price change = (index - 1) * 100. Preserve the source baseline. The public file may lag the retrieval date.'
    metadata['hdi']['transformation'] = 'UNDP HDI merged by country code and year with WDI real GDP per capita and population. Latest complete year with at least 150 countries; exclude aggregates.'
    metadata['jones_klenow']['transformation'] = 'Historical replication result: Levels in 2007, welfare and GDP per capita relative to US, divided by 100. This paper does not supply a current-year cross-section. Bubble populations are WDI 2007.'
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp.now(tz='UTC').isoformat()
    for name, value in results.items():
        d = value.rename_axis('date').reset_index() if isinstance(value, pd.Series) else value
        path = DATA_DIR / f'{name}.csv'
        d.to_csv(path, index=False)
        metadata[name]['retrieved_at_utc'] = stamp
        metadata[name]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        date_col = next((c for c in ['date', 'REF_DATE', 'Year', 'year'] if c in d), None)
        if date_col:
            metadata[name]['last_observation'] = str(d[date_col].max())
        print(name, metadata[name].get('last_observation', f'{len(d)} rows'), flush=True)
    (DATA_DIR / 'manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    refresh()
