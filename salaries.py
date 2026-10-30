import json
import math
from pathlib import Path
from contract_reader import RELEASE_KINDS

PERIODS = {'week': 1, 'month': 52 / 12, 'year': 52}
CURRENCIES = {'EUR', 'BRL', 'GBP', 'USD'}


class SalarySettings:
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {'currency': 'EUR', 'period': 'month', 'rates': {}}

    def view(self, career):
        data = self.read()
        rate = data['rates'].get(career, {}).get(data['currency'])
        money_rate = data.get('money_rates', {}).get(career, {}).get(data['currency'])
        return {'currency': data['currency'], 'period': data['period'],
                'rate': rate, 'money_rate': money_rate if money_rate is not None else rate,
                'money_source': 'clause' if money_rate is not None else 'salary' if rate is not None else None}

    def update(self, career, body, reference=None):
        currency, period = body.get('currency'), body.get('period')
        if currency not in CURRENCIES or period not in PERIODS:
            raise ValueError('Escolha uma moeda e um período válidos.')
        data = self.read()
        if 'amount' in body:
            amount = body['amount']
            wage = reference.get('wage') if reference else None
            if type(amount) not in (int, float) or not math.isfinite(amount) or not 0 < amount <= 10**12 or type(wage) not in (int, float) or not wage > 0:
                raise ValueError('Use um salário positivo do FM e um jogador/staff com salário lido.')
            rate = amount / (wage * PERIODS[period])
            if not math.isfinite(rate) or not 0 < rate <= 10**6:
                raise ValueError('Conversão fora da faixa permitida.')
            data['rates'].setdefault(career, {})[currency] = rate
        if 'money_amount' in body:
            amount = body['money_amount']
            kind = body.get('release_kind')
            clauses = ((reference or {}).get('contract') or {}).get('clauses') or []
            values = [c['value'] for c in clauses if c.get('kind') == kind
                      and c.get('parameter') is None and type(c.get('value')) in (int, float)
                      and math.isfinite(c['value']) and c['value'] > 0]
            if (type(kind) is not str or kind not in RELEASE_KINDS or not values or type(amount) not in (int, float)
                    or not math.isfinite(amount) or not 0 < amount <= 10**12):
                raise ValueError('Informe o valor positivo do FM e selecione uma cláusula de rescisão lida.')
            rate = amount / min(values)
            if not math.isfinite(rate) or not 0 < rate <= 10**6:
                raise ValueError('Conversão fora da faixa permitida.')
            data.setdefault('money_rates', {}).setdefault(career, {})[currency] = rate
        data.update(currency=currency, period=period)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data))
        temporary.replace(self.path)
        return self.view(career)
