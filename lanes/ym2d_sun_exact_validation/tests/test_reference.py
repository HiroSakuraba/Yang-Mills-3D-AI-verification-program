"""Exact arithmetic and deliberate-corruption regression controls."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from ym2d_wilson import build, kernel_interval
spec=importlib.util.spec_from_file_location('independent_2d_checker',ROOT/'tools'/'check_ym2d_exact.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)


class Exact2DChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data=build()

    def test_independent_reference(self):
        ok,report=checker.audit(self.data)
        self.assertTrue(ok,report)
        self.assertEqual(report['oriented_rectangles'],120)
        self.assertEqual(report['area_law_cases'],64)
        self.assertEqual(report['rational_intervals'],88)

    def test_haar_character_normalization(self):
        self.assertEqual([checker.haar_moment(k) for k in range(7)],
                         [F(1),F(0),F(1,4),F(0),F(1,8),F(0),F(5,64)])
        self.assertEqual(checker.coefficient(1,1),F(1,4))
        self.assertEqual(checker.coefficient(2,2),F(1,24))
        for n in (1,2):
            self.assertEqual(kernel_interval(F(0),n),(F(0),F(0)))

    def test_catalan_and_generator_bounds_agree_exactly(self):
        for beta in (F(0),F(1,2),F(2),F(4)):
            for n in (0,1,2):
                self.assertEqual(kernel_interval(beta,n),checker.moment_enclosure(beta,n))

    def test_noncommutative_exterior_cancellation(self):
        loop=next(r for r in self.data['loops'] if r['rectangle']==[1,4,0,3] and r['orientation']==1)
        self.assertGreater(len(loop['axial_word']),loop['area'])
        inside={tuple(p) for p in loop['interior_plaquettes']}
        remainder=[tuple(letter) for letter in loop['axial_word'] if tuple(letter[:2]) not in inside]
        self.assertTrue(remainder)
        self.assertEqual(checker.reduce_word(remainder),[])
        # A commutator must not be erased by treating a non-Abelian word as counts.
        self.assertNotEqual(checker.reduce_word([(0,0,1),(1,0,1),(0,0,-1),(1,0,-1)]),[])

    def test_corruptions_rejected(self):
        mutations=[]
        a=deepcopy(self.data);a['action']='exp(beta*sum_plaquettes(Tr(U_p)))';mutations.append(a)
        a=deepcopy(self.data);a['one_plaquette'][4]['normalized_character_mean']['lower']='2';mutations.append(a)
        a=deepcopy(self.data);a['one_plaquette'][5]['kernel_integral']['upper']='100';mutations.append(a)
        a=deepcopy(self.data);a['area_law_expectations'][1]['area']=99;mutations.append(a)
        a=deepcopy(self.data);a['loops'][0]['area']+=1;mutations.append(a)
        a=deepcopy(self.data);a['loops'][0]['axial_word'][0][2]*=-1;mutations.append(a)
        a=deepcopy(self.data);a['loops'].pop();mutations.append(a)
        a=deepcopy(self.data);a['comb_tree'].pop();mutations.append(a)
        a=deepcopy(self.data);a['loops'][0]['orientation']=True;mutations.append(a)
        a=deepcopy(self.data);a['boundary']='periodic';mutations.append(a)
        a=deepcopy(self.data);a['one_plaquette'][0]['beta']='0.0';mutations.append(a)
        a=deepcopy(self.data);a['outward_dyadic_bits']=16;mutations.append(a)
        for data in mutations:
            self.assertFalse(checker.audit(data)[0])

    def test_readiness_requires_every_existing_geometry_parent(self):
        missing=checker.readiness({})
        self.assertEqual(set(missing),set(checker.PREREQUISITES))
        state={'gates':{g:{'status':'CLOSED'} for g in checker.PREREQUISITES}}
        self.assertEqual(checker.readiness(state),[])
        state['gates']['YM3D_SUPPORT_LIFT_1']['status']='OPEN'
        self.assertEqual(checker.readiness(state),['YM3D_SUPPORT_LIFT_1'])

    def test_report_only_and_full_gate_cannot_accidentally_unlock_analytics(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp); lane=repo/'lanes'/'reference'; art=lane/'artifacts'
            art.mkdir(parents=True); (repo/'artifacts').mkdir()
            (art/'reference.json').write_text(json.dumps(self.data))
            state={'gates':{g:{'status':'CLOSED'} for g in checker.PREREQUISITES}}
            (repo/'artifacts'/'state.json').write_text(json.dumps(state))
            with patch.object(checker,'ROOT',lane), patch.object(checker,'REPOSITORY',repo):
                with patch.object(sys,'argv',['check_ym2d_exact.py','--report-only']):
                    self.assertEqual(checker.main(),0)
                self.assertFalse((art/'decision.json').exists())
                with patch.object(sys,'argv',['check_ym2d_exact.py']):
                    self.assertEqual(checker.main(),0)
            self.assertEqual(json.loads((art/'decision.json').read_text())['status'],'BLOCKED')
            self.assertFalse(json.loads((art/'benchmark_report.json').read_text())['program_gate_closed'])


if __name__=='__main__': unittest.main()
