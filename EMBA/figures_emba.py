"""Graphiques de la conjoncture canadienne.

Actualiser un graphique : python figures_emba.py --figure <nom>
Reproduire les graphiques avec les données de novembre :
  python figures_emba.py --snapshot ../Resources/emba_inflation_2026-11-22.json
  python figures_emba.py --figure travail --snapshot ../Resources/emba_travail_2026-11-22.json
  python figures_emba.py --figure douane --snapshot ../Resources/emba_emploi_douane_2026-11-22.json
  python figures_emba.py --figure intrants --snapshot ../Resources/emba_intrants_2026-11-23.json
  python figures_emba.py --figure pib --snapshot ../Resources/emba_pib_2026-11-22.json
  python figures_emba.py --figure exportations --snapshot ../Resources/emba_exportations_2026-11-22.json
  python figures_emba.py --figure taux --snapshot ../Resources/emba_taux_2026-11-22.json
  python figures_emba.py --figure intentions --snapshot ../Resources/emba_intentions_2026-11-22.json
  python figures_emba.py --figure demographie --snapshot ../Resources/emba_demographie_2026-11-22.json
  python figures_emba.py --figure ecart --snapshot ../Resources/emba_ecart_production_2026-11-22.json
Pour actualiser l’écart de production, ajouter les deux bornes et l’URL du nouveau RPM
dans un nouvel instantané daté emba_ecart_production_AAAA-MM-JJ.json dans Resources.
"""

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
import requests
from matplotlib.ticker import MaxNLocator, MultipleLocator

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "plot-common"))
from teaching_plot_utils import COLORS, MONTH_FR, get_valet_series, new_figure, recessions_ca, style_axes

# Statistique Canada : ensemble, Canada. Les deux indices sont non désaisonnalisés.
CPI = 41690973         # 18-10-0004-01 : IPC global (2002=100).
MEDIAN = 108785714     # 18-10-0256-01 : IPC-méd, variation sur 12 mois déjà publiée.
IPPI = 1230995983      # 18-10-0265-01 : IPPI total (janvier 2020=100).
# 18-10-0268-01 : indices mensuels des prix des matières brutes, Canada.
RAW_ENERGY = 1230998136
RAW_EX_ENERGY = 1230998148
# 14-10-0287-01 : Canada, 15 ans et plus, tous genres, taux désaisonnalisés.
PARTICIPATION = 2062816
EMPLOYMENT = 2062817
UNEMPLOYMENT = 2062815
# Tableau 14-10-0355-01, regroupements de canada_employment_exports (MBA, séance 1).
HIGH_EXPORT = (2057609, 2057605, 2057606)  # Fabrication, agriculture, ressources naturelles.
LOW_EXPORT = (2057617, 2057616, 2057621, 2057608, 2057619, 1643071246)
# Santé et aide sociale, enseignement, administration publique, construction,
# hébergement et restauration, commerce de détail.
ALL_INDUSTRIES = 2057603
# PIB réel en dollars enchaînés de 2017, tableaux 36-10-0104-01 et 36-10-0706-01.
REAL_GDP = 62305752
REAL_GDP_PER_CAPITA = 1645315579
# Contributions annualisées à la croissance trimestrielle du PIB réel, tableau 36-10-0104-01.
HOUSEHOLD_CONSUMPTION = 79448555
NONPROFIT_CONSUMPTION = 79448561
PUBLIC_CONSUMPTION = 79448562
FIXED_INVESTMENT = 79448563
INVENTORIES = 79448572
EXPORTS = 79448573
IMPORTS = 79448576
DISCREPANCY = 79448579
GDP_GROWTH = 79448580
# Exportations mensuelles, balance des paiements, données désaisonnalisées.
# 12-10-0163-01 : millions de dollars courants. Le groupe SCPAN 324 comprend
# l’or, l’argent et les métaux du groupe du platine sous forme brute, et leurs alliages.
GOODS_EXPORT_VALUE = 1566911338
PRECIOUS_METALS_EXPORT_VALUE = 1566911383
# 12-10-0168-01 : indices de prix de Paasche correspondants (2017 = 100).
GOODS_EXPORT_PRICE = 1566915936
PRECIOUS_METALS_EXPORT_PRICE = 1566915981
# Statistique Canada, Canada entier : 17-10-0059-01 et 17-10-0040-01.
BIRTHS, DEATHS = 62, 77
IMMIGRANTS, NET_EMIGRATION, NET_NONPERMANENT = 29850342, 1566834788, 29850346
WDS = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorByReferencePeriodRange"
EMBA_GOLD = "#D1BA22"  # EMBA/gabarit_emba.tex
# Noir, or foncé pour les traits sur fond blanc, puis bleu et rouge du logo EMBA.
EMBA_LINE_COLORS = ("#171717", "#967209", "#1C72AD", "#D8342B")


