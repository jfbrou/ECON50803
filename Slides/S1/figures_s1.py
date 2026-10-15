"""
ECON50803 — Session 1 : Figure Generation
============================================

Generates all matplotlib figures for Session 1 slides as vector PDFs.
PDF export preserves fonts, paths, and transparency without rasterizing plots.
All figure labels, axis titles, legends, and annotations are in French.

Run from Slides/S1/:
    python3 figures_s1.py
    python3 intro_data.py                  # refresh official inputs for slides 7--13
    python3 figures_s1.py --intro-only     # regenerate only those seven figures
    python3 remaining_data.py             # refresh the remaining source snapshots
    python3 figures_s1.py --remaining-only # regenerate the remaining figures offline
"""

from pathlib import Path
from statsmodels.tsa.filters.hp_filter import hpfilter
from stats_can import StatsCan

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "plot-common"))
import teaching_plot_utils
teaching_plot_utils.init(
    figures_dir=str(Path(__file__).resolve().parents[1] / 'Figures'),
    env_file=str(Path(__file__).resolve().parents[2] / '.env'))
from teaching_plot_utils import *
from intro_data import load_series as intro_series, load_frame as intro_frame
from remaining_data import (load_series as remaining_series,
                            load_frame as remaining_frame,
                            worldbank_panel)


def _source_month(date):
    """Use a single line in source notes; axis date labels use two lines."""
    return french_date_label(date).replace('\n', ' ')


# =====================================================================
# Figure 1: Canadian unemployment rate
# =====================================================================
def can_unemployment():
    print('Figure 1: Canadian unemployment rate')
    u = intro_series('unemployment')

    u_clean = u.dropna()

    fig, ax = new_figure()

    ax.plot(u, color=palette[0], linewidth=2)

    # Annotation for COVID spike
    covid_peak_date = u.loc['2020-01-01':'2020-12-31'].idxmax()
    covid_peak_val = u.loc[covid_peak_date]
    ax.annotate(f'{covid_peak_val:.1f}\\%',
                xy=(covid_peak_date, covid_peak_val),
                xytext=(covid_peak_date + pd.DateOffset(years=3), covid_peak_val - 0.5),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    last_date = u_clean.index[-1]
    first_year = u_clean.index[0].year
    ax.set_xlim(pd.to_datetime(str(first_year)), last_date)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(first_year, last_date.year + 1, 10)])
    ax.set_xticklabels(range(first_year, last_date.year + 1, 10), fontsize=11)
    ax.set_ylim(2, 16)
    ax.set_yticks(range(2, 16 + 1, 2))
    ax.set_yticklabels([str(x) + r'\%' for x in range(2, 16 + 1, 2)], fontsize=11)
    ax.set_ylabel(r"Taux de chômage", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime(str(first_year)):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    add_source(ax, f'Source: StatCan; OECD ({_source_month(last_date)})')
    save(fig, 'can_unemployment.pdf')


# =====================================================================
# Figure 2: Canadian inflation (long-run)
# =====================================================================
def can_inflation_longrun():
    print('Figure 2: Canadian inflation (long-run)')
    cpi = intro_series('cpi')                    # StatCan all-items CPI, 2002=100, NSA
    infl = cpi.pct_change(12, fill_method=None).dropna()

    fig, ax = new_figure()

    ax.plot(infl, color=palette[0], linewidth=2)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC (depuis 1991)")

    # Annotation for 2022 peak
    peak_date = infl.loc['2021-01-01':'2023-12-31'].idxmax()
    peak_val = infl.loc[peak_date]
    ax.annotate(f'{100*peak_val:.1f}\\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date - pd.DateOffset(years=5), peak_val + 0.005),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    last_date = infl.dropna().index[-1]
    ax.set_xlim(pd.to_datetime('1965'), last_date)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(1965, last_date.year + 1, 5)])
    ax.set_xticklabels(range(1965, last_date.year + 1, 5), fontsize=11,
                       rotation=45, ha='right')
    ax.set_ylim(-0.02, 0.14)
    ax.set_yticks(np.arange(-0.02, 0.14 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 14 + 0.1, 2)],
                       fontsize=11)
    ax.set_ylabel(r"Inflation IPC (12 mois)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('1965'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.55, 1.0))
    add_source(ax, f'Source: StatCan ({_source_month(last_date)})')
    save(fig, 'can_inflation_longrun.pdf')


# =====================================================================
# Figure 3: Policy rates (Fed + BoC)
# =====================================================================
def policy_rates():
    print('Figure 3: Policy rates (Fed + BoC)')
    fed = intro_series('fed_rate')
    boc = intro_series('boc_rate')

    fig, ax = new_figure()

    ax.plot(fed, color=palette[0], linewidth=2,
            label=r"Taux effectif des fonds fédéraux (É.-U.)")
    ax.plot(boc, color=palette[1], linewidth=2,
            label=r"Taux cible à un jour (Canada)")

    last_date = max(fed.dropna().index[-1], boc.dropna().index[-1])
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2006, last_date.year + 1, 2)])
    ax.set_xticklabels(range(2006, last_date.year + 1, 2), fontsize=11)
    ax.set_xlim(pd.to_datetime('2006'), last_date)
    ax.set_ylim(0, 6)
    ax.set_yticks(range(0, 6 + 1, 1))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 6 + 1, 1)], fontsize=11)
    ax.set_ylabel('Taux directeur', fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.18, 1.0))
    add_source(ax, f'Source: Fed de New York; FRED; BdC ({_source_month(last_date)})')
    save(fig, 'policy_rates.pdf')


# =====================================================================
# Figure 4: Canadian inflation (recent)
# =====================================================================
def canada_inflation_recent():
    print('Figure 4: Canadian inflation (recent)')
    cpi = intro_series('cpi')
    infl = cpi.pct_change(12, fill_method=None).dropna()

    # Fetch BoC consumer inflation expectations (1-year ahead)
    # Survey date maps to expected inflation 1 year forward
    exp_1yr = intro_series('inflation_expectations')
    # Shift dates forward by 1 year (expectation horizon)
    exp_dates = exp_1yr.index + pd.DateOffset(years=1)
    exp_vals = exp_1yr.values / 100  # convert from % to fraction

    fig, ax = new_figure()

    # BoC target band (1-3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC")

    ax.plot(infl, color=palette[0], linewidth=2, label='Inflation IPC')

    # Plot expectations (only future portion, from last actual data onward)
    last_actual = infl.dropna().index[-1]
    future_mask = exp_dates > last_actual
    if future_mask.any():
        # Connect from last actual point to first expectation point
        bridge_dates = pd.Index([last_actual]).append(exp_dates[future_mask])
        bridge_vals = np.concatenate([[infl.loc[last_actual]],
                                      exp_vals[future_mask]])
        ax.plot(bridge_dates, bridge_vals, color=palette[7], linewidth=2,
                linestyle=':', label='Anticipations des consommateurs (1 an)')

    # Annotation for 2022 peak
    peak_date = infl.loc['2021-01-01':'2023-12-31'].idxmax()
    peak_val = infl.loc[peak_date]
    ax.annotate(f'{100*peak_val:.1f}\\%',
                xy=(peak_date, peak_val),
                xytext=(peak_date + pd.DateOffset(months=8), peak_val + 0.008),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))

    # x-axis: end at the last plotted point
    last_plot = last_actual
    if future_mask.any():
        last_plot = max(last_plot, exp_dates[future_mask][-1])
    ax.set_xlim(pd.to_datetime('2016'), last_plot)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2016, last_plot.year + 1, 1)])
    ax.set_xticklabels(range(2016, last_plot.year + 1, 1), fontsize=11,
                       rotation=45, ha='right')
    ax.set_ylim(-0.02, 0.10)
    ax.set_yticks(np.arange(-0.02, 0.10 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 10 + 0.1, 2)],
                       fontsize=11)
    ax.set_ylabel(r"Inflation IPC (12 mois)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=10, loc='upper left',
              bbox_to_anchor=(0.0, 1.0))
    quarter = (exp_1yr.index[-1].month - 1) // 3 + 1
    add_source(ax, f'Source: StatCan; BdC (enquête T{quarter} {exp_1yr.index[-1].year})')
    save(fig, 'canada_inflation_recent.pdf')


