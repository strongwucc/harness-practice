# 测试层·修复后的测试组：忠实契约 fixture
#
# 同一组业务用例，fixture 直接从契约模拟层取数（渠道按分回传）——
# 输入忠实于外部契约后，错误实现立即现形：broken 1/3，fixed 3/3。
#
# 注意 broken 唯一「通过」的用例（变价拒绝）：它对的原因是「恰好两个数不等」
# ——否定性用例无法区分「对的理由」，这也是假绿难以自查的机制之一。

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import contract
from reconciliation import broken, fixed
from reconciliation.fixed import PriceFieldDriftError

# ---- fixture：从契约模拟层取数，渠道按分回传（忠实外部契约）----
RESP = contract.channel_render_response('0.60')   # 渠道渲染响应：item_price=60（分）
PRICE_FEN = RESP['item_price']                     # 60 —— 分，不是 0.60
FROZEN = contract.local_frozen_cost('0.60')        # '0.60' —— 元


def _drifts_to_probe(fn, *args):
  """「应转探查」= 抛 PriceFieldDriftError（不终态、不硬拒）"""
  try:
    fn(*args)
    return False
  except PriceFieldDriftError:
    return True


# ---- 用例 1：平价单应放行（原事故的直接杀伤面——该平价样本被误拒）----
def test_faithful_same_price_passes_broken():
  assert broken.assert_price_match(PRICE_FEN, FROZEN) is True  # 事故版：60 != 0.60 → 误拒


def test_faithful_same_price_passes_fixed():
  assert fixed.assert_price_match(PRICE_FEN, FROZEN) is True   # 修复版：归一化后放行


# ---- 用例 2：变价单应拒绝（渠道 61 分 vs 本地 0.60 元）——严格断言返回 False，
#      不把「异常转探查」算作拒绝（拒绝与探查是两种不同裁决）----
def test_faithful_changed_price_rejected_broken():
  assert broken.assert_price_match(61, FROZEN) is False        # 碰巧对：恰好两数不等


def test_faithful_changed_price_rejected_fixed():
  assert fixed.assert_price_match(61, FROZEN) is False         # 对得有理由


# ---- 用例 3：非整数分（字段漂移信号）应转探查、不硬拒（原事故边界处理）----
def test_faithful_drifted_field_probes_broken():
  assert _drifts_to_probe(broken.assert_price_match, 60.5, FROZEN)  # 事故版误当价变硬拒


def test_faithful_drifted_field_probes_fixed():
  assert _drifts_to_probe(fixed.assert_price_match, 60.5, FROZEN)   # 修复版抛漂移异常


IMPLEMENTATIONS = {
  'broken(事故版)': [test_faithful_same_price_passes_broken,
                     test_faithful_changed_price_rejected_broken,
                     test_faithful_drifted_field_probes_broken],
  'fixed(修复版)': [test_faithful_same_price_passes_fixed,
                    test_faithful_changed_price_rejected_fixed,
                    test_faithful_drifted_field_probes_fixed],
}

# 预期通过数：broken 的 2 个 FAIL 是演示预期（它就是事故版）；
# fixed 必须全绿——任何偏离都意味着实现退化或 fixture 失真，属于意外
EXPECTED_PASS = {'broken(事故版)': 1, 'fixed(修复版)': 3}

if __name__ == '__main__':
  unexpected = []
  for impl, tests in IMPLEMENTATIONS.items():
    failed = 0
    for fn in tests:
      try:
        fn()
        print('  PASS {} :: {}'.format(impl, fn.__name__))
      except AssertionError:
        print('  FAIL {} :: {}'.format(impl, fn.__name__))
        failed += 1
    passed = len(tests) - failed
    print('  忠实 fixture 组 [{}]: {}/{} 通过'.format(impl, passed, len(tests)))
    if passed != EXPECTED_PASS[impl]:
      unexpected.append('{} 通过 {}/{}（预期 {}）'.format(impl, passed, len(tests), EXPECTED_PASS[impl]))
  if unexpected:
    print('  [意外偏离] 预期结果矩阵被打破——实现退化或 fixture 失真: {}'.format('; '.join(unexpected)))
    sys.exit(1)
  print('  结果符合预期矩阵（broken 的 FAIL 为演示预期，非测试故障）')
  sys.exit(0)