def statcan_data(vectors, start, snapshot, frequency="MS"):
    if snapshot:
        payload = json.loads(snapshot.read_text(encoding="utf-8"))
    else:
        response = requests.get(WDS, params={
            "vectorIds": ",".join(map(str, vectors)), "startRefPeriod": start,
            "endReferencePeriod": date.today().isoformat(),
        }, timeout=40)
        response.raise_for_status()
        payload = response.json()

    series_by_vector = {}
    for item in payload:
        if item["status"] != "SUCCESS":
            raise ValueError(f"Réponse de Statistique Canada : {item['status']}")
        series = item["object"]
        vector = series["vectorId"]
        points = pd.DataFrame(series["vectorDataPoint"])
        values = points.set_index(pd.to_datetime(points["refPer"]))["value"]
        series_by_vector[vector] = values.sort_index().asfreq(frequency)
    return pd.DataFrame(series_by_vector)[list(vectors)]


def common_history(data):
    last_common = min(data[col].last_valid_index() for col in data)
    data = data.loc["2019-01-01":last_common]
    if data.empty or data.isna().any().any():
        raise ValueError("Historique mensuel commun incomplet.")
    return data


def inflation(snapshot):
    data = statcan_data((CPI, MEDIAN, IPPI), "2018-01-01", snapshot)
    for vector in (CPI, IPPI):
        data[vector] = 100 * (data[vector] / data[vector].shift(12) - 1)
    return common_history(data)


def style_time_axis(ax, start, end, step):
    style_axes(ax)
    ax.set_prop_cycle(color=EMBA_LINE_COLORS)
    ax.grid(axis="y", linestyle="-", color="#DEDEDE", linewidth=.55)
    ax.set_axisbelow(True)
    ax.spines[["left", "bottom"]].set_color("#B6B6B6")
    ax.tick_params(axis="both", length=0, labelsize=13, pad=5)
    ax.yaxis.set_major_locator(MultipleLocator(step))
    # Les graduations en mode texte emploient le Fira Sans des diapositives.
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}".replace("-", r"\textminus{}"))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y", usetex=False))
    ax.set_xlim(start, end)
    for begin, stop in recessions_ca:
        if begin < end and stop > start:
            ax.axvspan(begin, stop, facecolor="#D4D4D4", linewidth=0, zorder=0)


def latest_value(fig, name, value, ink, y, unit=r"\,\%"):
    fig.add_artist(plt.Line2D([.737, .777], [y, y], transform=fig.transFigure,
                              color=ink, linewidth=2.5))
    fig.text(.786, y, name, fontsize=12.6, va="center")
    value = f"{value:.1f}".replace(".", ",")
    fig.text(.786, y-.075, rf"\textbf{{{value}{unit}}}", fontsize=18, va="center")


def plot_inflation_pair(data, other, label, step, filename, title):
    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.052, right=.695, bottom=.17, top=.88)
    start, end = data.index[0], data.index[-1]
    style_time_axis(ax, start, end, step)
    pair = data[[CPI, other]]
    low = math.floor(min(0, pair.min().min()) / step) * step
    high = math.ceil(max(3, pair.max().max()) / step) * step
    ax.set_ylim(low, high)
    ax.set_title(r"Variation sur 12 mois (\%)", loc="left", fontsize=14, pad=8)
    fig.text(.737, .89, rf"\textbf{{{MONTH_FR[end.month].capitalize()} {end.year}}}",
             fontsize=14, va="center")
    target_ink = "#B9A649"
    ax.axhspan(1, 3, color=EMBA_GOLD, alpha=.17, linewidth=0, zorder=0)
    ax.axhline(2, color=target_ink, linewidth=1.2, zorder=1)
    # Même code visuel pour chaque courbe et sa dernière observation.
    for vector, name, y in [(CPI, "IPC global", .75), (other, label, .52)]:
        line, = ax.plot(data.index, data[vector], linewidth=2.5, zorder=3)
        latest_value(fig, name, data[vector].iloc[-1], line.get_color(), y)
    fig.text(.737, .25, r"\textbf{Cible de la Banque du Canada}", fontsize=12.5)
    fig.add_artist(Rectangle((.737, .176), .04, .045, transform=fig.transFigure,
                             facecolor=EMBA_GOLD, alpha=.17, edgecolor="none"))
    fig.add_artist(plt.Line2D([.737, .777], [.199, .199], transform=fig.transFigure,
                              color=target_ink, linewidth=1.2))
    fig.text(.786, .199, r"2\,\% pour l’IPC global", fontsize=12, va="center")
    fig.text(.786, .128, r"Fourchette de 1 à 3\,\%", fontsize=11.5)
    fig.text(.052, .025, "Sources — Statistique Canada, Banque du Canada et Institut C.D. Howe",
             fontsize=10.7, color="#535353")
    fig.savefig(HERE / filename, transparent=True,
                metadata={"Title": title,
                          "Subject": f"Statistique Canada, vecteurs {CPI}, {other}. "
                                     f"Dernier mois commun : {end:%Y-%m}."})
    plt.close(fig)


