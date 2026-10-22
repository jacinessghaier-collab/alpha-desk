from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import numpy as np


PORTFOLIO_DATA: dict[str, dict[str, Any]] = {
    "BHP Group (BHP)": {"symbol": "BHP", "wkn": "850524", "paar": "Paar 1: Minen & Energie", "typ": "Kernaktie", "kurs_eur": 28.50, "div_yield": 5.8, "kgv": 11.2, "monate": "März, Sep", "rot_monat": "Monat 1 (Nov, Mrz, Jul)", "gewicht": 10.0, "risiko": "Zyklisch", "sentiment": "Bullish", "infl_faktor": 1.25},
    "Woodside Energy (WDS)": {"symbol": "WDS", "wkn": "A3DNGW", "paar": "Paar 1: Minen & Energie", "typ": "Kernaktie", "kurs_eur": 18.20, "div_yield": 6.8, "kgv": 9.5, "monate": "März, Sep", "rot_monat": "Monat 2 (Dez, Apr, Aug)", "gewicht": 8.5, "risiko": "Zyklisch", "sentiment": "Neutral", "infl_faktor": 1.30},
    "Rio Tinto (RIO)": {"symbol": "RIO", "wkn": "852147", "paar": "Paar 2: Rohstoff vs. Auto", "typ": "Kernaktie", "kurs_eur": 58.00, "div_yield": 6.2, "kgv": 10.8, "monate": "April, Sep", "rot_monat": "Monat 3 (Jan, Mai, Sep)", "gewicht": 11.0, "risiko": "Zyklisch", "sentiment": "Bullish", "infl_faktor": 1.22},
    "Mercedes-Benz (MBG)": {"symbol": "MBG.DE", "wkn": "710000", "paar": "Paar 2: Rohstoff vs. Auto", "typ": "Kernaktie", "kurs_eur": 62.40, "div_yield": 7.8, "kgv": 7.2, "monate": "Mai", "rot_monat": "Monat 1 (Nov, Mrz, Jul)", "gewicht": 12.0, "risiko": "Zyklisch", "sentiment": "Neutral", "infl_faktor": 0.85},
    "HSBC Holdings (HSBA)": {"symbol": "HSBC", "wkn": "923893", "paar": "Paar 3: Finanzen & Zinsen", "typ": "Kernaktie", "kurs_eur": 8.10, "div_yield": 4.4, "kgv": 8.0, "monate": "Apr, Jun, Sep, Dez", "rot_monat": "Monat 4 (Feb, Jun, Okt)", "gewicht": 9.0, "risiko": "Defensiv", "sentiment": "Bullish", "infl_faktor": 1.10},
    "Legal & General (LGEN)": {"symbol": "LGEN.L", "wkn": "851584", "paar": "Paar 3: Finanzen & Zinsen", "typ": "Kernaktie", "kurs_eur": 2.90, "div_yield": 7.7, "kgv": 10.1, "monate": "Jun, Sep", "rot_monat": "Monat 3 (Jan, Mai, Sep)", "gewicht": 8.0, "risiko": "Defensiv", "sentiment": "Neutral", "infl_faktor": 1.05},
    "Imperial Brands (IMB)": {"symbol": "IMB.L", "wkn": "903000", "paar": "Paar 4: Krisenfester Konsum", "typ": "Kernaktie", "kurs_eur": 24.50, "div_yield": 6.3, "kgv": 9.8, "monate": "Mrz, Jun, Sep, Dez", "rot_monat": "Monat 2 (Dez, Apr, Aug)", "gewicht": 9.5, "risiko": "Defensiv", "sentiment": "Bullish", "infl_faktor": 1.18},
    "British American Tobacco (BATS)": {"symbol": "BTI", "wkn": "916018", "paar": "Paar 4: Krisenfester Konsum", "typ": "Kernaktie", "kurs_eur": 32.10, "div_yield": 5.7, "kgv": 8.9, "monate": "Feb, Mai, Aug, Nov", "rot_monat": "Monat 4 (Feb, Jun, Okt)", "gewicht": 10.0, "risiko": "Defensiv", "sentiment": "Bullish", "infl_faktor": 1.16},
    "Visa Inc. (V)": {"symbol": "V", "wkn": "A0NC7B", "paar": "Wachstums-Monopol", "typ": "Satellit", "kurs_eur": 265.00, "div_yield": 0.7, "kgv": 28.5, "monate": "Mrz, Jun, Sep, Dez", "rot_monat": "Monatlicher Sparplan", "gewicht": 11.0, "risiko": "Growth", "sentiment": "Strong Bull", "infl_faktor": 1.45},
    "Microsoft Corp. (MSFT)": {"symbol": "MSFT", "wkn": "870747", "paar": "Wachstums-Monopol", "typ": "Satellit", "kurs_eur": 410.00, "div_yield": 0.7, "kgv": 32.4, "monate": "Mrz, Jun, Sep, Dez", "rot_monat": "Monatlicher Sparplan", "gewicht": 11.0, "risiko": "Growth", "sentiment": "Strong Bull", "infl_faktor": 1.50},
}


def make_portfolio_data(saved_weights: dict[str, float] | None = None) -> dict[str, dict[str, Any]]:
    portfolio = deepcopy(PORTFOLIO_DATA)
    for name, weight in (saved_weights or {}).items():
        if name in portfolio:
            portfolio[name]["gewicht"] = float(weight)
    return portfolio


def load_portfolio_data(store_path: Path | None = None) -> dict[str, dict[str, Any]]:
    path = store_path or Path(__file__).resolve().with_name("alpha_desk_data.json")
    try:
        store = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        store = {}
    weights = store.get("weights", {}) if isinstance(store, dict) else {}
    return make_portfolio_data(weights if isinstance(weights, dict) else {})


def build_inflation_series(inflation_factor: float) -> tuple[list[int], list[float], list[float]]:
    years = list(range(2000, 2057))
    rng = np.random.RandomState(101)
    consumer_price_index = [100.0]
    for year in years[1:]:
        rate = 0.6 if year in (2008, 2009) else (6.8 if year in (2022, 2023) else rng.normal(2.1, 0.5))
        consumer_price_index.append(consumer_price_index[-1] * (1 + max(-0.2, rate) / 100.0))

    asset_index = [100.0]
    for index in range(1, len(years)):
        inflation_step = consumer_price_index[index] / consumer_price_index[index - 1] - 1.0
        asset_index.append(asset_index[-1] * (1 + inflation_step * inflation_factor + 0.01))
    return years, consumer_price_index, asset_index


def calculate_order_route(asset: dict[str, Any], current_price: float, savings_amount: float) -> dict[str, float | int]:
    if current_price <= 0:
        raise ValueError("Der Referenzkurs muss größer als null sein.")
    net_budget = max(0.0, savings_amount / 2.0 - 1.0)
    whole_shares = int(net_budget // current_price)
    invested_amount = whole_shares * current_price
    return {
        "net_budget": net_budget,
        "whole_shares": whole_shares,
        "exact_shares": net_budget / current_price,
        "invested_amount": invested_amount,
        "cash_reserve": net_budget - invested_amount,
        "annual_dividend": net_budget * float(asset["div_yield"]) / 100.0,
    }
