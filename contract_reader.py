"""Contract states from the player's current registration and decoded terms."""

RELEASE_KINDS = {'minimum_fee_release', 'minimum_fee_release_foreign', 'minimum_fee_release_domestic',
                 'minimum_fee_release_domestic_higher_division', 'relegation_release', 'non_promotion_release'}


def contract_state(row):
    contract = row.get('contract')
    if not isinstance(contract, dict) or not contract:
        return 'unknown'

    wage = contract.get('wage')
    kind = contract.get('kind_code')
    has_terms = (type(wage) is int and wage > 0) or (type(kind) is int and kind >= 0)
    if contract.get('club_uid') is not None and has_terms:
        return 'contracted'

    if ('team_id' not in row or row['team_id'] is not None
            or 'club_uid' not in row or row['club_uid'] is not None):
        return 'unknown'
    required = ('club_uid', 'team_id', 'wage', 'kind_code', 'end_source')
    if not all(key in contract for key in required):
        return 'unknown'
    current = ('club_uid', 'team_id', 'wage', 'kind_code', 'squad_status_code', 'event_count')
    if any(contract.get(key) is not None for key in current) or contract.get('clauses'):
        return 'unknown'
    if contract['end_source'] not in ('none', 'player_record'):
        return 'unknown'
    # Fallback dates and future chain records do not establish a contract in effect.
    return 'free'


def listing_status(row, build, game_date):
    contract = row.get('contract') or {}
    code = (contract.get('unknown') or {}).get('e39')
    # shortcut: only 0/1/2 on 26.3.2 are checked in game; extend after checking other states/builds.
    if (not build.startswith('26.3.2+') or contract_state(row) != 'contracted'
            or contract.get('end_source') != 'contract'
            or not contract.get('start') or contract['start'] > game_date
            or not contract.get('end') or contract['end'] < game_date
            or type(code) is not int or code not in (0, 1, 2)):
        return None, None
    return code == 1, code == 2
