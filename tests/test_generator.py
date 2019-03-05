import random
import string
import unittest

# module importができない
from src import generator


def randomname(n):
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)

html = """
<div>
    <input name={} value{}>
    <input name={} value{}>
    <input name={} value{}>
    <input name={} value{}>
</div>
"""


class GeneratorTest(unittest.TestCase):
    def generate_hidden_params_test(self):
        rs1 = randomname(random.randint(50))
        rs2 = randomname(random.randint(60))
        rs3 = randomname(random.randint(70))
        rs4 = randomname(random.randint(80))
        rs5 = randomname(random.randint(90))
        rs6 = randomname(random.randint(100))
        rs7 = randomname(random.randint(110))
        rs8 = randomname(random.randint(120))
        
        data = generator.generate_hidden_params(html.format(rs1, rs2, rs3, rs4, rs5, rs6, rs7, rs8))
        expected = {
            rs1: rs2,
            rs3: rs4,
            rs5: rs6,
            rs7: rs8
        }

        self.assertEqual(data, expected)

if __name__=="__main__":
    unittest.main()
