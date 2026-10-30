"""Current club finances from the validated prefix of its own sponsor list."""
import struct

from fmsave.readers.finances import (
    find_finance_layouts, locate_finance_chain, locate_sponsor_chain,
)


def read_current_club_finances(game_db, spans, build, clock, schema=None):
    # shortcut: only the 26.3.2 suffix has independent in-game controls.
    if build != '26.3.2+2329565':
        return {}
    layouts = find_finance_layouts(schema, build)
    prefix = layouts.sponsors
    if prefix.prefix_suffix_bytes != 68:
        return {}
    found, ambiguous = {}, set()
    for span in spans:
        if not 0 <= span.record_start < span.record_end <= len(game_db):
            continue
        chain = locate_finance_chain(game_db, span, layouts.chains)
        if chain is None:
            continue
        head, count, _ = chain
        start = head + count * layouts.chains.row_bytes
        sponsors = locate_sponsor_chain(game_db, start, span.record_end, prefix)
        if sponsors is None:
            continue
        count_at = start + prefix.prefix_count_offset
        suffix = count_at + 1 + game_db[count_at] * prefix.prefix_entry_bytes
        if suffix + prefix.prefix_suffix_bytes > span.record_end or sponsors[0] != suffix + prefix.prefix_suffix_bytes:
            continue
        transfer, wage = struct.unpack_from('<II', game_db, suffix)
        balance = struct.unpack_from('<i', game_db, suffix + 22)[0]
        low, high = layouts.chains.balance_range
        if not low <= balance <= high or transfer > high or wage > layouts.chains.weekly_maximum:
            continue
        if span.club_uid in found:
            ambiguous.add(span.club_uid)
        else:
            found[span.club_uid] = {
                'balance': balance, 'transfer_budget_remaining': transfer,
                'wage_budget_weekly': wage, 'finance_source': 'current',
                'finance_date': str(clock),
            }
    return {uid: fields for uid, fields in found.items() if uid not in ambiguous}