def plot_inflation(data):
    plot_inflation_pair(data, MEDIAN, "IPC fondamental (médiane)", 2,
                        "inflation_canada.pdf", "Inflation globale et inflation fondamentale au Canada")
    plot_inflation_pair(data, IPPI, "Prix industriels (IPPI)", 5,
                        "inflation_production_canada.pdf", "Prix à la production et à la consommation au Canada")
    print(data.tail(1).round(1).to_string())


def plot_labour(snapshot):
    data = common_history(statcan_data((PARTICIPATION, EMPLOYMENT, UNEMPLOYMENT),
                                       "2019-01-01", snapshot))
    start, end = data.index[0], data.index[-1]
    fig, population = new_figure(10, 4.85)
    fig.subplots_adjust(left=.052, right=.665, bottom=.17, top=.88)
    style_time_axis(population, start, end, 5)
    rates = data[[EMPLOYMENT, PARTICIPATION]]
    population.set_ylim(5 * math.floor(rates.min().min() / 5),
                        5 * math.ceil(rates.max().max() / 5))
    population.set_title(r"Emploi et activité (\% des 15 ans et plus)", loc="left",
                         fontsize=12, pad=7)

    _, gold, blue, red = EMBA_LINE_COLORS
    labour_force = population.twinx()
    # Sur l’axe de droite, la plage 0–30 % sépare visuellement les trois courbes.
    labour_force.set_ylim(0, max(30, 5 * math.ceil(data[UNEMPLOYMENT].max() / 5)))
    labour_force.yaxis.set_major_locator(MultipleLocator(5))
    labour_force.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}")
    labour_force.tick_params(axis="y", length=3, labelsize=13, pad=4, colors=gold)
    labour_force.spines[["top", "bottom", "left"]].set_visible(False)
    labour_force.spines["right"].set_color(gold)
    labour_force.grid(False)
    labour_force.set_title(r"Chômage (\% de la population active)", loc="right",
                           fontsize=12, pad=7, color=gold)
    fig.text(.737, .89, rf"\textbf{{{MONTH_FR[end.month].capitalize()} {end.year}}}",
             fontsize=14, va="center")
    for ax, vector, label, ink, y in [
            (population, EMPLOYMENT, "Taux d’emploi", red, .74),
            (population, PARTICIPATION, "Taux d’activité", blue, .53),
            (labour_force, UNEMPLOYMENT, "Taux de chômage", gold, .29)]:
        ax.plot(data.index, data[vector], color=ink, linewidth=2.5, zorder=3)
        latest_value(fig, label, data[vector].iloc[-1], ink, y)

    fig.text(.052, .025, "Sources — Statistique Canada, Enquête sur la population active "
             "(données désaisonnalisées) et Institut C.D. Howe", fontsize=10.7, color="#535353")
    fig.savefig(HERE / "marche_travail_canada.pdf", transparent=True,
                metadata={"Title": "Le marché du travail au Canada",
                          "Subject": f"Statistique Canada, tableau 14-10-0287-01. Dernier mois : {end:%Y-%m}."})
    plt.close(fig)
    print(data.tail(1).to_string())


def plot_tariff_employment(snapshot):
    base_month = pd.Timestamp("2023-01-01")
    vectors = (*HIGH_EXPORT, *LOW_EXPORT, ALL_INDUSTRIES)
    data = common_history(statcan_data(vectors, "2023-01-01", snapshot)).loc[base_month:]
    levels = pd.DataFrame({
        "Secteurs plus exposés": data[list(HIGH_EXPORT)].sum(axis=1, min_count=len(HIGH_EXPORT)),
        "Secteurs moins exposés": data[list(LOW_EXPORT)].sum(axis=1, min_count=len(LOW_EXPORT)),
        "Tous les secteurs": data[ALL_INDUSTRIES],
    })
    indices = 100 * levels / levels.loc[base_month]
    end = indices.index[-1]

    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.052, right=.982, bottom=.17, top=.88)
    style_time_axis(ax, base_month, end, 2)
    ax.set_ylim(2 * math.floor(indices.min().min() / 2), 2 * math.ceil(indices.max().max() / 2))
    ticks = pd.date_range(base_month, end, freq="6MS")
    ax.set_xticks(ticks, [f"{MONTH_FR[d.month]} {d:%y}" for d in ticks], fontsize=11)
    ax.set_title("Indice de l’emploi (janvier 2023 = 100)", loc="left", fontsize=14, pad=8)
    _, gold, blue, red = EMBA_LINE_COLORS
    for (name, series), ink in zip(indices.items(), (red, blue, gold)):
        ax.plot(series.index, series, label=name, color=ink, linewidth=2.5, zorder=3)
    ax.legend(loc="upper left", fontsize=13, frameon=False)

    fig.text(.052, .025, "Source — Statistique Canada, Enquête sur la population active "
             "(données désaisonnalisées), tableau 14-10-0355-01.", fontsize=10.7, color="#535353")
    fig.savefig(HERE / "emploi_exposition_douane.pdf", transparent=True,
                metadata={"Title": "L’emploi selon l’exposition aux droits de douane américains",
                          "Subject": f"Tableau 14-10-0355-01. Janvier 2023 = 100. Dernier mois : {end:%Y-%m}."})
    plt.close(fig)
    print(indices.tail(1).round(1).to_string())


