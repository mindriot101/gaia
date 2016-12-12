"""
Estimate r_star from IRFM theta and GAIA parallaxes
"""
import argparse as ap

def argParse():
    """
    Parse the command line arguments
    """
    parser = ap.ArgumentParser()
    parser.add_argument('theta',
                        help='theta value from IRFM (mas)'
                        type=float)
    parser.add_argument('parallax',
                        help='parallax from GAIA (mas)'
                        type=float)
    return parser.parse_args()

def rStar(theta, parallax):
    """
    Calculate r_star from IRFM theta and parallax
    """
    r_star = 214.9*(theta/2.)/parallax
    print(r_star)
    return r_star

if __name__ == "__main__":
    args = argParse()
    r = rStar(args.theta, args.parallax)

