import unittest

import appparser


class TDProcessingTest(unittest.TestCase):
    def testPostionsParsing(self, from_file="C:\Users\gokul\workspace\\finase\printVersion.txt"):
        obj = appparser.TDPositions(from_file=from_file)
        print obj.getCurrentBalancesAndPositions().to_string()

    def testURLGeneration(self):
        from_file = "C:\Users\gokul\workspace\\finase\printVersion.txt"
        obj = appparser.TDPositions(from_file=from_file)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