def plot_gdp_levels(data):
    levels = data[[REAL_GDP, REAL_GDP_PER_CAPITA]]
    indices = 100 * levels / levels.loc["2019-10-01"]
    end = indices.index[-1]
    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.052, right=.982, bottom=.17, top=.88)
    style_time_axis(ax, indices.index[0], end, 5)
    ax.set_ylim(5 * math.floor(indices.min().min() / 5), 5 * math.ceil(indices.max().max() / 5))
    ax.set_title("Indice trimestriel (T4 2019 = 100)", loc="left", fontsize=14, pad=8)
    for vector, name in [(REAL_GDP, "PIB réel"), (REAL_GDP_PER_CAPITA, "PIB réel par habitant")]:
        ax.plot(indices.index, indices[vector], label=name, linewidth=2.5, zorder=3)
    ax.legend(loc="lower right", ncol=2, fontsize=13, frameon=False)
    fig.text(.052, .025, "Sources — Statistique Canada, tableaux 36-10-0104-01 et 36-10-0706-01, et Institut C.D. Howe.",
             fontsize=10.7, color="#535353")
    fig.savefig(HERE / "pib_reel_par_habitant.pdf", transparent=True,
                metadata={"Title": "PIB réel et PIB réel par habitant au Canada"})
    plt.close(fig)


def plot_gdp_waterfall(quarter):
    # Dans le tableau source, les importations sont publiées avant soustraction.
    effects = pd.Series({
        "Consommation\nprivée": quarter[HOUSEHOLD_CONSUMPTION] + quarter[NONPROFIT_CONSUMPTION],
        "Consommation\npublique": quarter[PUBLIC_CONSUMPTION],
        "Investissement\nfixe": quarter[FIXED_INVESTMENT],
        "Variation\ndes stocks": quarter[INVENTORIES],
        "Exportations": quarter[EXPORTS],
        "Importations": -quarter[IMPORTS],
    })
    growth = quarter[GDP_GROWTH]
    # Les huit contributions sources et le total sont arrondis au millième de point.
    if not math.isclose(effects.sum() + quarter[DISCREPANCY], growth, abs_tol=.0045):
        raise ValueError("La somme des contributions diffère de la croissance publiée.")

    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.067, right=.993, bottom=.23, top=.88)
    style_axes(ax)
    ax.spines[["left", "bottom"]].set_visible(False)
    ax.tick_params(axis="both", length=0, pad=6, labelsize=12)
    ax.set_axisbelow(True)
    ax.grid(axis="y", linestyle="-", color="#DEDEDE", linewidth=.55)
    ax.axhline(0, color="#777777", linewidth=.9)
    date = quarter.name
    ax.set_title(rf"\textbf{{T{date.quarter} {date.year}}} — Contributions à la croissance annualisée (points de pourcentage)",
                 loc="left", fontsize=13.3, pad=10)

    cumulative = effects.cumsum()
    lo, hi = min(0, cumulative.min(), growth), max(0, cumulative.max(), growth)
    padding = .1 * max(hi - lo, .1)
    ticks = MaxNLocator(nbins=6, steps=[1, 2, 2.5, 5, 10]).tick_values(
        lo - padding if lo < 0 else 0, hi + padding if hi > 0 else padding)
    ax.set_yticks(ticks)
    ax.set_ylim(ticks[0], ticks[-1])
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", r"\textminus{}"))

    red = EMBA_LINE_COLORS[3]
    width = .64
    start = 0
    for i, (effect, end) in enumerate(zip(effects, cumulative)):
        ax.bar(i, effect, bottom=start, width=width, color=COLORS["green"] if effect >= 0 else red, zorder=3)
        if i < len(effects) - 1:
            ax.hlines(end, i + width / 2, i + 1 - width / 2, color="#929292", linewidth=.8)
        label = f"{effect:+.2f}".replace(".", ",").replace("-", r"\textminus{}")
        ax.annotate(label, (i, end), xytext=(0, 4 if effect >= 0 else -5),
                    textcoords="offset points", ha="center", va="bottom" if effect >= 0 else "top",
                    fontsize=12.5)
        start = end

    last = len(effects)
    ax.bar(last, growth, width=width, color=EMBA_GOLD, zorder=3)
    total = f"{growth:+.2f}".replace(".", ",").replace("-", r"\textminus{}")
    ax.annotate(rf"\textbf{{{total}\,\%}}", (last, growth), xytext=(0, 5 if growth >= 0 else -5),
                textcoords="offset points", ha="center", va="bottom" if growth >= 0 else "top", fontsize=13.5)
    ax.set_xticks(range(last + 1), [*effects.index, "PIB réel"], fontsize=11)
    ax.set_xlim(-.55, last + .55)
    fig.text(.067, .025, "Source — Statistique Canada, tableau 36-10-0104-01. Données trimestrielles désaisonnalisées.",
             fontsize=10.7, color="#535353")
    fig.savefig(HERE / "contributions_pib_reel.pdf", transparent=True,
                metadata={"Title": "Contributions des dépenses à la croissance annualisée du PIB réel canadien"})
    plt.close(fig)


