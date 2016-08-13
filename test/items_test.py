import unittest
import items

class MyTest(unittest.TestCase):
    def test_match_filefolder(self):
        for i in items.FilesDirectories.match_filefolder('/',['hom','sz']):
            self.assertEqual(i, '/home/sz')

#unittest.main()
