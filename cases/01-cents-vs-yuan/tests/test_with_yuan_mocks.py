# 测试层·事故前的测试组（历史快照）：元值 mock
#
# 这组测试复现「事故前」的状态：mock 数据与被测实现犯同一个单位假设——
# mock 的渠道返回值按「元」给（0.60），实现也按「元」比。
# 结果：测试全绿，但对错误实现零检出力——这就是「mock 同源假绿」。
#
# 注意：本组只对事故版（broken）有意义——它就是当时唯一存在的实现。
# 修复后这组 mock 被整体重写为忠实契约 fixture（见 test_with_faithful_fixtures.py）。

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reconciliation.broken import assert_price_match


# ---- mock 数据：全部按「元」构造（与实现同源的单位假设）----
MOCK_CHANNEL_PRICE = 0.60   # mock 作者以为渠道按元传
MOCK_FROZEN_COST = '0.60'   # 本地冻结成本（元）


def test_price_match_passes_on_same_price():
  # 同价应放行——在元值 mock 下，错误实现「恰好」答对
  assert assert_price_match(MOCK_CHANNEL_PRICE, MOCK_FROZEN_COST) is True


def test_price_match_rejects_on_diff_price():
  # 异价应拒绝
  assert assert_price_match(0.65, MOCK_FROZEN_COST) is False


def test_price_match_rejects_on_cost_drift():
  # 成本漂移应拒绝
  assert assert_price_match(MOCK_CHANNEL_PRICE, '0.62') is False


if __name__ == '__main__':
  tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith('test_')]
  failed = 0
  for name, fn in tests:
    try:
      fn()
      print('  PASS {}'.format(name))
    except AssertionError:
      print('  FAIL {}'.format(name))
      failed += 1
  print('  元值 mock 组: {} passed, {} failed —— 全绿，但对事故版实现零检出力（假绿）'.format(
    len(tests) - failed, failed))
  sys.exit(1 if failed else 0)