def plot_gdp(snapshot):
    vectors = (REAL_GDP, REAL_GDP_PER_CAPITA, HOUSEHOLD_CONSUMPTION, NONPROFIT_CONSUMPTION,
               PUBLIC_CONSUMPTION, FIXED_INVESTMENT, INVENTORIES, EXPORTS, IMPORTS, DISCREPANCY, GDP_GROWTH)
    data = statcan_data(vectors, "2019-01-01", snapshot, frequency="QS")
    if data.empty or data.isna().any().any():
        raise ValueError("Données trimestrielles du PIB incomplètes.")
    plot_gdp_levels(data)
    plot_gdp_waterfall(data.iloc[-1])


def plot_goods_exports(snapshot):
    base = pd.Timestamp("2024-09-01")
    vectors = (GOODS_EXPORT_VALUE, PRECIOUS_METALS_EXPORT_VALUE,
               GOODS_EXPORT_PRICE, PRECIOUS_METALS_EXPORT_PRICE)
    data = common_history(statcan_data(vectors, "2024-09-01", snapshot)).loc[base:]
    if base not in data.index or (data <= 0).any().any():
        raise ValueError("Base de septembre 2024 absente ou données d’exportation non positives.")
    # À prix fixes de 2017, les volumes sont additifs. Déflater chaque valeur
    # par son propre indice de Paasche avant de soustraire le groupe 324.
    total = 100 * data[GOODS_EXPORT_VALUE] / data[GOODS_EXPORT_PRICE]
    metals = 100 * data[PRECIOUS_METALS_EXPORT_VALUE] / data[PRECIOUS_METALS_EXPORT_PRICE]
    levels = pd.DataFrame({"Total des biens": total, "Biens hors or*": total - metals})
    indices = 100 * levels / levels.loc[base]
    end = indices.index[-1]

    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.052, right=.959, bottom=.21, top=.88)
    style_time_axis(ax, base, end, 5)
    ax.set_ylim(5 * math.floor(indices.min().min() / 5), 5 * math.ceil(indices.max().max() / 5))
    ticks = pd.date_range(base, end, freq="4MS")
    ax.set_xticks(ticks, [f"{MONTH_FR[d.month]} {d:%y}" for d in ticks], fontsize=11)
    ax.set_title("Volume des exportations (septembre 2024 = 100)", loc="left", fontsize=14, pad=8)
    for name, series in indices.items():
        ax.plot(series.index, series, label=name, linewidth=2.5, zorder=3)
    ax.legend(loc="upper right", ncol=2, fontsize=13, frameon=False)
    fig.text(.052, .070, "* Le poste exclu regroupe l’or, l’argent et les métaux du groupe du platine "
             "sous forme brute, ainsi que leurs alliages.", fontsize=10.7, color="#535353")
    fig.text(.052, .025, "Source — Statistique Canada, tableaux 12-10-0163-01 et 12-10-0168-01. "
             "Données mensuelles désaisonnalisées.", fontsize=10.7, color="#535353")
    fig.savefig(HERE / "exportations_biens_canada.pdf", transparent=True,
                metadata={"Title": "Exportations canadiennes de biens, totales et hors or",
                          "Subject": f"Volumes aux prix de 2017, base septembre 2024. Dernier mois : {end:%Y-%m}."})
    plt.close(fig)
    print(indices.iloc[[0, -1]].round(1).to_string())


def valet_data(series, start, snapshot):
    if snapshot:
        observations = pd.json_normalize(json.loads(snapshot.read_text(encoding="utf-8"))["observations"])
        data = observations.set_index(pd.to_datetime(observations["d"]))[[s + ".v" for s in series]]
        data.columns = series
        return data.astype(float).sort_index().loc[start:]
    return pd.DataFrame({s: get_valet_series(s, start=start) for s in series})


