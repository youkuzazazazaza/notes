
"""
案例文档：
输出一个函数，计算给定值的从0开始的累加计算，如果和必须小于123456，大于0
边界条件是必须是大于给定的参数必须是大于0的，累加求完的和必须小于12346
"""


def sum(n):
    sum = 0
    for index in range(n):
        sum += index
    return sum




import unittest
class TestLearn(unittest.TestCase):
    def test_sum(self):
        n = -1 
        assert n >= 0,"输入的参数必须是大于0"
        sum_value = sum(n)
        assert sum_value <= 123456,"求和的结果必须是小于123456"
        print("输出的结果是", sum_value)


if __name__ == '__main__':
    unittest.main()