# =====================================================================
# Figure 5: Canadian employment by US-export dependence
# =====================================================================
def canada_employment_exports():
    print('Figure 5: Canadian employment by export dependence')
    # Snapshot contains Canada-only, seasonally adjusted employment estimates.
    # Never add provincial rows or standard errors to employment levels.
    df = intro_frame('employment', parse_dates=['REF_DATE'])

    # Industries with high US-export dependence
    high_export = [
        'Manufacturing [31-33]',
        'Agriculture [111-112, 1100, 1151-1152]',
        'Forestry, fishing, mining, quarrying, oil and gas [21, 113-114, 1153, 2100]',
    ]

    # Industries with limited US-export dependence
    low_export = [
        'Health care and social assistance [62]',
        'Educational services [61]',
        'Public administration [91]',
        'Construction [23]',
        'Accommodation and food services [72]',
        'Retail trade [44-45]',
    ]

    industry_col = 'North American Industry Classification System (NAICS)'
    levels = df.pivot(index='REF_DATE', columns=industry_col, values='VALUE')
    # Exact, disjoint industry names avoid including both aggregates and their
    # components, or accidentally matching wholesale-and-retail to retail alone.
    high_matched, low_matched = high_export, low_export

    # Filter and aggregate, indexed to Jan 2023 = 100
    def get_index(industry_list):
        sub = levels[industry_list].sum(axis=1, min_count=len(industry_list))
        return sub / sub.loc['2023-01-01'] * 100

    # Total employment
    total = get_index(['Total employed, all industries'])

    fig, ax = new_figure()

    # Use HEC colours: coral for high-export, navy for low-export, green for all
    if len(high_matched) > 0:
        high_idx = get_index(high_matched)
        ax.plot(high_idx, color=palette[2], linewidth=2,
                label=r"Forte dépendance aux export. américaines")
    if len(low_matched) > 0:
        low_idx = get_index(low_matched)
        ax.plot(low_idx, color=palette[0], linewidth=2,
                label=r"Faible dépendance aux export. américaines")
    if len(total) > 0:
        ax.plot(total, color=palette[1], linewidth=2,
                label='Tous les secteurs')

    # Determine y-axis range: round to nice ticks
    all_series = []
    if len(high_matched) > 0:
        all_series.append(high_idx)
    if len(low_matched) > 0:
        all_series.append(low_idx)
    if len(total) > 0:
        all_series.append(total)
    if all_series:
        ymin_data = min(s.min() for s in all_series)
        ymax_data = max(s.max() for s in all_series)
        ymin = int(np.floor(ymin_data / 2) * 2)
        ymax = int(np.ceil(ymax_data / 2) * 2)
        ax.set_ylim(ymin, ymax)
        ax.set_yticks(range(ymin, ymax + 1, 2))
        ax.set_yticklabels([str(x) for x in range(ymin, ymax + 1, 2)],
                           fontsize=11)

    # Keep regular six-month ticks without extending beyond the observations.
    all_dates = pd.concat(all_series).index if all_series else pd.DatetimeIndex([])
    last_data = all_dates.max() if len(all_dates) > 0 else pd.to_datetime('2026-01-01')
    xtick_dates = pd.date_range('2023-01-01', end=last_data, freq='6MS')
    ax.set_xticks(xtick_dates)
    ax.set_xticklabels([french_date_label(d) for d in xtick_dates], fontsize=11)
    ax.set_xlim(pd.to_datetime('2023-01-01'), last_data)
    ax.set_ylabel(r"Indice d'emploi (janv. 2023 = 100)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, f'Source: StatCan, 14-10-0355-01 ({_source_month(last_data)})')
    save(fig, 'canada_employment_exports.pdf')


# =====================================================================
# Figure 6: Hockey stick — world GDP per capita
# =====================================================================
def hockey_stick_world():
    print('Figure 6: Hockey stick (GDP per capita, long-run)')
    # Download Maddison GDP per capita from OWID API (Maddison 2023 edition, data to 2022)
    df = intro_frame('maddison')

    fig, ax = new_figure()

    # Data uses English entity names; display labels are French
    countries = {
        'United States': (r"États-Unis", palette[0]),
        'United Kingdom': ('Royaume-Uni', palette[1]),
        'Canada': ('Canada', palette[2]),
        'France': ('France', palette[3]),
    }

    max_year = 0
    for entity_en, (label_fr, color) in countries.items():
        sub = df.loc[(df['Entity'] == entity_en) & df['GDP per capita'].notna()]
        ax.plot(sub['Year'], sub['GDP per capita'], color=color,
                label=label_fr, linewidth=2)
        max_year = max(max_year, sub['Year'].max())

    ax.set_xlim(0, max_year)
    ax.set_xticks(range(0, max_year + 1, 250))
    ax.set_xticklabels(range(0, max_year + 1, 250), fontsize=11)
    ax.set_ylim(0, 60000)
    ax.set_yticks(range(0, 60000 + 1, 10000))
    ax.set_yticklabels([r'\$' + str(x) + 'K' for x in range(0, 60 + 1, 10)],
                       fontsize=11)
    ax.set_ylabel("PIB réel par habitant\n(dollars internationaux de 2011)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left',
              bbox_to_anchor=(0.02, 1.0))
    add_source(ax, 'Source: Maddison Project Database 2023 (via Our World in Data)')
    save(fig, 'hockey_stick_world.pdf')


# =====================================================================
# Figure 7: US effective tariff rate since 1790
# =====================================================================
def us_tariff_rate():
    print('Figure 7: US effective tariff rate since 1790')
    hist = intro_frame('tariffs_history').rename(columns={'year': 'Year', 'value': 'ETR'})
    recent = intro_frame('tariffs', parse_dates=['date']).sort_values('date')
    last = recent.iloc[-1]
    vintage_date = last['date']
    # Point-in-time statutory estimates from the latest published policy vintage;
    # do not substitute its scheduled future rates or call it a 2025 annual rate.
    etr_overall = last['total']
    etr_canada = last['Canada']
    vintage_x = vintage_date.year + (vintage_date.dayofyear - 1) / (366 if vintage_date.is_leap_year else 365)

    fig, ax = new_figure()

    # Historical line
    ax.plot(hist['Year'], hist['ETR'], color=palette[0], linewidth=2)

    # Dotted connectors distinguish current statutory estimates from history.
    last_hist_year = hist['Year'].iloc[-1]
    last_hist_etr = hist['ETR'].iloc[-1]

    # Overall US rate (coral)
    ax.plot([last_hist_year, vintage_x], [last_hist_etr, etr_overall],
            color=palette[2], linewidth=2, linestyle=':')
    ax.plot(vintage_x, etr_overall, 'o', color=palette[2], markersize=8,
            zorder=5, clip_on=False)

    # Canada-specific rate (green)
    ax.plot([last_hist_year, vintage_x], [last_hist_etr, etr_canada],
            color=palette[1], linewidth=2, linestyle=':')
    ax.plot(vintage_x, etr_canada, 'o', color=palette[1], markersize=8,
            zorder=5, clip_on=False)

    # Annotations — equal-length arrows
    # Figure is 8×4 in, axes span 97 yr × 20 pp → x_scale=0.0825 in/yr, y_scale=0.2 in/pp
    # Target visual arrow length ≈ 1.5 in for all three
    ax.annotate(f'{etr_overall:.1f}\\%  global',
                xy=(vintage_x, etr_overall),
                xytext=(2007, 19),
                fontsize=11, color=palette[2], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[2], lw=1.5))
    ax.annotate(f'{etr_canada:.1f}\\%  Canada',
                xy=(vintage_x, etr_canada),
                xytext=(2008, 11),
                fontsize=11, color=palette[1], fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=palette[1], lw=1.5))

    # Smoot-Hawley (shrinkB=12pt ≈ 0.17 in gap before data line)
    etr_1932 = hist.loc[hist['Year'] == 1932, 'ETR'].iloc[0]
    ax.annotate('Smoot-Hawley' + '\n' + f'({etr_1932:.0f}\\%)',
                xy=(1932, etr_1932),
                xytext=(1949, 15.5),
                fontsize=9, color=palette[7], ha='center',
                arrowprops=dict(arrowstyle='->', color=palette[7],
                                lw=1, alpha=0.6, shrinkB=12))

    ax.set_xticks(range(1930, vintage_date.year + 1, 10))
    ax.set_xticklabels(range(1930, vintage_date.year + 1, 10), fontsize=11)
    ax.set_xlim(1930, vintage_x)
    ax.set_ylim(0, 20)
    ax.set_yticks(range(0, 20 + 1, 5))
    ax.set_yticklabels([str(x) + r'\%' for x in range(0, 20 + 1, 5)],
                       fontsize=11)
    ax.set_ylabel(r"Taux tarifaire effectif américain", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, f'Source: Yale Budget Lab ({vintage_date.day} {_source_month(vintage_date)})')
    ax.text(0, -0.18,
            f'Historique : droits perçus / importations; point {vintage_date.year} : estimation statutaire (pondérations 2024).',
            transform=ax.transAxes, fontsize=8, color=palette[7], ha='left')
    save(fig, 'us_tariff_rate.pdf')


# ── StatsCan GDP accounts helper ──────────────────────────────────────
def _load_gdp_accounts(prices='Current prices'):
    """Pivot archived, seasonally adjusted StatCan expenditure accounts."""
    df = remaining_frame('gdp_accounts', parse_dates=['REF_DATE'])
    df = df[df['Prices'] == prices]
    df = df.pivot(index='REF_DATE', columns='Estimates',
                  values='VALUE').reset_index()
    return df


def _can_gdp(real=True):
    prices = 'Chained (2017) dollars' if real else 'Current prices'
    return _load_gdp_accounts(prices).set_index('REF_DATE')['Gross domestic product at market prices'].dropna()