def plot_interest_rates(snapshot):
    policy = "V39079"
    bond = "BD.CDN.10YR.DQ.YLD"
    start = pd.Timestamp("2019-01-01")
    decision = pd.Timestamp("2027-01-27")
    session = pd.Timestamp("2027-01-28")
    rates = valet_data((policy, bond), "2019-01-01", snapshot)
    rates = rates.sort_index().loc[start:session]
    if rates.index.has_duplicates or rates.count().min() < 2:
        raise ValueError("Historique quotidien des taux incomplet ou dates en double.")
    # Les obligations ne sont pas cotées les jours de fermeture du marché.
    policy_rate = rates[policy].dropna()
    bond_yield = rates[bond].dropna()
    end = rates.dropna().index[-1]

    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.052, right=.975, bottom=.17, top=.89)
    style_time_axis(ax, start, decision + pd.Timedelta(days=45), 1)
    ax.set_ylim(min(0, math.floor(rates.min().min())), math.floor(rates.max().max()) + 1)
    ax.set_title(r"Taux d’intérêt (\%)", loc="left", fontsize=14, pad=8)
    ax.step(policy_rate.index, policy_rate, where="post", label="Taux directeur",
            color=EMBA_LINE_COLORS[0], linewidth=2.4, zorder=3)
    ax.plot(bond_yield.index, bond_yield, label="Obligation du Canada à 10 ans",
            color=EMBA_LINE_COLORS[1], linewidth=1.6, zorder=2)
    ax.legend(loc="upper left", fontsize=12.5, frameon=False)

    # Le repère indique la date de l'annonce, même avant qu'un résultat soit connu.
    ax.axvline(decision, ymin=0, ymax=.94, color="#898989", linewidth=.8, zorder=1)
    ax.annotate("Annonce de la Banque du Canada\n27 janvier 2027", (decision, .94),
                xycoords=("data", "axes fraction"), xytext=(-5, 1), textcoords="offset points",
                ha="right", va="top", fontsize=11.5, color="#444444")
    fig.text(.052, .025, f"Sources — Banque du Canada et Institut C.D. Howe. "
             f"Données quotidiennes disponibles pour les deux séries au {end.day} {MONTH_FR[end.month]} {end.year}.",
             fontsize=10.7, color="#535353")
    fig.savefig(HERE / "taux_directeur_et_10_ans.pdf", transparent=True,
                metadata={"Title": "Taux directeur et rendement de l’obligation du Canada à 10 ans",
                          "Subject": f"Banque du Canada, Valet : {policy}, {bond}. Dernière date commune : {end:%Y-%m-%d}."})
    plt.close(fig)
    print(rates.loc[end].to_string())


def save_data_figure(fig, filename, title, source):
    fig.text(.058, .025, source, fontsize=10.7, color="#535353")
    fig.savefig(HERE / filename, transparent=True, metadata={"Title": title, "Subject": source})
    plt.close(fig)


def plot_raw_material_prices(snapshot):
    levels = common_history(statcan_data((RAW_ENERGY, RAW_EX_ENERGY), "2022-01-01", snapshot))
    growth = levels.pct_change(12, fill_method=None).mul(100).loc["2023-01":]
    if growth.empty or growth.isna().any().any():
        raise ValueError("Historique insuffisant pour les variations sur douze mois de l’IPMB.")
    start, end = growth.index[0], growth.index[-1]
    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.065, right=.865, bottom=.17, top=.86)
    step = 20
    style_time_axis(ax, start, end, step)
    ax.set_ylim(step * math.floor(min(0, growth.min().min()) / step),
                step * math.ceil(max(0, growth.max().max()) / step))
    ax.set_title(r"Variation sur 12 mois (\%)", loc="left", fontsize=14, pad=8)
    ticks = pd.date_range(start, end, freq="6MS")
    ax.set_xticks(ticks, [f"{MONTH_FR[d.month]} {d:%y}" for d in ticks], fontsize=11)
    ax.axhline(0, color="#888888", linewidth=.9)
    for vector, label in [(RAW_ENERGY, "Produits énergétiques bruts"),
                          (RAW_EX_ENERGY, "Autres matières brutes")]:
        series = growth[vector]
        line, = ax.plot(series.index, series, label=label, linewidth=2.5)
        value = f"{series.iloc[-1]:+.1f}".replace(".", ",").replace("-", r"\textminus{}")
        ax.annotate(rf"\textbf{{{value}\,\%}}", (end, series.iloc[-1]), xytext=(6, 0),
                    textcoords="offset points", va="center", color=line.get_color(), fontsize=13)
    ax.legend(loc="upper left", fontsize=12.7, frameon=False)
    ax.annotate(f"{MONTH_FR[end.month]} {end.year}", (1, 1), xycoords="axes fraction",
                xytext=(4, 10), textcoords="offset points", ha="left", fontsize=11.5)
    save_data_figure(fig, "prix_matieres_brutes.pdf", "Prix des matières brutes au Canada",
                     "Source — Statistique Canada, Indice des prix des matières brutes, tableau 18-10-0268-01.")


