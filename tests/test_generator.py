import random
import string
import unittest

from src.generator import (
    generate_hidden_params,
    generate_issues,
    generate_project_info,
    find_board_id,
    HIDDEN_PARAMS
)

def randomstr(b):
    n = random.randint(1, b)
    randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
    return ''.join(randlst)

generate_hidden_params_html = """
<html>
    <head>
        <h1>test html</h1>
        <div>
            <input name="{}" value="{}">
            <input name="{}" value="{}">
            <input name="{}" value="{}">
            <input name="{}" value="{}">
        </div>
    </head>
</html>
"""

generate_project_info_html = """
<table id="_ctl0_ContentPlaceHolder1_gridList">
    <tbody>
        <tr class="header">
            <td>col 1</td>
            <td>col 2</td>
            <td>col 3</td>
            <td>col 4</td>
        </tr>
        {}
    </tbody>
</table>
"""

generate_issues_html = """
<table id="_ctl0_ContentPlaceHolder1_gridList">
    <tbody>
        <tr class="pager">
            <td>1</td>
        </tr>
        <tr class="header">
            <td>col 1</td>
            <td>col 2</td>
            <td>col 3</td>
            <td>col 4</td>
            <td>col 5</td>
            <td>col 6</td>
            <td>col 7</td>
        </tr>
        {}
        <tr class="pager">
            <td>1</td>
        </tr>
    </tbody>
</table>
"""

project_info_tr_html = """
<tr>
    <td>{0[0]}</td>
    <td><a href="#">{0[1]}</a></td>
    <td>{0[2]}</td>
    <td>{0[3]}</td>
</tr>
"""

issues_tr_html = """
<tr>
    <td>{0[0]}</td>
    <td><a href="#">{0[1]}</a></td>
    <td>{0[2]}</td>
    <td>{0[3]}</td>
    <td>{0[4]}</td>
    <td>{0[5]}</td>
    <td>{0[6]}</td>
</tr>
"""

find_board_id_html = """
<table id="_ctl0_ContentPlaceHolder1_gridList">
    <tbody>
        <tr class="header">
            <td>col 1</td>
            <td>col 2</td>
            <td>col 3</td>
            <td>col 4</td>
        </tr>
        {}
    </tbody>
</table>
"""

find_board_id_td_html = """
<tr>
    <td>hoge</td>
    <td><a href="{0[0]}={0[1]}">{0[2]}</a></td>
    <td>hoge</td>
    <td>hoge</td>
    <td>hoge</td>
    <td>hoge</td>
    <td>hoge</td>
</tr>
"""

class GeneratorTest(unittest.TestCase):
    def test_generate_hidden_params(self):
        rs0 = randomstr(50)
        rs1 = randomstr(60)
        rs2 = randomstr(70)
        rs3 = randomstr(80)
        
        html = generate_hidden_params_html.format(
            HIDDEN_PARAMS[0], rs0,
            HIDDEN_PARAMS[1], rs1,
            HIDDEN_PARAMS[2], rs2,
            HIDDEN_PARAMS[3], rs3
        )
        data = generate_hidden_params(html)
        expected = {
            HIDDEN_PARAMS[0]: rs0,
            HIDDEN_PARAMS[1]: rs1,
            HIDDEN_PARAMS[2]: rs2,
            HIDDEN_PARAMS[3]: rs3
        }

        self.assertEqual(data, expected)

    def test_generate_project_info(self):
        N = random.randint(1, 50)

        random_rows = [[randomstr(40) for _ in range(4)] for __ in range(N)]
        rows = [project_info_tr_html.format(random_rows[i]) for i in range(N)]

        html = generate_project_info_html.format("".join(rows))

        data = generate_project_info(html)
        expected = [random_rows[i][0:2] for i in range(N)]

        self.assertEqual(data, expected)

    def test_generate_issues(self):
        N = random.randint(1, 50)
        random_rows = [[randomstr(40) for _ in range(7)] for __ in range(N)]
        rows = [issues_tr_html.format(random_rows[i]) for i in range(N)]

        html = generate_issues_html.format("".join(rows))
        data = generate_issues(html)

        self.assertEqual(data, random_rows)

    def test_find_board_id(self):
        N = random.randint(1, 50)
        pares = [[randomstr(40) for _ in range(3)] for __ in range(N)]
        rows = [find_board_id_td_html.format(pares[i]) for i in range(N)]

        html = find_board_id_html.format("".join(rows))

        M = random.randint(1, N)
        _, board_id, name = pares[M]
        data = find_board_id(html, name)

        self.assertEqual(data, board_id)

if __name__=="__main__":
    unittest.main()