#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from astropy.coordinates import SkyCoord
from astropy import units as u
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import queryGaia  # noqa


class TestNameParsing(unittest.TestCase):

    def setUp(self):
        self.name = '1SWASP J063201.52+440921.4'
        self.expected = str(SkyCoord(
            ra=98.00633333 * u.degree,
            dec=44.15594444 * u.degree
        ))

    # Match the string representations as this handles float closeness issues
    def test_valid_name(self):
        coord = queryGaia.swaspIdToSkyCoord(self.name)
        self.assertEqual(str(coord), self.expected)

    def test_name_without_space(self):
        newname = self.name.replace(' ', '')
        coord = queryGaia.swaspIdToSkyCoord(newname)
        self.assertEqual(str(coord), self.expected)

    def test_invalid_name_parsing(self):
        newname = self.name.replace('SWASP', 'FOOBAR')
        self.assertIsNone(
            queryGaia.swaspIdToSkyCoord(newname)
        )

if __name__ == '__main__':
    unittest.main()