def plot_business_intentions(snapshot):
    history = valet_data(("EMPLOY", "INVESTMACHEQUIP"), "1998-07-01", snapshot).asfreq("QS")
    if history.empty or history.isna().any().any() or history.abs().max().max() > 100:
        raise ValueError("Soldes d’opinion manquants ou en dehors de l’intervalle de −100 à 100.")
    data = history.loc["2019":]
    end = data.index[-1]
    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.058, right=.975, bottom=.20, top=.89)
    style_time_axis(ax, data.index[0], end, 20)
    ax.set_ylim(20 * math.floor(min(0, data.min().min()) / 20),
                20 * math.ceil(max(0, data.max().max()) / 20))
    ax.axhline(0, color="#777777", linewidth=.9)
    ax.set_title("Solde des opinions pour les 12 prochains mois (points de pourcentage)",
                 loc="left", fontsize=13.6, pad=8)
    for column, label in [("EMPLOY", "Embauche"), ("INVESTMACHEQUIP", "Investissement en machines et matériel")]:
        ax.plot(data.index, data[column], label=label, linewidth=2.4)
    ax.legend(loc="upper right", fontsize=12.2, frameon=False)
    latest, average = data.iloc[-1], history.mean()
    fig.text(.058, .075, rf"\textbf{{T{end.quarter} {end.year}}}\quad Embauche {latest['EMPLOY']:+.0f} "
             rf"(moyenne {average['EMPLOY']:+.0f})\qquad Investissement {latest['INVESTMACHEQUIP']:+.0f} "
             f"(moyenne {average['INVESTMACHEQUIP']:+.0f})", fontsize=12)
    save_data_figure(fig, "intentions_entreprises.pdf", "Intentions d’embauche et d’investissement",
                          "Sources — Banque du Canada, Enquête sur les perspectives des entreprises "
                          "(moyennes depuis 1998), et Institut C.D. Howe.")


def plot_population_growth(snapshot):
    vectors = (BIRTHS, DEATHS, IMMIGRANTS, NET_EMIGRATION, NET_NONPERMANENT)
    flows = statcan_data(vectors, "2021-07-01", snapshot, frequency="QS").loc["2021-07-01":]
    if len(flows) < 4 or flows.isna().any().any():
        raise ValueError("Composantes trimestrielles de la population incomplètes.")
    components = pd.DataFrame({
        "Accroissement naturel": flows[BIRTHS] - flows[DEATHS],
        "Migration internationale nette": flows[IMMIGRANTS] - flows[NET_EMIGRATION] + flows[NET_NONPERMANENT],
    })
    # Années non chevauchantes se terminant au dernier trimestre publié.
    annual = components.rolling(4).sum().dropna() / 1000
    end = annual.index[-1]
    annual = annual.loc[annual.index.quarter == end.quarter]
    natural, migration = (annual[col] for col in annual)
    years = annual.index.year
    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.072, right=.975, bottom=.16, top=.89)
    style_axes(ax)
    ax.set_axisbelow(True)
    ax.grid(axis="y", linestyle="-", color="#DEDEDE", linewidth=.55)
    ax.tick_params(axis="both", length=0, labelsize=13, pad=5)
    ax.set_title(f"Variation sur 12 mois se terminant en {['mars', 'juin', 'septembre', 'décembre'][end.quarter - 1]} "
                 "(milliers de personnes)", loc="left", fontsize=13.6, pad=8)
    ax.bar(years, natural, width=.52, label=natural.name, color=EMBA_LINE_COLORS[0])
    bottom = natural.where(natural * migration > 0, 0)
    ax.bar(years, migration, bottom=bottom, width=.52, label=migration.name, color=EMBA_LINE_COLORS[1])
    tallest = annual.clip(lower=0).sum(axis=1)
    lowest = annual.clip(upper=0).sum(axis=1)
    step = 250
    ax.set_ylim(step * math.floor(lowest.min() / step), step * math.ceil((tallest.max() + 65) / step))
    ax.yaxis.set_major_locator(MultipleLocator(step))
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:,.0f}".replace(",", r"\,"))
    ax.axhline(0, color="#777777", linewidth=.9)
    ax.set_xticks(years, [str(y) for y in years])
    for year, total, top in zip(years, natural + migration, tallest):
        label = f"{total:,.0f}".replace(",", r"\,")
        ax.annotate(label, (year, top), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=12.5)
    ax.legend(loc="upper right", fontsize=12, frameon=False)
    save_data_figure(fig, "croissance_demographique.pdf", "Les sources de la croissance démographique canadienne",
                          "Source — Statistique Canada, tableaux 17-10-0059-01 et 17-10-0040-01. "
                          "Le chiffre au-dessus de chaque barre indique le total.")


