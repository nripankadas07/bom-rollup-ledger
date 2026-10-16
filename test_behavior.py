import unittest
from bom_rollup_ledger import analyze, rows, amount, exact
from fractions import Fraction

B = "parent,component,quantity\n"
C = "part,unit_cost\n"


class RollupTests(unittest.TestCase):
    def test_shared_assembly_accumulates_before_propagating(self):
        b = B + "R,A,2\nR,B,3\nA,S,4\nB,S,5\nS,L,0.1\n"
        r = analyze(b, C + "L,2.50\n", "R", "2")
        self.assertEqual(r['leaves'], [{'part': 'L', 'quantity': '4.6', 'unit_cost': '2.5', 'extended_cost': '11.5'}])
        self.assertEqual(r['total_material_cost'], '11.5')

    def test_decimal_products_are_exact(self):
        r = analyze(B + "A,B,0.1\nB,C,0.2\n", C + "C,0.3\n", 'A')
        self.assertEqual(r['total_material_cost'], '0.006')

    def test_missing_price_withholds_total(self):
        r = analyze(B + "R,A,2\nR,B,3\n", C + "A,4\n", 'R')
        self.assertEqual((r['known_material_subtotal'], r['total_material_cost'], r['missing_prices']), ('8', None, ['B']))

    def test_zero_price_is_known(self):
        r = analyze(B + "R,A,2\n", C + "A,0\n", 'R')
        self.assertTrue(r['complete'])
        self.assertEqual(r['total_material_cost'], '0')

    def test_leaf_root(self):
        r = analyze(B, C + "L,2\n", 'L', '3')
        self.assertEqual(r['total_material_cost'], '6')

    def test_unpriced_leaf_can_be_root(self):
        r = analyze(B + "R,L,2\n", C, 'L')
        self.assertEqual(r['missing_prices'], ['L'])

    def test_unrelated_prices_are_visible(self):
        r = analyze(B + "R,L,2\n", C + "L,2\nX,10\n", 'R')
        self.assertEqual(r['unused_prices'], ['X'])

    def test_order_independence(self):
        lines = ['R,A,2', 'R,B,3', 'B,S,2', 'A,S,1']
        a = analyze(B + '\n'.join(lines) + '\n', C + 'S,4\n', 'R')
        b = analyze(B + '\n'.join(reversed(lines)) + '\n', C + 'S,4\n', 'R')
        self.assertEqual(a['leaves'], b['leaves'])
        self.assertEqual(a['total_material_cost'], '32')

    def test_cycle_anywhere_refuses_partial_result(self):
        with self.assertRaisesRegex(ValueError, 'cycle'):
            analyze(B + 'R,L,1\nX,Y,1\nY,X,1\n', C + 'L,1\n', 'R')

    def test_duplicate_edge_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            analyze(B + 'R,L,1\nR,L,2\n', C + 'L,1\n', 'R')

    def test_assembly_price_refused(self):
        with self.assertRaisesRegex(ValueError, 'leaves'):
            analyze(B + 'R,L,1\n', C + 'R,1\nL,2\n', 'R')

    def test_duplicate_price_refused(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            analyze(B, C + 'L,1\nL,2\n', 'L')

    def test_quoted_unicode_id(self):
        r = analyze(B + 'R,"ভাল,part",2\n', C + '"ভাল,part",3\n', 'R')
        self.assertEqual(r['total_material_cost'], '6')

    def test_bad_csv_shapes(self):
        for s in ['a,b,c\n', B + 'R,L\n', B + 'R,L,1,extra\n']:
            with self.subTest(s=s), self.assertRaises(ValueError):
                analyze(s, C, 'R')

    def test_bad_amounts(self):
        for q in ['-1', '1e2', 'NaN', 'True', '.1', '1.123456789']:
            with self.subTest(q=q), self.assertRaises(ValueError):
                amount(q)
        with self.assertRaises(ValueError):
            amount('0', positive=True)

    def test_deep_chain_without_python_recursion(self):
        b = B + ''.join(f'P{i},P{i+1},1\n' for i in range(1500))
        self.assertEqual(analyze(b, C + 'P1500,2\n', 'P0')['total_material_cost'], '2')

    def test_unknown_root_and_bad_currency(self):
        with self.assertRaises(ValueError):
            analyze(B, C, 'X')
        with self.assertRaises(ValueError):
            analyze(B, C + 'X,1\n', 'X', currency='usd')

    def test_nonprinting_identifiers_refused(self):
        for value in ['L\x7f', 'L\u200b', 'L\u202e', 'L\x00']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                analyze(B + 'R,' + value + ',1\n', C, 'R')

    def test_arithmetic_budget(self):
        with self.assertRaisesRegex(ValueError, 'budget'):
            exact(Fraction(2**5000))


if __name__ == '__main__':
    unittest.main()
