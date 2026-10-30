import sys
import struct
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from club_finances import read_current_club_finances
from fmsave.readers.clubs import ClubRecordSpan
from fmsave.readers.finances import find_finance_layouts, _finance_row_reader


class CurrentClubFinanceTests(unittest.TestCase):
    def fixture(self, entries=0, balance=-125):
        build='26.3.2+2329565'
        layouts=find_finance_layouts(None,build)
        raw=bytearray(4000)
        span=ClubRecordSpan(318,100,len(raw),None)
        head=500
        struct.pack_into('<I',raw,head-4,3)
        reader=_finance_row_reader(layouts.chains)
        for offset in range(head,head+3*layouts.chains.row_bytes,layouts.chains.row_bytes):
            row=reader.row_struct.pack(1,100,200,150,10,8,40,0,0,30,10,40,10)
            raw[offset:offset+len(row)]=row
        start=head+3*layouts.chains.row_bytes
        prefix=layouts.sponsors
        for offset in (0,*prefix.prefix_date_offsets):
            raw[start+offset:start+offset+4]=prefix.prefix_marker
        raw[start+prefix.prefix_count_offset]=entries
        suffix=start+prefix.prefix_count_offset+1+entries*prefix.prefix_entry_bytes
        for offset,expected in prefix.prefix_suffix_fixed:
            raw[suffix+offset:suffix+offset+len(expected)]=expected
        for offset in prefix.prefix_suffix_date_offsets:
            raw[suffix+offset:suffix+offset+4]=prefix.prefix_marker
        struct.pack_into('<II',raw,suffix,250,40)
        struct.pack_into('<i',raw,suffix+22,balance)
        return raw,span,suffix,start

    def read(self,raw,spans,build='26.3.2+2329565'):
        return read_current_club_finances(bytes(raw),spans,build,date(2025,12,30))

    def test_current_suffix_is_distinct_from_monthly_history_and_signed(self):
        for entries in (0,1,3):
            raw,span,suffix,start=self.fixture(entries)
            result=self.read(raw,[span])[318]
            self.assertEqual(result,{'balance':-125,'transfer_budget_remaining':250,
                'wage_budget_weekly':40,'finance_source':'current','finance_date':'2025-12-30'})
        raw,span,_,_=self.fixture(balance=0)
        self.assertEqual(self.read(raw,[span])[318]['balance'],0)

    def test_invalid_prefix_or_truncation_cannot_read_neighbor_money(self):
        raw,span,suffix,start=self.fixture(entries=2)
        for at in (start,start+25,suffix+20,suffix+43):
            bad=bytearray(raw);bad[at]^=255
            self.assertEqual(self.read(bad,[span]),{})
        bad=bytearray(raw);bad[start+72+8]=1
        self.assertEqual(self.read(bad,[span]),{})
        short=ClubRecordSpan(318,span.record_start,suffix+67,None)
        self.assertEqual(self.read(raw,[short]),{})
        self.assertEqual(self.read(raw[:suffix+67],[span]),{})
        self.assertEqual(self.read(raw,[ClubRecordSpan(318,-1,len(raw),None)]),{})

    def test_version_plausibility_and_duplicate_ownership_are_required(self):
        raw,span,suffix,_=self.fixture()
        self.assertEqual(self.read(raw,[span],'26.4.0'),{})
        self.assertEqual(self.read(raw,[span],'26.3.2+9999999'),{})
        self.assertEqual(self.read(raw,[span,span]),{})
        for offset,value,fmt in [(0,2000000001,'<I'),(4,20000001,'<I'),(22,-400000001,'<i')]:
            bad=bytearray(raw);struct.pack_into(fmt,bad,suffix+offset,value)
            self.assertEqual(self.read(bad,[span]),{})

    def test_nonempty_primary_sponsors_must_validate_before_reading_current_money(self):
        raw,span,suffix,_=self.fixture(entries=3)
        raw[suffix+67]=1
        row=suffix+68
        raw[row]=2
        struct.pack_into('<HH',raw,row+2,1,2025)
        struct.pack_into('<HH',raw,row+6,1,2027)
        struct.pack_into('<I',raw,row+11,1000)
        struct.pack_into('<I',raw,row+21,500)
        self.assertEqual(self.read(raw,[span])[318]['balance'],-125)
        raw[row+10]=2
        self.assertEqual(self.read(raw,[span]),{})
        raw[row+10]=0
        struct.pack_into('<I',raw,row+21,1001)
        self.assertEqual(self.read(raw,[span]),{})
