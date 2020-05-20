"""
Test the smith_distrubiotn.py functions.

Author
------
    Dr. Randal J. Barnes
    Department of Civil, Environmental, and Geo- Engineering
    University of Minnesota

Version
-------
    17 May 2020
"""

import numpy as np

from akeyaa.smith_distribution import smith_pdf, smith_cdf, smith_quartiles


#--------------------------------------------------------------------------
def test_smith_pdf():
    mu = np.array( [[1.], [2.]] )
    sigma = np.array( [[2., 1.], [1., 3.]] )

    alpha = np.linspace(0, 2*np.pi, 10)
    pdf = smith_pdf(alpha, mu, sigma)

    pdf_ans = np.array([
        0.082633326709771, 0.453847423028614, 0.538084798525049,
        0.117852523781454, 0.051437060901120, 0.040453966191302,
        0.037600718897055, 0.030693276068009, 0.035604961954848,
        0.082633326709771])

    assert(np.allclose(pdf, pdf_ans))


#--------------------------------------------------------------------------
def test_smith_cdf():
    mu = np.array( [[1.], [2.]] )
    sigma = np.array( [[2., 1.], [1., 3.]] )

    lb = np.pi/4
    ub = np.pi/2
    cdf = smith_cdf(lb, ub, mu, sigma)

    cdf_ans = np.array([0.5066762601816892])
    assert(np.allclose(cdf, cdf_ans))


#--------------------------------------------------------------------------
def test_smith_quartiles():
    mu = np.array( [[1.], [2.]] )
    sigma = np.array( [[2., 1.], [1., 3.]] )

    a25, a50, a75 = smith_quartiles(mu, sigma)

    a25_ans = 0.7490668340655687
    a50_ans = 1.1071487177940904
    a75_ans = 1.5039391029162892

    assert(np.isclose(a25, a25_ans))
    assert(np.isclose(a50, a50_ans))
    assert(np.isclose(a75, a75_ans))

    cdf = smith_cdf(a25, a75, mu, sigma)
    assert(np.isclose(cdf, 0.50))


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    test_smithpdf()