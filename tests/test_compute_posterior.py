"""
Test the inakeyaa.py functions.

Author
------
    Dr. Randal J. Barnes
    Department of Civil, Environmental, and Geo- Engineering
    University of Minnesota

Version
-------
    13 May 2020
"""

import numpy as np

from akeyaa.compute_posterior import compute_posterior


#--------------------------------------------------------------------------
def test_compute_posterior():
    data = np.array([
        [751., 841., 53.18, 2.],
        [255., 254., 51.02, 2.],
        [506., 814., 52.64, 2.],
        [699., 244., 51.89, 2.],
        [891., 929., 53.64, 2.],
        [959., 350., 52.62, 2.],
        [547., 197., 51.49, 2.],
        [139., 251., 50.78, 2.],
        [149., 616., 51.53, 2.],
        [258., 473., 51.46, 2.]
        ])
    i50 = 0.001
    (mu, sigma) = compute_posterior(i50, data)

    mu_ans = np.array([0.000326324847500637, 0.000291466465797025])

    sigma_ans = np.array([
        [ 6.27519301387955e-007, -2.38189347940752e-008],
        [-2.38189347940752e-008,  6.39825975889726e-007]
        ])

    assert(np.allclose(mu, mu_ans))
    assert(np.allclose(sigma, sigma_ans))


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    test_compute_posterior()
