from copy import deepcopy
from fractions import Fraction as F
import importlib.util,math
from pathlib import Path
import sys,unittest
import numpy as np
from scipy.special import roots_jacobi
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from link_decimation import build
spec=importlib.util.spec_from_file_location('independent_local_audit',ROOT/'tools'/'check_local_step.py')
checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)


class LocalStepChecks(unittest.TestCase):
    def test_independent_polynomial_and_majorant(self):
        ok,report=checker.audit(build());self.assertTrue(ok,report)
        self.assertEqual(report['checked_interaction_monomials'],36)

    def test_actual_3d_star_includes_six_pair_loops_and_quartic_interactions(self):
        case=build()['cases'][1];terms=case['normalized_log_weight_coefficients']
        self.assertEqual(sum(t['beta_power']==2 for t in terms),6)
        self.assertEqual(sum(len(t['pair_factors'])==2 for t in terms),21)
        self.assertTrue(any(t['beta_power']==4 and len(t['pair_factors'])==2 for t in terms))

    def test_uniform_remainder_against_independent_haar_quadrature(self):
        x,weights=roots_jacobi(64,.5,.5);weights=weights*(2/math.pi)
        def log_weight(beta,q):return math.log(float(np.sum(weights*np.exp(beta*math.sqrt(q)*x))))
        for case in build()['cases']:
            m=case['staple_count'];b=float(F(case['beta_max']));C=float(F(case['normalized_log_weight_error_le_beta6_times']))
            for beta in (b,b/2):
                for q in np.linspace(0,m*m,33):
                    numerical=log_weight(beta,q)-log_weight(beta,m)
                    polynomial=beta**2*(q-m)/8-beta**4*(q*q-m*m)/384
                    self.assertLessEqual(abs(numerical-polynomial),C*beta**6+1e-14)

    def test_exact_zero_and_reference_normalization(self):
        for case in build()['cases']:
            m=case['staple_count'];q=F(m);b=F(case['beta_max'])
            self.assertEqual(b*b*(q-m)/8-b**4*(q*q-m*m)/384,0)
            self.assertGreater(F(case['normalized_error_at_beta_max']),0)
            self.assertLess(F(case['normalized_error_at_beta_max']),F(1,10000))

    def test_corruptions_rejected(self):
        data=build();changes=[]
        a=deepcopy(data);a['analytic_gate_closed']=True;changes.append(a)
        a=deepcopy(data);a['rg_contraction_established']=True;changes.append(a)
        a=deepcopy(data);a['cases'][1]['normalized_log_weight_coefficients'].pop();changes.append(a)
        a=deepcopy(data);a['cases'][1]['normalized_log_weight_coefficients'][0]['coefficient']='1/2';changes.append(a)
        a=deepcopy(data);a['cases'][1]['normalized_log_weight_error_le_beta6_times']='0';changes.append(a)
        a=deepcopy(data);a['cases'][0]['beta_max']='1';changes.append(a)
        a=deepcopy(data);a['pair_variable']='Tr(S_i*S_j^dagger)';changes.append(a)
        for item in changes:self.assertFalse(checker.audit(item)[0])
if __name__=='__main__':unittest.main()