def _quarter_label(date):
    return f'T{(date.month - 1) // 3 + 1} {date.year}'


def _gdp_share_plot(dates, ratio, ylabel, ylim, ytick_step, fname):
    """Generic GDP-share time-series plot with recession shading."""
    valid = ratio.notna() & (dates >= pd.Timestamp('1970-01-01'))
    dates, ratio = dates[valid], ratio[valid]
    fig, ax = new_figure()
    ax.plot(dates, ratio, color=palette[0], linewidth=2)

    last_date = dates.iloc[-1]
    last_year_tick = (last_date.year // 10) * 10       # round *down* to decade
    ax.set_xlim(pd.to_datetime('1970'), last_date)
    ax.set_xticks([pd.to_datetime(str(y))
                   for y in range(1970, last_year_tick + 1, 10)])
    ax.set_xticklabels(range(1970, last_year_tick + 1, 10), fontsize=11)

    ylim = (min(ylim[0], np.floor(ratio.min() / ytick_step) * ytick_step),
            max(ylim[1], np.ceil(ratio.max() / ytick_step) * ytick_step))
    ax.set_ylim(ylim)
    yticks = np.arange(
        np.ceil(ylim[0] / ytick_step) * ytick_step,
        ylim[1] + ytick_step / 2,
        ytick_step)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{100*x:.0f}' + r'\%' for x in yticks], fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('1970'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    add_source(ax, f'Source: StatCan, 36-10-0104-01 ({_quarter_label(last_date)}; prix courants)')
    save(fig, fname)


# =====================================================================
# Figure 8: GDP decomposition pie chart (most recent year)
# =====================================================================
def gdp_decomposition_canada():
    print('Figure 8: GDP decomposition pie chart')
    df = _load_gdp_accounts()

    # Use most recent full year of data
    complete = df.dropna(subset=['Gross domestic product at market prices']).groupby(df['REF_DATE'].dt.year).size()
    year = complete[complete == 4].index.max()
    dy = df[df['REF_DATE'].dt.year == year]

    # Components (World Bank convention: G = gov consumption only,
    # I = all capital formation including government investment)
    C = (dy['Final consumption expenditure'].mean()
         - dy['General governments final consumption expenditure'].mean())
    G = dy['General governments final consumption expenditure'].mean()
    I = (dy['Gross fixed capital formation'].mean()
         + dy['Investment in inventories'].mean())
    X = dy['Exports of goods and services'].mean()
    M = dy['Less: imports of goods and services'].mean()
    NX = X - M
    Y = dy['Gross domestic product at market prices'].mean()

    shares = [C / Y, I / Y, G / Y, np.abs(NX) / Y]
    labels = ['$C$', '$I$', '$G$', '$NX$']
    colors = [palette[0], palette[2], palette[1], palette[3]]

    fig, ax = plt.subplots(figsize=(7, 5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    # Place percentage labels at wedge centroids
    pct_labels = [f'{100*s:.0f}\\%' for s in shares]
    # NX label shows sign
    nx_sign = '$-$' if NX < 0 else ''
    pct_labels[3] = f'{nx_sign}{100*np.abs(NX)/Y:.0f}\\%'

    wedges, texts = ax.pie(
        shares, labels=labels, colors=colors,
        startangle=90, counterclock=False,
        textprops={'fontsize': 20, 'fontweight': 'bold'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2})

    # Add percentage inside each large wedge (at 0.55 radius)
    for i, (wedge, pct) in enumerate(zip(wedges, pct_labels)):
        ang = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
        if i < 3:  # C, I, G — label inside
            x = 0.55 * np.cos(ang)
            y = 0.55 * np.sin(ang)
            ax.text(x, y, pct, fontsize=18, fontweight='bold',
                    color='white', ha='center', va='center')
        else:  # NX — label outside with leader line
            ax.annotate(pct,
                        xy=(0.95 * np.cos(ang), 0.95 * np.sin(ang)),
                        xytext=(1.35 * np.cos(ang), 1.35 * np.sin(ang)),
                        fontsize=18, fontweight='bold', ha='center',
                        arrowprops=dict(arrowstyle='-', color='black',
                                        lw=0.8))

    add_source(ax, f'Source: StatCan ({year}; prix courants)')
    if NX < 0:
        ax.text(0.5, -0.06, '$NX < 0$ : aire représentée en valeur absolue.',
                transform=ax.transAxes, ha='center', fontsize=8, color=palette[7])
    save(fig, 'gdp_decomposition_canada.pdf')


# =====================================================================
# Figure 8b: GDP decomposition — 4-country comparison
# =====================================================================
def gdp_decomposition_4countries():
    print('Figure 8b: GDP decomposition — 4-country comparison')

    # World Bank indicator codes (most recent year available)
    # NE.CON.PRVT.ZS  Household final consumption (% of GDP)
    # NE.GDI.TOTL.ZS  Gross capital formation (% of GDP)
    # NE.CON.GOVT.ZS  Government final consumption (% of GDP)
    # NE.RSB.GNFS.ZS  External balance (Net exports, % of GDP)
    indicators = {
        'C': 'NE.CON.PRVT.ZS',
        'I': 'NE.GDI.TOTL.ZS',
        'G': 'NE.CON.GOVT.ZS',
        'NX': 'NE.RSB.GNFS.ZS',
    }
    countries = {
        'CAN': 'Canada',
        'USA': r"États-Unis",
        'CHN': 'Chine',
        'BRA': r"Brésil",
    }

    panel, year = worldbank_panel(list(indicators.values()), countries)
    panel = panel.set_index('iso')
    data = {name: {comp: panel.loc[iso, ind] for comp, ind in indicators.items()}
            for iso, name in countries.items()}

    colors = [palette[0], palette[2], palette[1], palette[3]]  # C, I, G, NX
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.5))
    fig.patch.set_alpha(0.0)
    fig.subplots_adjust(top=0.85)

    for ax, (name, comps) in zip(axes, data.items()):
        ax.patch.set_alpha(0.0)
        C, I, G = comps['C'], comps['I'], comps['G']
        NX = comps.get('NX', 0) or 0
        nx_sign = '$-$' if NX < 0 else ''
        shares = [C, I, G, np.abs(NX)]
        labels = ['$C$', '$I$', '$G$',
                  f'$NX$\n{nx_sign}{np.abs(NX):.1f}\\%']

        wedges, texts = ax.pie(
            shares, labels=labels, colors=colors,
            startangle=90, counterclock=False,
            textprops={'fontsize': 18, 'fontweight': 'bold'},
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
            labeldistance=1.15)

        # Percentage labels inside large wedges (C, I, G)
        for i in range(3):
            wedge = wedges[i]
            ang = np.deg2rad((wedge.theta1 + wedge.theta2) / 2)
            val = [C, I, G][i]
            ax.text(0.55 * np.cos(ang), 0.55 * np.sin(ang),
                    f'{val:.0f}\\%',
                    fontsize=18, fontweight='bold', color='white',
                    ha='center', va='center')

        ax.set_title(f'\\textbf{{{name}}}', fontsize=20, pad=20)

    fig.suptitle(f'Source: Banque mondiale ({year}; prix courants; aire de NX en valeur absolue)',
                 x=0.99, y=0.99, fontsize=8, ha='right', va='top')
    save(fig, 'gdp_decomposition_4countries.pdf')


# =====================================================================
# Figure 9: Consumption share of GDP
# =====================================================================
def consumption_share_gdp():
    print('Figure 9: Consumption share of GDP')
    df = _load_gdp_accounts()
    df['Consumption'] = (df['Final consumption expenditure']
                         - df['General governments final consumption expenditure'])
    ratio = df['Consumption'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$C / Y$',
                    ylim=(0.50, 0.60), ytick_step=0.02,
                    fname='consumption_share_gdp.pdf')


# =====================================================================
# Figure 9: Investment share of GDP
# =====================================================================
def investment_share_gdp():
    print('Figure 9: Investment share of GDP')
    df = _load_gdp_accounts()
    df['Investment'] = (df['Gross fixed capital formation']
                        + df['Investment in inventories'])
    ratio = df['Investment'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$I / Y$',
                    ylim=(0.16, 0.28), ytick_step=0.02,
                    fname='investment_share_gdp.pdf')


# =====================================================================
# Figure 10: Government spending share of GDP
# =====================================================================
def government_share_gdp():
    print('Figure 10: Government spending share of GDP')
    df = _load_gdp_accounts()
    df['Government'] = df['General governments final consumption expenditure']
    ratio = df['Government'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$G / Y$',
                    ylim=(0.18, 0.26), ytick_step=0.02,
                    fname='government_share_gdp.pdf')


# =====================================================================
# Figure 11: Trade share of GDP
# =====================================================================
def trade_share_gdp():
    print('Figure 11: Trade share of GDP')
    df = _load_gdp_accounts()
    # Exports + |Imports| = total two-way trade (openness measure)
    df['Trade'] = (df['Exports of goods and services']
                   + df['Less: imports of goods and services'].abs())
    ratio = df['Trade'] / df['Gross domestic product at market prices']
    _gdp_share_plot(df['REF_DATE'], ratio,
                    ylabel=r'$(X + M) / Y$',
                    ylim=(0.30, 0.70), ytick_step=0.10,
                    fname='trade_share_gdp.pdf')


def _gdp_cycle_data():
    """Consistent fixed-2017-price levels; a linear HP filter permits negatives.

    Filter the full 1961-onward sample, then display 1981 onward. No logarithm
    is applied to inventory investment, which is a signed flow. Constant-price
    fixed investment plus inventory investment defines total I. Linearity gives
    an exact decomposition of its cycle into fixed and inventory components.
    """
    df = remaining_frame('gdp_constant_prices', parse_dates=['REF_DATE'])
    df = df.pivot(index='REF_DATE', columns='Estimates', values='VALUE')
    levels = pd.DataFrame({
        'C': df['Household final consumption expenditure']
             + df["Non-profit institutions serving households' final consumption expenditure"],
        'I_fixed': df['Gross fixed capital formation'],
        'I_stocks': df['Investment in inventories'],
        'G': df['General governments final consumption expenditure'],
    }).dropna()
    levels['I'] = levels['I_fixed'] + levels['I_stocks']
    expected = pd.date_range(levels.index[0], levels.index[-1], freq='QS')
    if not levels.index.equals(expected) or not (levels[['C', 'I', 'G']] > 0).all().all():
        raise ValueError('Cycles require complete quarterly C/I/G levels.')
    cycles, trends = pd.DataFrame(index=levels.index), pd.DataFrame(index=levels.index)
    for column in levels:
        cycles[column], trends[column] = hpfilter(levels[column], lamb=1600)
    if not (trends[['C', 'I', 'G']] > 0).all().all():
        raise ValueError('C/I/G trend denominators must be positive.')
    if not np.allclose(cycles['I'], cycles['I_fixed'] + cycles['I_stocks'],
                       rtol=1e-8, atol=1e-5):
        raise ValueError('Investment cycle decomposition failed to reconcile.')
    return levels.loc['1981-01-01':], cycles.loc['1981-01-01':], trends.loc['1981-01-01':]


def _draw_gdp_cycles(data, series, ylabel, fname, tick_suffix=r'\%'):
    last_date = data.index[-1]
    fig, ax = new_figure(9, 4.5)
    for label, column, color, width in series:
        ax.plot(data.index, data[column], label=label, color=color,
                linestyle='-', linewidth=width, zorder=3)
    for start, end in recessions_ca:
        if end >= data.index[0]:
            ax.axvspan(max(start, data.index[0]), min(end, last_date),
                       color='grey', alpha=0.18, linewidth=0, zorder=0)
    ax.axhline(0, color=palette[7], linewidth=0.8, zorder=2)
    ax.set_xlim(data.index[0], last_date)
    first_year = data.index[0].year
    tick_years = [first_year] + list(range((first_year // 10 + 1) * 10, last_date.year + 1, 10))
    ticks = [pd.Timestamp(year, 1, 1) for year in tick_years]
    ax.set_xticks(ticks)
    ax.set_xticklabels([date.year for date in ticks], fontsize=11)
    lower = np.floor(data.to_numpy().min() / 5) * 5
    upper = np.ceil(data.to_numpy().max() / 5) * 5
    ticks_y = np.arange(lower, upper + 1, 5)
    ax.set_ylim(lower, upper)
    ax.set_yticks(ticks_y)
    ax.set_yticklabels([f'{value:.0f}' + tick_suffix for value in ticks_y], fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)
    style_axes(ax)
    ax.legend(loc='upper right', ncol=3, frameon=False, fontsize=11,
              columnspacing=1.2, handlelength=2)
    ax.text(0.01, 0.02, 'Zones grisées : récessions', transform=ax.transAxes,
            fontsize=8, ha='left', va='bottom', color=palette[7])
    add_source(ax, f'Source: StatCan, 36-10-0123-01 ({_quarter_label(last_date)}); prix constants de 2017, filtre HP ($\\lambda = 1600$).')
    save(fig, fname)


def gdp_component_cycles():
    """C, total I and G: percentage deviations from their own level trends."""
    print('Figure: GDP expenditure cycles (Canada)')
    _, cycles, trends = _gdp_cycle_data()
    data = 100 * cycles[['C', 'I', 'G']] / trends[['C', 'I', 'G']]
    _draw_gdp_cycles(data, [('$C$', 'C', palette[0], 1.7),
                            ('$I$', 'I', palette[2], 1.7),
                            ('$G$', 'G', palette[1], 1.7)],
                     r'Écart à la tendance (\%)', 'gdp_component_cycles.pdf')


def investment_cycles_breakdown():
    """Additive cycle contributions, in percentage points of total I's trend."""
    print('Figure: Fixed investment and inventory cycle contributions')
    _, cycles, trends = _gdp_cycle_data()
    data = cycles[['I', 'I_fixed', 'I_stocks']].div(trends['I'], axis=0) * 100
    _draw_gdp_cycles(data, [('Total ($I$)', 'I', palette[2], 2.2),
                            ('Capital fixe', 'I_fixed', palette[0], 1.7),
                            ('Variation des stocks', 'I_stocks', palette[1], 1.7)],
                     r'Contribution au cycle de $I$ (pp)',
                     'investment_cycles_breakdown.pdf', tick_suffix='')


# =====================================================================
# Figure: Real GDP — Canada vs USA (quarterly, indexed)
# =====================================================================
def gdp_canada_usa():
    print('Figure: Real GDP — Canada vs USA (quarterly)')
    can = _can_gdp()
    usa = remaining_series('us_gdp')

    # Index to 2000Q1 = 100
    can_base = can.loc['2000-01-01':'2000-03-31'].iloc[0]
    usa_base = usa.loc['2000-01-01':'2000-03-31'].iloc[0]
    can_idx = (can / can_base * 100).loc['2000-01-01':]
    usa_idx = (usa / usa_base * 100).loc['2000-01-01':]

    fig, ax = new_figure()
    ax.plot(can_idx, color=palette[0], linewidth=2.5, label='Canada')
    ax.plot(usa_idx, color=palette[1], linewidth=2.5,
            label=r"États-Unis")

    last_date = max(can_idx.dropna().index[-1], usa_idx.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2000-01-01'), last_date)
    xticks = [pd.to_datetime(str(y)) for y in range(2000, last_date.year + 1, 5)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([d.year for d in xticks], fontsize=11)

    ymax = tick_ceil(max(can_idx.max(), usa_idx.max()), 10)
    ax.set_ylim(100, ymax)
    ax.set_yticks(range(100, ymax + 1, 10))
    ax.set_yticklabels(range(100, ymax + 1, 10), fontsize=11)
    ax.set_ylabel(r"PIB réel (2000T1 = 100)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2000'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=11, loc='upper left')
    add_source(ax, f'Source: StatCan; BEA/FRED ({_quarter_label(last_date)})')
    save(fig, 'gdp_canada_usa.pdf')


# =====================================================================
# Figure: Real GDP per capita — Canada vs USA (quarterly, indexed)
# =====================================================================
def gdp_per_capita_canada_usa():
    print('Figure: Real GDP per capita — Canada vs USA (quarterly)')
    # Official quarterly series avoid extrapolating annual population.
    can_pc = remaining_series('can_gdp_per_capita')
    usa_pc = remaining_series('us_gdp_per_capita')

    # Index to 2000Q1 = 100
    can_base = can_pc.loc['2000-01-01':'2000-03-31'].iloc[0]
    usa_base = usa_pc.loc['2000-01-01':'2000-03-31'].iloc[0]
    can_idx = (can_pc / can_base * 100).loc['2000-01-01':]
    usa_idx = (usa_pc / usa_base * 100).loc['2000-01-01':]

    fig, ax = new_figure()
    ax.plot(can_idx, color=palette[0], linewidth=2.5, label='Canada')
    ax.plot(usa_idx, color=palette[1], linewidth=2.5,
            label=r"États-Unis")

    last_date = max(can_idx.dropna().index[-1], usa_idx.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2000-01-01'), last_date)
    xticks = [pd.to_datetime(str(y)) for y in range(2000, last_date.year + 1, 5)]
    ax.set_xticks(xticks)
    ax.set_xticklabels([d.year for d in xticks], fontsize=11)

    ymax = tick_ceil(max(can_idx.max(), usa_idx.max()), 10)
    ax.set_ylim(100, ymax)
    ax.set_yticks(range(100, ymax + 1, 10))
    ax.set_yticklabels(range(100, ymax + 1, 10), fontsize=11)
    ax.set_ylabel(r"PIB réel par hab. (2000T1 = 100)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2000'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=11, loc='upper left')
    add_source(ax, f'Source: StatCan; BEA/FRED ({_quarter_label(last_date)})')
    save(fig, 'gdp_per_capita_canada_usa.pdf')


# =====================================================================
# Figure: GDP per capita vs GDP — cross-country scatter
# =====================================================================
def gdp_vs_gdp_per_capita():
    print('Figure: GDP per capita vs GDP — cross-country scatter')
    # GDP, PPP (constant 2021 international $)
    gdp_ind = 'NY.GDP.MKTP.PP.KD'
    # GDP per capita, PPP (constant 2021 international $)
    gdppc_ind = 'NY.GDP.PCAP.PP.KD'
    # Population (for bubble sizes)
    pop_ind = 'SP.POP.TOTL'

    panel, year = worldbank_panel([gdp_ind, gdppc_ind, pop_ind])
    df = panel.rename(columns={gdp_ind: 'gdp', gdppc_ind: 'gdppc', pop_ind: 'pop'})
    df['gdp'] = df['gdp'] / 1e12
    df = df[(df.gdp > 0) & (df.gdppc > 0)]

    # Highlight countries (ISO → French display label)
    highlights = {
        'USA': r"États-Unis", 'CAN': 'Canada', 'CHN': 'Chine',
        'IND': 'Inde', 'BRA': r"Brésil", 'NGA': r"Nigéria",
        'NOR': r"Norvège", 'LUX': 'Luxembourg',
    }

    fig, ax = new_figure()

    # Bubble sizes proportional to population
    max_pop = df['pop'].max()
    sizes = 500 * (df['pop'] / max_pop) ** 0.5
    sizes = sizes.clip(lower=12)

    ax.scatter(df['gdp'], df['gdppc'], s=sizes,
               color=palette[0], alpha=0.35, edgecolors='white',
               linewidth=0.5)

    # Highlight specific countries
    for iso, name in highlights.items():
        row = df[df['iso'] == iso]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        sz = 500 * (row['pop'] / max_pop) ** 0.5
        sz = max(sz, 12)
        color = palette[1] if iso == 'CAN' else palette[0]
        ax.scatter(row['gdp'], row['gdppc'], s=sz,
                   color=color, alpha=0.7, edgecolors='white', linewidth=0.5,
                   zorder=5)
        # Offset tuning
        offsets = {
            'USA': (12, 10), 'CAN': (12, 12), 'CHN': (12, -16),
            'IND': (12, 8), 'BRA': (12, -14), 'NGA': (-55, -10),
            'NOR': (-55, 14), 'LUX': (10, -14),
        }
        ox, oy = offsets.get(iso, (12, 8))
        ax.annotate(name, xy=(row['gdp'], row['gdppc']),
                    xytext=(ox, oy), textcoords='offset points',
                    fontsize=9, fontweight='bold', color='black',
                    arrowprops=dict(arrowstyle='-', color=palette[7],
                                    lw=0.8, shrinkB=3),
                    zorder=10)

    ax.set_xscale('log')
    ax.set_xlim(0.005, 80)
    ax.set_xticks([0.01, 0.1, 1, 10])
    ax.set_xticklabels([r'\$0.01T', r'\$0.1T', r'\$1T', r'\$10T'],
                       fontsize=11)
    ax.set_xlabel(r"PIB réel, PPA (milliers de Mds, \$ int. 2021)",
                  fontsize=11)

    ax.set_yscale('log')
    ax.set_ylim(800, 150000)
    yticks = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    ax.set_yticks(yticks)
    ax.set_yticklabels([r'\$1K', r'\$2K', r'\$5K', r'\$10K',
                        r'\$20K', r'\$50K', r'\$100K'], fontsize=11)
    ax.set_ylabel(r"PIB réel par habitant (PPA)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    add_source(ax, f'Source: Banque mondiale, WDI ({year})')
    save(fig, 'gdp_vs_gdp_per_capita.pdf')


# =====================================================================
# Figure: Real GDP at PPP — horizontal bar chart of top economies
# =====================================================================
def gdp_ppp_time_series():
    print('Figure: Real GDP at PPP — top economies bar chart')
    # World Bank: GDP, PPP (constant 2021 international $)
    indicator = 'NY.GDP.MKTP.PP.KD'

    # Top 12 economies by GDP PPP (approximate ordering)
    # ISO → (English name for API, French label for display)
    countries_iso = {
        'CHN': ('China', 'Chine'),
        'USA': ('United States', r"États-Unis"),
        'IND': ('India', 'Inde'),
        'JPN': ('Japan', 'Japon'),
        'DEU': ('Germany', 'Allemagne'),
        'RUS': ('Russia', 'Russie'),
        'IDN': ('Indonesia', r"Indonésie"),
        'BRA': ('Brazil', r"Brésil"),
        'GBR': ('United Kingdom', 'Royaume-Uni'),
        'FRA': ('France', 'France'),
        'MEX': ('Mexico', 'Mexique'),
        'CAN': ('Canada', 'Canada'),
    }

    panel, year = worldbank_panel([indicator], countries_iso)
    panel = panel.set_index('iso')
    data = {name_fr: panel.loc[iso, indicator] / 1e12
            for iso, (_, name_fr) in countries_iso.items()}

    # Largest economies at the top of the horizontal chart.
    data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    names = list(data.keys())
    values = list(data.values())
    colors = [palette[1] if n == 'Canada' else palette[0] for n in names]

    bars = ax.barh(names, values, color=colors, height=0.65, edgecolor='white',
                   linewidth=0.5)

    # Value labels at end of each bar
    for bar, val in zip(bars, values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
                f'\\${val:.1f}T', va='center', fontsize=10, color=palette[7])

    ax.set_xlim(0, max(values) * 1.2)
    ax.set_xticks([])
    ax.tick_params(axis='y', labelsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.invert_yaxis()

    ax.set_title(r"PIB réel en PPA (milliers de Mds, \$ int. 2021)",
                 fontsize=12, loc='left', pad=10)
    add_source(ax, f'Source: Banque mondiale, WDI ({year})')
    save(fig, 'gdp_ppp_world.pdf')


# =====================================================================
# Figure: GDP per capita vs price level (cross-section scatter)
# =====================================================================
def gdp_per_capita_vs_price_level():
    print('Figure: GDP per capita vs price level')
    # GDP per capita, PPP (constant 2021 international $)
    gdppc_ind = 'NY.GDP.PCAP.PP.KD'
    # PPP conversion factor, GDP (LCU per international $)
    ppp_ind = 'PA.NUS.PPP'
    # Official exchange rate (LCU per US$, period average)
    xr_ind = 'PA.NUS.FCRF'
    # Population
    pop_ind = 'SP.POP.TOTL'

    panel, year = worldbank_panel([gdppc_ind, ppp_ind, xr_ind, pop_ind])
    df = panel.rename(columns={gdppc_ind: 'gdppc', pop_ind: 'pop'})
    df['price_level'] = df[ppp_ind] / df[xr_ind]
    us_price = df.loc[df.iso == 'USA', 'price_level'].iloc[0]
    df['price_level'] = df['price_level'] / us_price
    df = df[(df.gdppc > 500) & (df.price_level > 0.05)]

    # Highlight countries (ISO → French display label)
    highlights = {
        'USA': r"États-Unis", 'CAN': 'Canada', 'CHN': 'Chine',
        'IND': 'Inde', 'JPN': 'Japon', 'BRA': r"Brésil",
        'NGA': r"Nigéria", 'NOR': r"Norvège", 'CHE': 'Suisse',
    }

    fig, ax = new_figure()

    # Bubble sizes proportional to population
    max_pop = df['pop'].max()
    sizes = 500 * (df['pop'] / max_pop) ** 0.5
    sizes = sizes.clip(lower=12)

    ax.scatter(df['gdppc'], df['price_level'], s=sizes,
               color=palette[0], alpha=0.45, edgecolors='white',
               linewidth=0.5)

    # Highlight specific countries with arrows connecting labels to dots
    for iso, name in highlights.items():
        row = df[df['iso'] == iso]
        if len(row) == 0:
            continue
        row = row.iloc[0]
        sz = 500 * (row['pop'] / max_pop) ** 0.5
        sz = max(sz, 12)
        color = palette[1] if iso == 'CAN' else palette[0]
        ax.scatter(row['gdppc'], row['price_level'], s=sz,
                   color=color, alpha=0.85, edgecolors='white', linewidth=0.5,
                   zorder=5)
        # Offset in points — tuned to avoid overlap at figsize (9, 4.5)
        offsets = {
            'USA': (12, 10), 'CAN': (-50, -14), 'CHN': (14, 10),
            'IND': (12, -14), 'JPN': (-45, 14), 'BRA': (-45, 10),
            'NGA': (-52, -10), 'NOR': (-55, -14), 'CHE': (-65, -8),
        }
        ox, oy = offsets.get(iso, (12, 8))
        ax.annotate(name, xy=(row['gdppc'], row['price_level']),
                    xytext=(ox, oy), textcoords='offset points',
                    fontsize=9, fontweight='bold', color='black',
                    arrowprops=dict(arrowstyle='-', color=palette[7],
                                    lw=0.8, shrinkB=3),
                    zorder=10)

    ax.set_xscale('log')
    ax.set_xlim(1000, 150000)
    ax.set_xticks([1000, 10000, 100000])
    ax.set_xticklabels([r'\$1,000', r'\$10,000', r'\$100,000'], fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant (PPA)", fontsize=11)
    ax.set_ylim(0.05, 1.2)
    ax.set_yticks(np.arange(0.2, 1.2 + 0.01, 0.2))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(0.2, 1.2 + 0.01, 0.2)],
                       fontsize=11)
    ax.set_ylabel(r'$P\,/\,P^{US}$', fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray', linestyle=':', linewidth=0.5)
    add_source(ax, f'Source: Banque mondiale, WDI ({year})')
    save(fig, 'gdp_per_capita_vs_price_level.pdf')


# =====================================================================
# Figure: Big Mac Index — dot chart (Economist-style)
# =====================================================================
def big_mac_index():
    print('Figure: Big Mac Index — dot chart')
    df = remaining_frame('big_mac')

    # Two most recent dates
    dates = sorted(df['date'].unique())
    d_latest = dates[-1]
    d_prev = dates[-2]

    latest = df[df['date'] == d_latest].set_index('iso_a3')
    prev = df[df['date'] == d_prev].set_index('iso_a3')

    # Selected countries (mix of over- and under-valued)
    selected = [
        'CHE', 'NOR', 'EUZ', 'GBR', 'USA', 'CAN', 'SWE',
        'TUR', 'SGP', 'MEX', 'KOR', 'BRA', 'CHN', 'JPN',
        'VNM', 'IND', 'TWN',
    ]

    rows = []
    for iso in selected:
        if iso in latest.index:
            row = {'iso': iso, 'name': latest.loc[iso, 'name'],
                   'pct_latest': latest.loc[iso, 'USD_raw'] * 100,
                   'price_latest': latest.loc[iso, 'dollar_price']}
            if iso in prev.index:
                row['pct_prev'] = prev.loc[iso, 'USD_raw'] * 100
            else:
                row['pct_prev'] = np.nan
            rows.append(row)

    rdf = pd.DataFrame(rows)
    # Sort by latest valuation descending
    rdf = rdf.sort_values('pct_latest', ascending=True).reset_index(drop=True)

    # Translate country names to French for y-axis labels
    rdf['name_fr'] = rdf['name'].replace({'Britain': 'Royaume-Uni'}).apply(_tr)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    y = np.arange(len(rdf))

    # Previous period dots (lighter)
    ax.scatter(rdf['pct_prev'], y, s=55, color=palette[2], alpha=0.3,
               zorder=3, label=_source_month(pd.Timestamp(d_prev)))
    # Latest dots
    colors = [palette[1] if iso == 'CAN' else palette[2] for iso in rdf['iso']]
    ax.scatter(rdf['pct_latest'], y, s=65, color=colors, alpha=0.85,
               zorder=4, label=_source_month(pd.Timestamp(d_latest)))

    # Zero line
    ax.axvline(x=0, color='black', linewidth=0.8)

    # Price labels on the right margin (right-aligned)
    data_min = min(rdf.pct_latest.min(), rdf.pct_prev.min())
    data_max = max(rdf.pct_latest.max(), rdf.pct_prev.max())
    left = np.floor(data_min / 20) * 20 - 5
    right_data = np.ceil(data_max / 20) * 20
    price_x = right_data + 20
    for i, row in rdf.iterrows():
        idx = rdf.index.get_loc(i)
        ax.text(price_x, idx, f'\\${row["price_latest"]:.2f}',
                va='center', ha='right', fontsize=9, color=palette[7])

    # Country names on the left (French)
    ax.set_yticks(y)
    ax.set_yticklabels(rdf['name_fr'], fontsize=10)

    # x-axis
    ax.set_xlim(left, price_x + 6)
    ax.set_ylim(-0.7, len(rdf) + 1.5)
    xticks = np.arange(np.ceil(left / 20) * 20, right_data + 1, 20).astype(int)
    ax.set_xticks(list(xticks))
    ax.set_xticklabels([f'{x:+d}' if x != 0 else '0' for x in xticks],
                       fontsize=10)
    ax.set_xlabel(r"Évaluation de la monnaie locale face au dollar, \%",
                  fontsize=10)

    # Price column header — right-aligned, same x as price labels
    ax.text(price_x, len(rdf) + 0.3,
            'Prix, \\$', fontsize=9, fontweight='bold',
            va='bottom', ha='right', color=palette[0])

    # Horizontal grid lines
    for yi in y:
        ax.axhline(y=yi, xmin=0, xmax=(right_data - left) / (price_x + 6 - left),
                   color='gray', linewidth=0.3, alpha=0.5)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(axis='y', length=0)

    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=9, loc='upper left',
              bbox_to_anchor=(0.0, 1.0), ncol=2,
              markerscale=1.2)
    add_source(ax, r"Source: \textit{The Economist}, Big Mac Index")
    save(fig, 'big_mac_index.pdf')


# ── Shared helper for GDP growth plots ────────────────────────────────
def _gdp_growth_plot(real_g, nom_g, show_real, fname):
    """Plot nominal (and optionally real) GDP growth for Canada."""
    fig, ax = new_figure()
    ax.plot(nom_g, color=palette[0], linewidth=2, label='Nominal')
    if show_real:
        ax.plot(real_g, color=palette[1], linewidth=2, label=r"Réel")
    ax.axhline(y=0, color='black', linewidth=0.5)

    first_year = max(real_g.dropna().index[0].year, 1962)
    last_date = max(real_g.dropna().index[-1], nom_g.dropna().index[-1])
    last_year_tick = (last_date.year // 10) * 10
    ax.set_xlim(pd.to_datetime(str(first_year)), last_date)
    tick_years = list(range(first_year, last_date.year + 1, 10))
    ax.set_xticks([pd.to_datetime(str(y)) for y in tick_years])
    ax.set_xticklabels(tick_years, fontsize=11)
    ax.set_xlim(pd.to_datetime(str(first_year)), last_date)

    visible = pd.concat([nom_g.loc[str(first_year):], real_g.loc[str(first_year):]])
    ymin = min(-0.10, np.floor(visible.min() / 0.05) * 0.05)
    ymax = max(0.25, np.ceil(visible.max() / 0.05) * 0.05)
    ax.set_ylim(ymin, ymax)
    yticks = np.arange(ymin, ymax + 0.001, 0.05)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{100*x:.0f}' + r'\%' for x in yticks], fontsize=11)
    ax.set_ylabel(r"Croissance du PIB", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime(str(first_year)):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=11, loc='lower left',
              bbox_to_anchor=(0.0, 0.0))
    add_source(ax, f'Source: StatCan ({_quarter_label(last_date)}; variation sur 4 trimestres)')
    save(fig, fname)


# =====================================================================
# Figure: Nominal GDP growth — Canada (alone)
# =====================================================================
def gdp_nominal_canada():
    print('Figure: Nominal GDP growth — Canada')
    real = _can_gdp()
    nom = _can_gdp(real=False)
    real_g = real.pct_change(4, fill_method=None).dropna()
    nom_g = nom.pct_change(4, fill_method=None).dropna()
    _gdp_growth_plot(real_g, nom_g, show_real=False, fname='gdp_nominal_canada.pdf')


# =====================================================================
# Figure: Nominal vs real GDP growth — Canada
# =====================================================================
def gdp_nominal_real_canada():
    print('Figure: Nominal vs real GDP growth — Canada')
    real = _can_gdp()
    nom = _can_gdp(real=False)
    real_g = real.pct_change(4, fill_method=None).dropna()
    nom_g = nom.pct_change(4, fill_method=None).dropna()
    _gdp_growth_plot(real_g, nom_g, show_real=True, fname='gdp_nominal_real_canada.pdf')


# =====================================================================
# Figure: CPI vs GDP deflator inflation — Canada (recent)
# =====================================================================
def inflation_cpi_deflator_canada():
    print('Figure: CPI vs GDP deflator inflation — Canada')
    cpi = intro_series('cpi')
    cpi_infl = cpi.pct_change(12, fill_method=None).dropna()

    # GDP deflator = nominal GDP / real GDP -> 4-quarter % change
    nom_gdp = _can_gdp(real=False)
    real_gdp = _can_gdp()
    deflator = nom_gdp / real_gdp
    defl_infl = deflator.pct_change(4, fill_method=None).dropna()

    fig, ax = new_figure()

    # BoC target band (1-3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC")

    ax.plot(cpi_infl, color=palette[0], linewidth=2, label='IPC')
    ax.plot(defl_infl, color=palette[2], linewidth=2,
            label=r"Déflateur du PIB")

    last_date = max(cpi_infl.dropna().index[-1], defl_infl.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2016'), last_date)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2016, last_date.year + 1)])
    ax.set_xticklabels(range(2016, last_date.year + 1), fontsize=11)

    ymax = max(0.10, np.ceil(defl_infl.loc['2016':].max() / 0.02) * 0.02)
    ax.set_ylim(-0.02, ymax)
    ax.set_yticks(np.arange(-0.02, ymax + 0.001, 0.02))
    ax.set_yticklabels([f'{100*x:.0f}' + r'\%' for x in np.arange(-0.02, ymax + 0.001, 0.02)],
                       fontsize=11)
    ax.set_ylabel(r"Inflation (sur 12 mois)", fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2016'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, f'Source: StatCan (IPC : {_source_month(last_date)}; déflateur : {_quarter_label(defl_infl.index[-1])})')
    save(fig, 'inflation_cpi_deflator_canada.pdf')


# =====================================================================
# Figure: Headline vs core CPI inflation — Canada
# =====================================================================
def inflation_headline_core_canada():
    print('Figure: Headline vs core CPI inflation — Canada')
    cpi = intro_series('cpi')
    headline = cpi.pct_change(12, fill_method=None).dropna()

    core_cpi = remaining_series('core_cpi')
    core = core_cpi.pct_change(12, fill_method=None).dropna()

    fig, ax = new_figure()

    # BoC target band (1-3%)
    ax.axhspan(0.01, 0.03, color=palette[1], alpha=0.12, linewidth=0)
    ax.axhline(y=0.02, color=palette[1], linestyle=':', linewidth=1.5,
               label=r"Cible de 2\% de la BdC")

    ax.plot(headline, color=palette[0], linewidth=2, label='IPC global')
    ax.plot(core, color=palette[2], linewidth=2,
            label=r"IPC de base (hors alim. \& énergie)")

    last_date = max(headline.dropna().index[-1], core.dropna().index[-1])
    ax.set_xlim(pd.to_datetime('2016'), last_date)
    ax.set_xticks([pd.to_datetime(str(y)) for y in range(2016, last_date.year + 1)])
    ax.set_xticklabels(range(2016, last_date.year + 1), fontsize=11)

    ax.set_ylim(-0.02, 0.10)
    ax.set_yticks(np.arange(-0.02, 0.10 + 0.001, 0.02))
    ax.set_yticklabels([f'{x:.0f}' + r'\%' for x in np.arange(-2, 10 + 0.1, 2)],
                       fontsize=11)
    ax.set_ylabel(r"Inflation IPC (sur 12 mois)", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    for start, end in recessions_ca:
        if start >= pd.to_datetime('2016'):
            ax.axvspan(start, end, color='grey', alpha=0.3, linewidth=0)

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, f'Source: StatCan ({_source_month(last_date)})')
    save(fig, 'inflation_headline_core_canada.pdf')


# =====================================================================
# Figure: High-frequency online price indices (Cavallo et al.)
# =====================================================================
def inflation_highfreq_cavallo():
    print('Figure: High-frequency online prices (Cavallo et al.)')
    # PricingLab tracks US online retail prices, grouped by the goods' origin.
    # Imported-goods prices reflect tariff costs passed through by retailers;
    # they are not border import prices with a tariff mechanically added.
    # Methodology: https://www.pricinglab.org/tariff-tracker/
    df = remaining_frame('pricinglab', parse_dates=['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Convert to cumulative % change from first observation
    dom_pct = (df['index_domestic'] - 1) * 100
    imp_pct = (df['index_imported'] - 1) * 100

    fig, ax = new_figure()

    # Raw daily data
    ax.plot(df['date'], dom_pct, color=palette[0], linewidth=2,
            label='Biens domestiques')
    ax.plot(df['date'], imp_pct, color=palette[2], linewidth=2,
            label=r"Biens importés")

    ax.axhline(y=0, color='black', linewidth=0.5)

    # x-axis: monthly ticks
    first_date = df['date'].min()
    last_date = df['date'].max()
    xticks = pd.date_range(first_date.replace(day=1), last_date, freq='2MS')
    xticks = xticks[xticks >= first_date]
    ax.set_xlim(first_date, last_date)
    ax.set_xticks(xticks)
    ax.set_xticklabels([french_date_label(d) for d in xticks], fontsize=11)

    # y-axis
    ymin = int(np.floor(min(dom_pct.min(), imp_pct.min())))
    ymax = int(np.ceil(max(dom_pct.max(), imp_pct.max())))
    ax.set_ylim(ymin, ymax)
    yticks = np.arange(ymin, ymax + 0.1, 1)
    ax.set_yticks(yticks)
    ax.set_yticklabels([f'{x:+.0f}' + r'\%' for x in yticks], fontsize=11)
    ax.set_ylabel(r"Variation cumulée des prix", fontsize=11,
                  rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    # Keep the policy dates below the series and away from the legend.
    # March 4: Canada/Mexico tariffs take effect and the extra China duty rises.
    # April 2: announcement of reciprocal tariffs (baseline effective April 5).
    event_color = '#64748B'
    for date, label, offset, align in [
            ('2025-03-04', '4 mars\n2025', -4, 'right'),
            ('2025-04-02', '2 avril\n2025', 4, 'left')]:
        event_date = pd.Timestamp(date)
        ax.axvline(event_date, color=event_color, linewidth=0.9,
                   linestyle=(0, (3, 3)), alpha=0.7, zorder=1)
        ax.annotate(label, xy=(event_date, 0.04),
                    xycoords=('data', 'axes fraction'),
                    xytext=(offset, 0), textcoords='offset points',
                    ha=align, va='bottom', fontsize=8.5, color=event_color)

    # Label the observed holiday troughs, without changing the raw price data.
    # The paper documents holiday discounts in 2024; the repeating 2025 dip
    # bottoms out in the Black Friday/Cyber Monday weekend as well.
    for year, text_date, text_y in [
            (2024, '2024-10-14', -2.1),
            (2025, '2025-12-14', -0.6)]:
        holiday = df['date'].between(f'{year}-11-20', f'{year}-12-05')
        trough = imp_pct.loc[holiday].idxmin()
        ax.annotate(f'Vendredi\nfou {year}',
                    xy=(df.loc[trough, 'date'], imp_pct.loc[trough]),
                    xytext=(pd.Timestamp(text_date), text_y),
                    ha='left', va='center', fontsize=9, color=event_color,
                    arrowprops=dict(arrowstyle='->', color=event_color,
                                    linewidth=0.8, shrinkA=3, shrinkB=3))

    style_axes(ax)
    ax.legend(frameon=False, fontsize=11, loc='upper left')
    add_source(ax, fr'Source: Cavallo, Llamas \& Vázquez (PricingLab; {last_date.day} {_source_month(last_date)})')
    save(fig, 'inflation_highfreq_cavallo.pdf')


# =====================================================================
# Figure: HDI vs GDP per capita (cross-country scatter)
# =====================================================================
def hdi_vs_gdp_per_capita():
    print('Figure: HDI vs GDP per capita')
    hdi = remaining_frame('hdi').rename(columns={
        'Code': 'code', 'Year': 'year', 'Entity': 'entity',
        'Human Development Index': 'hdi'})
    wdi = remaining_frame('worldbank').rename(columns={
        'iso': 'code', 'NY.GDP.PCAP.PP.KD': 'ny_gdp_pcap_pp_kd',
        'SP.POP.TOTL': 'population_historical'})
    hdi = hdi[hdi.code.isin(wdi.code.unique())]
    df = hdi.merge(wdi[['code', 'year', 'ny_gdp_pcap_pp_kd', 'population_historical']],
                   on=['code', 'year'], validate='one_to_one')
    df = df.dropna(subset=['hdi', 'ny_gdp_pcap_pp_kd', 'population_historical'])
    coverage = df.groupby('year').code.nunique()
    year = int(coverage[coverage >= 150].index.max())
    df = df[df.year == year].copy()
    df['pop_share'] = df.population_historical / df.population_historical.sum()

    # Highlight countries
    highlights = {
        'USA': r"États-Unis", 'CAN': 'Canada', 'CHN': 'Chine',
        'IND': 'Inde', 'BRA': r"Brésil", 'NGA': r"Nigéria",
        'NOR': r"Norvège", 'JPN': 'Japon',
    }

    fig, ax = new_figure()

    # Bubble sizes proportional to population
    sizes = 800 * df['pop_share'] ** 0.5
    sizes = sizes.clip(lower=15)

    ax.scatter(df.ny_gdp_pcap_pp_kd, df.hdi, s=sizes,
               color=palette[0], alpha=0.45, edgecolors='white',
               linewidth=0.5)

    # Regression line (log GDP vs HDI)
    log_x = np.log(df.ny_gdp_pcap_pp_kd.values)
    y_vals = df.hdi.values
    slope, intercept = np.polyfit(log_x, y_vals, 1)
    x_line = np.linspace(np.log(1000), np.log(150000), 200)
    ax.plot(np.exp(x_line), slope * x_line + intercept,
            color=palette[1], linewidth=1.5, zorder=1)

    # Correlation coefficient
    corr = np.corrcoef(log_x, y_vals)[0, 1]
    ax.text(0.03, 0.95, f'$\\rho = {corr:.2f}$', fontsize=9, color=palette[7],
            ha='left', va='top', transform=ax.transAxes)

    # Highlight Canada with accent color
    can = df[df.code == 'CAN']
    if len(can) > 0:
        can = can.iloc[0]
        sz = max(800 * can['pop_share'] ** 0.5, 15)
        ax.scatter(can.ny_gdp_pcap_pp_kd, can.hdi, s=sz,
                   color=palette[1], alpha=0.7, edgecolors='white',
                   linewidth=0.5, zorder=5, label='Canada')
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=11)

    ax.set_xscale('log')
    ax.set_xlim(1000, 150000)
    ax.set_xticks([1000, 10000, 100000])
    ax.set_xticklabels([r'\$1,000', r'\$10,000', r'\$100,000'], fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant (PPA)", fontsize=11)

    ax.set_ylim(0.3, 1.0)
    ax.set_yticks(np.arange(0.3, 1.01, 0.1))
    ax.set_yticklabels([f'{x:.1f}' for x in np.arange(0.3, 1.01, 0.1)],
                       fontsize=11)
    ax.set_ylabel('IDH', fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray',
            linestyle=':', linewidth=0.5)
    add_source(ax, f'Source: UNDP/OWID; Banque mondiale ({year})')
    save(fig, 'hdi_vs_gdp_per_capita.pdf')


# =====================================================================
# Figure: Beyond GDP — Jones and Klenow (2016) welfare metric
# =====================================================================
def beyond_gdp():
    print('Figure: Beyond GDP — Jones and Klenow (2016)')
    df = remaining_frame('jones_klenow').copy()
    df['welfare'] = df['welfare'] / 100
    df['y'] = df['y'] / 100

    # This historical paper comparison uses populations from the same year.
    pops = remaining_frame('worldbank')
    pops = pops[pops.year == 2007].dropna(subset=['SP.POP.TOTL'])
    pop_by_name = dict(zip(pops.name, pops['SP.POP.TOTL']))

    # Match population to JK country names (fuzzy match common differences)
    name_map = {
        'Korea, Rep.': 'Korea, Republic of',
        'Iran, Islamic Rep.': 'Iran, Islamic Republic of',
        'Egypt, Arab Rep.': 'Egypt',
        'Venezuela, RB': 'Venezuela',
        'Russian Federation': 'Russia',
        'Slovak Republic': 'Slovakia',
        'Kyrgyz Republic': 'Kyrgyzstan',
        'Congo, Dem. Rep.': 'Congo, Democratic Republic of',
        'Cote d\'Ivoire': "C\u00f4te d'Ivoire",
    }
    df['pop'] = df['country'].apply(
        lambda c: pop_by_name.get(c.strip())
                  or pop_by_name.get(name_map.get(c.strip(), ''))
                  or None)
    # Fill missing with a small default so they still appear
    df['pop'] = df['pop'].fillna(df['pop'].min())

    fig, ax = new_figure()

    # 45-degree line
    ax.plot([1 / 100, 2.7], [1 / 100, 2.7], color=palette[1],
            linestyle='-', linewidth=1.5, zorder=1)

    # Bubble sizes proportional to population
    max_pop = df['pop'].max()
    sizes = 500 * (df['pop'] / max_pop) ** 0.5
    sizes = sizes.clip(lower=10)

    ax.scatter(df.y, df.welfare, s=sizes, color=palette[0], alpha=0.45,
               edgecolors='white', linewidth=0.5, zorder=3)

    # Correlation coefficient (log-log)
    corr = np.corrcoef(np.log(df.y.values), np.log(df.welfare.values))[0, 1]
    ax.text(0.03, 0.95, f'$\\rho = {corr:.2f}$', fontsize=9, color=palette[7],
            ha='left', va='top', transform=ax.transAxes)

    # Highlight Canada with accent color
    can = df[df['country'].str.strip() == 'Canada']
    if len(can) > 0:
        can = can.iloc[0]
        sz = max(500 * (can['pop'] / max_pop) ** 0.5, 10)
        ax.scatter(can.y, can.welfare, s=sz, color=palette[1], alpha=0.7,
                   edgecolors='white', linewidth=0.5, zorder=5, label='Canada')
    ax.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='none', framealpha=1, fontsize=11)

    ax.set_xscale('log', base=2)
    ax.set_xlim(1 / 100, 2.7)
    xticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
    ax.set_xticks(xticks)
    ax.set_xticklabels(['1/64', '1/32', '1/16', '1/8', '1/4', '1/2',
                         '1', '2'], fontsize=11)
    ax.set_xlabel(r"PIB réel par habitant (relatif aux É.-U.)",
                  fontsize=11)

    ax.set_yscale('log', base=2)
    ax.set_ylim(1 / 100, 2)
    yticks = [1/64, 1/32, 1/16, 1/8, 1/4, 1/2, 1, 2]
    ax.set_yticks(yticks)
    ax.set_yticklabels(['1/64', '1/32', '1/16', '1/8', '1/4', '1/2',
                         '1', '2'], fontsize=11)
    ax.set_ylabel(r'$\lambda$', fontsize=11, rotation=0, ha='left')
    ax.yaxis.set_label_coords(0, 1.02)

    style_axes(ax)
    ax.grid(True, which='major', axis='x', color='gray',
            linestyle=':', linewidth=0.5)
    add_source(ax, 'Source: Jones et Klenow (2016); données de 2007')
    save(fig, 'beyond_gdp.pdf')


# =====================================================================
# Figure: GDP / GNI ratio — horizontal bar chart (Ireland outlier)
# =====================================================================
def gdp_gni_ratio():
    print('Figure: GDP / GNI ratio — cross-country comparison')

    # Latest complete common-year WDI GDP/GNI comparison.
    countries = {
        'IRL': 'Irlande',
        'SGP': 'Singapour',
        'CAN': 'Canada',
        'USA': r"États-Unis",
        'DEU': 'Allemagne',
        'FRA': 'France',
        'JPN': 'Japon',
        'GBR': 'Royaume-Uni',
        'BRA': r"Brésil",
        'CHN': 'Chine',
        'IND': 'Inde',
        'PHL': 'Philippines',
    }

    gdp_ind = 'NY.GDP.MKTP.CD'
    gni_ind = 'NY.GNP.MKTP.CD'
    panel, year_used = worldbank_panel([gdp_ind, gni_ind], countries)
    panel = panel.set_index('iso')
    ratios = {name: panel.loc[iso, gdp_ind] / panel.loc[iso, gni_ind]
              for iso, name in countries.items()}

    # Sort by ratio (ascending for horizontal bars)
    ratios = dict(sorted(ratios.items(), key=lambda x: x[1], reverse=False))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    names = list(ratios.keys())
    values = list(ratios.values())
    colors = [palette[3] if n == 'Irlande' else
              palette[1] if n == 'Canada' else
              palette[0] for n in names]

    bars = ax.barh(names, values, color=colors, height=0.65,
                   edgecolor='white', linewidth=0.5)

    # Value labels
    for bar, val in zip(bars, values):
        label = f'{val:.2f}'
        ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                label, va='center', fontsize=10, color=palette[7])

    # Reference line at 1.0
    ax.axvline(1.0, color=palette[7], linewidth=0.8, linestyle='--', alpha=0.5)

    ax.set_xlim(min(values) - 0.05, max(values) + 0.08)
    ax.tick_params(axis='y', labelsize=11)
    ax.tick_params(axis='x', labelsize=10)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()

    ax.set_title('Ratio PIB / RNB', fontsize=12, loc='left', pad=10)
    add_source(ax, f'Source: World Bank, WDI ({year_used})')
    save(fig, 'gdp_gni_ratio.pdf')


# =====================================================================
# Main
# =====================================================================
if __name__ == '__main__':
    print('Generating Session 1 figures (French)...')
    print(f'Output: {FIGURES_DIR}\n')

    figures = [
        can_unemployment,
        can_inflation_longrun,
        policy_rates,
        canada_inflation_recent,
        canada_employment_exports,
        hockey_stick_world,
        us_tariff_rate,
        gdp_decomposition_canada,
        gdp_decomposition_4countries,
        consumption_share_gdp,
        investment_share_gdp,
        government_share_gdp,
        trade_share_gdp,
        gdp_component_cycles,
        investment_cycles_breakdown,
        gdp_ppp_time_series,
        gdp_per_capita_vs_price_level,
        big_mac_index,
        gdp_canada_usa,
        gdp_per_capita_canada_usa,
        gdp_vs_gdp_per_capita,
        gdp_gni_ratio,
        gdp_nominal_canada,
        gdp_nominal_real_canada,
        inflation_cpi_deflator_canada,
        inflation_headline_core_canada,
        inflation_highfreq_cavallo,
        hdi_vs_gdp_per_capita,
        beyond_gdp,
    ]

    if '--intro-only' in sys.argv:
        figures = figures[:7]
    elif '--remaining-only' in sys.argv:
        figures = figures[7:]

    failed = []
    for fn in figures:
        try:
            fn()
        except Exception as e:
            print(f'  \u2717 {fn.__name__}: {e}')
            failed.append(fn.__name__)

    if failed:
        print(f'\n{len(failed)} figure(s) failed: {", ".join(failed)}')
        sys.exit(1)
    else:
        print('\nDone \u2014 all figures generated.')
