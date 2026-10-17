from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from scalar_bridge import build
spec=importlib.util.spec_from_file_location('independent_bridge_constants',ROOT/'tools'/'check_constants.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)


class BridgeChecks(unittest.TestCase):
    def test_independent_constants(self):
        ok,detail=checker.audit(build());self.assertTrue(ok,detail)

    def test_corruptions(self):
        data=build();mutations=[]
        a=deepcopy(data);a['cases'][0]['channel_transfer_radius_upper']='1/100';mutations.append(a)
        a=deepcopy(data);a['cases'][1]['spatial_polynomial_low_to_high'][0]='50';mutations.append(a)
        a=deepcopy(data);a['cases'][0]['dimensionless_energy_lower_endpoint_interval']=['1','2'];mutations.append(a)
        a=deepcopy(data);a['analytic_gate_closed']=True;mutations.append(a)
        a=deepcopy(data);a['required_hypotheses'].pop();mutations.append(a)
        for item in mutations:self.assertFalse(checker.audit(item)[0])

    def test_above_radius_atom_eventually_violates_polynomial_bound(self):
        alpha=F(1,2);r=F(3,4);n=128
        self.assertGreater(F(1,100)*r**n,(1+n*n)*alpha**n)
        self.assertLessEqual(alpha**n,(1+n*n)*alpha**n)

    def test_one_channel_is_not_all_sectors(self):
        # Diagonal positive transfer matrix (1,1/2,99/100); observable sees only 1/2.
        observable=[F(0),F(1),F(0)];eigenvalues=[F(1),F(1,2),F(99,100)]
        for n in range(8):
            moment=sum(w*w*v**n for w,v in zip(observable,eigenvalues))
            self.assertEqual(moment,F(1,2)**n)
        self.assertGreater(eigenvalues[2],F(1,2))
if __name__=='__main__':unittest.main()
