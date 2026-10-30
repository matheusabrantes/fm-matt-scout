"""Independent implementation of FMSuperScout's published valuation equations."""

from bisect import bisect_left
from datetime import date
from math import exp, floor, log

MODEL_REVISION = 'cd0062e0e51ca57bbed5ef0268a04427e3655afd'
MODEL_URL = f'https://github.com/mavarobli/FMSuperScout/blob/{MODEL_REVISION}/app/app.js#L1027-L1140'
MODEL_COLUMNS = ('model_value', 'model_value_low', 'model_value_high',
                 'model_fee', 'model_fee_low', 'model_fee_high')


def rounded_money(value):
    step = 100000 if value >= 1000000 else 10000
    return floor(value / step + 0.5) * step


def estimate(player, game_date, buyer_reputation=None, wage_rank=None):
    result = dict.fromkeys(MODEL_COLUMNS)
    result.update(model_source='FMSuperScout', model_revision=MODEL_REVISION,
                  model_url=MODEL_URL, model_value_basis=None, model_regression_value=None,
                  model_fee_basis=None, model_assumptions=[])
    if player.get('contract_state') == 'free':
        result.update(dict.fromkeys(MODEL_COLUMNS, 0), model_fee_basis='free', model_value_basis='free')
        return result
    age, ca, pa, reputation = (player.get(key) for key in ('age', 'ca', 'pa', 'rep_world'))
    if (type(age) is not int or not 14 <= age <= 100
            or type(ca) is not int or not 1 <= ca <= 200
            or type(pa) is not int or not 1 <= pa <= 200
            or type(reputation) is not int or not 0 <= reputation <= 10000
            or player.get('contract_state') != 'contracted'):
        return result
    months = None
    contract = player.get('contract') or {}
    if (contract.get('start') or game_date) > game_date:
        return result
    if contract.get('end_source') == 'contract' and player.get('contract_end'):
        try:
            months = (date.fromisoformat(player['contract_end']) - date.fromisoformat(game_date)).days / 30.44
        except (ValueError, TypeError):
            return result
        if months < 0:
            return result
    if months is None:
        result['model_assumptions'].append('Prazo contratual não lido: 36 meses para valor e 30 para compra.')
    if reputation == 0:
        result['model_assumptions'].append('Reputação mundial zero: referência 3.000 do modelo.')
    fame = reputation or 3000
    fame = min(fame, 7500) + 0.3 * max(0, fame - 7500)
    headroom = max(0, pa - ca) * (1 if age <= 21 else 0.5 if age <= 24 else 0)
    value = exp(10.96 + 0.997 * fame / 1000 - 0.069 * age - 0.041 * headroom
                + 0.507 * log(max(2, 36 if months is None else months)))
    if months is not None and months <= 4:
        value *= 0.7
    value = rounded_money(value)
    result['model_regression_value'] = value
    stored = player.get('value')
    has_value = type(stored) is int and stored > 0
    result['model_value_basis'] = 'save' if has_value else 'model'
    if has_value:
        value = stored
    band = 0.5 if age <= 20 else 0.35
    if has_value:
        band = 0.15
    result.update(model_value=value, model_value_low=floor(value * (1-band) + 0.5),
                  model_value_high=floor(value * (1+band) + 0.5))
    base = value
    result['model_fee_basis'] = result['model_value_basis']
    if player.get('transfer_listed') is True:
        multiplier = 1
    else:
        multiplier = min(1.35, max(0.6, 0.7 + 0.014 * (30 if months is None else months)))
        if age <= 21 and pa - ca >= 15:
            multiplier *= 1 + min(0.2, (pa-ca) * 0.007)
        elif age <= 23:
            multiplier *= 1.05
        elif age >= 31:
            multiplier *= 0.8
        elif age >= 29:
            multiplier *= 0.9
        if wage_rank:
            rank, count = wage_rank
            multiplier *= 1.12 if rank <= 2 else 1.05 if rank <= 5 else 0.92 if rank / count > 0.6 else 1
        seller = player.get('club_reputation')
        if buyer_reputation and type(seller) is int and seller > 0:
            multiplier *= min(1.2, max(0.88, 1 + (buyer_reputation - seller) / 15000))
        multiplier = min(1.7, max(0.4, multiplier))
    fee = base if player.get('transfer_listed') is True and result['model_fee_basis'] == 'save' else rounded_money(base * multiplier)
    result.update(model_fee=fee, model_fee_low=floor(fee * 0.85 + 0.5),
                  model_fee_high=floor(fee * 1.15 + 0.5))
    return result


def enrich_estimates(players, game_date, buyer_reputation=None):
    wages = {}
    for player in players:
        club, wage = player.get('club_uid'), player.get('wage')
        if club is not None and type(wage) is int and wage > 0:
            wages.setdefault(club, []).append(-wage)
    for values in wages.values():
        values.sort()
    for player in players:
        values = wages.get(player.get('club_uid'), ())
        wage = player.get('wage')
        rank = ((bisect_left(values, -wage)+1, len(values))
                if len(values) >= 8 and type(wage) is int and wage > 0 else None)
        player.update(estimate(player, game_date, buyer_reputation, rank))
