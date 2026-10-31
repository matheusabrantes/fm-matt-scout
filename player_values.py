"""Keep explicit zero valuations separate from missing save fields."""


def market_value_fields(player):
    state = player.get('transfer_value_state')
    value = player.get('transfer_value')
    if state == 'zero' and (value is None or type(value) is int and value == 0):
        value = 0
    elif (state not in ('ok', None) or type(value) is not int or value < 0):
        value = None
    status = ('zero' if value == 0 else 'ok') if value is not None else (
        state if state in ('placeholder', 'unset') else 'unavailable')
    notes = {
        'ok': 'Valor lido do save; pode diferir da faixa exibida no FM.',
        'zero': 'Valor zero gravado no save; não significa jogador sem contrato.',
        'placeholder': 'O save contém um marcador em vez de um valor de mercado.',
        'unset': 'O save não registra este valor de mercado.',
        'unavailable': 'O valor de mercado não pôde ser lido.',
    }
    player.update(value=value, value_source='save' if value is not None else None,
                  value_status=status, value_note=notes[status])