def plot_output_gap_range(snapshot):
    if snapshot is None:
        snapshot = max((HERE.parent / "Resources").glob("emba_ecart_production_*.json"), default=None)
        if snapshot is None:
            raise FileNotFoundError("Fournir avec --snapshot les fourchettes publiées dans les RPM.")
    data = pd.read_json(snapshot)
    data.index = pd.PeriodIndex(data["quarter"], freq="Q")
    data = data.sort_index()
    if (data.empty or not data.index.equals(pd.period_range(data.index[0], data.index[-1], freq="Q"))
            or data[["lower", "upper"]].isna().any().any() or (data.lower >= data.upper).any()):
        raise ValueError("Fourchettes de l’écart de production incomplètes ou incohérentes.")
    def valeur_fr(value):
        return f"{value:g}".replace(".", ",").replace("-", r"\textminus{}")

    end = data.index[-1]
    dates = data.index.to_timestamp()
    lower, upper = data["lower"].to_numpy(), data["upper"].to_numpy()
    midpoint = (lower + upper) / 2
    ink, gold = EMBA_LINE_COLORS[:2]
    fig, ax = new_figure(10, 4.85)
    fig.subplots_adjust(left=.065, right=.865, bottom=.17, top=.77)
    style_time_axis(ax, dates[0], dates[-1], .5)
    ax.set_ylim(math.floor(min(0, lower.min()) * 2) / 2,
                math.ceil(max(0, upper.max()) * 2) / 2)
    ax.yaxis.set_major_formatter(lambda v, _: valeur_fr(v))
    ax.spines["left"].set_visible(False)
    fig.text(.065, .938, r"Écart de production, en \% du PIB potentiel", fontsize=15)

    band = ax.fill_between(dates, lower, upper, color=EMBA_GOLD, alpha=.38, linewidth=0,
                           label="Fourchette estimée par la Banque du Canada", zorder=2)
    ax.axhline(0, color="#858585", linewidth=1, zorder=3)
    line, = ax.plot(dates, midpoint, color=ink, linewidth=2.2, marker="o", markersize=4,
                    label="Milieu de la fourchette", clip_on=False, zorder=4)
    fig.legend(handles=[band, line], loc="center left", bbox_to_anchor=(.065, .863),
               ncol=2, frameon=False, fontsize=12.8, borderaxespad=0, borderpad=0,
               handlelength=2.3, handletextpad=.6, columnspacing=1.7)
    ax.annotate("PIB au potentiel", (.58, 0), xycoords=("axes fraction", "data"),
                xytext=(0, 4), textcoords="offset points", ha="left", color="#565656", fontsize=12)

    first_quarters = data.index.quarter == 1
    ax.set_xticks(dates[first_quarters], [str(year) for year in data.index.year[first_quarters]])
    ax.set_xticks(dates, minor=True)
    ax.tick_params(axis="x", which="minor", length=3, color="#B6B6B6")

    ax.annotate(rf"\textbf{{T{end.quarter} {end.year}}}", (dates[-1], upper[-1]),
                xytext=(8, 15), textcoords="offset points", fontsize=12, color=ink)
    for bound in (lower[-1], upper[-1]):
        ax.annotate(rf"{valeur_fr(bound)}\,\%", (dates[-1], bound), xytext=(8, 0),
                    textcoords="offset points", va="center", color=gold, fontsize=12)
    ax.annotate(rf"\textbf{{{valeur_fr(midpoint[-1])}\,\%}}", (dates[-1], midpoint[-1]),
                xytext=(8, 0), textcoords="offset points", va="center", color=ink, fontsize=13)
    save_data_figure(fig, "ecart_production_canada.pdf", "Écart de production au Canada",
                          "Source — Banque du Canada, Rapport sur la politique monétaire. Estimations publiées à chaque trimestre.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure", choices=("inflation", "travail", "douane", "pib", "exportations", "taux",
                                             "intentions", "demographie", "ecart", "intrants"), default="inflation")
    parser.add_argument("--snapshot", type=Path, help="Données JSON archivées de Statistique Canada ou de la Banque du Canada.")
    args = parser.parse_args()
    if args.figure == "travail":
        plot_labour(args.snapshot)
    elif args.figure == "douane":
        plot_tariff_employment(args.snapshot)
    elif args.figure == "intrants":
        plot_raw_material_prices(args.snapshot)
    elif args.figure == "pib":
        plot_gdp(args.snapshot)
    elif args.figure == "exportations":
        plot_goods_exports(args.snapshot)
    elif args.figure == "taux":
        plot_interest_rates(args.snapshot)
    elif args.figure == "intentions":
        plot_business_intentions(args.snapshot)
    elif args.figure == "demographie":
        plot_population_growth(args.snapshot)
    elif args.figure == "ecart":
        plot_output_gap_range(args.snapshot)
    else:
        plot_inflation(inflation(args.snapshot))
