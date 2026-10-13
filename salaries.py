import json
import math
from pathlib import Path

PERIODS = {'week': 1, 'month': 52 / 12, 'year': 52}
CURRENCIES = {'EUR', 'BRL', 'GBP', 'USD'}


class SalarySettings:
    def __init__(self, path):
        self.path = Path(path)

    def read(self):
        return json.loads(self.path.read_text()) if self.path.exists() else {'currency': 'EUR', 'period': 'month', 'rates': {}}

    def view(self, career):
        data = self.read()
        return {'currency': data['currency'], 'period': data['period'],
                'rate': data['rates'].get(career, {}).get(data['currency'])}

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
        data.update(currency=currency, period=period)
        temporary = self.path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data))
        temporary.replace(self.path)
        return self.view(career)
