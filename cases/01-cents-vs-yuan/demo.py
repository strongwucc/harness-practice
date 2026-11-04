# 一条命令复现整个案例：python3 demo.py
#
# 输出四幕对照：契约层 → 校验层 → 测试层（假绿 → 有牙齿）
# 依赖：Python 3.8+ 标准库，无第三方依赖

import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.join(HERE, 'tests')


def run(script):
  # 运行测试子进程：非零退出或 stderr 属意外（预期失败矩阵由 runner 自身校验），
  # 显式暴露而不是静默继续——演示不能在有故障时仍打印成功叙事
  r = subprocess.run([sys.executable, os.path.join(TESTS, script)],
                     capture_output=True, text=True)
  out = r.stdout.rstrip()
  if r.returncode != 0 or r.stderr.strip():
    out += '\n  [意外] 子进程异常退出(code={}): {}'.format(
      r.returncode, r.stderr.strip()[:200])
  return out


def main():
  print('=' * 62)
  print('案例 01：渠道按分传数据、本地按元比较——契约失真如何骗过测试')
  print('=' * 62)

  print('\n[1] 契约层（合成 fixture，模拟外部契约的单位约定）')
  import contract
  resp = contract.channel_render_response('0.60')
  print('  渠道 render 响应 : item_price = {}    （单位:分 → 即 0.60 元）'.format(resp['item_price']))
  print('  本地冻结成本     : frozen_cost = \'0.60\'（单位:元）')
  print('  金额事实：两边一致（0.60 元 == 0.60 元）——但单位不同')

  print('\n[2] 校验层')
  from reconciliation import broken, fixed
  verdict_broken = broken.assert_price_match(resp['item_price'], '0.60')
  verdict_fixed = fixed.assert_price_match(resp['item_price'], '0.60')
  print('  事故版 broken : Decimal(60) == Decimal(0.60) → {} → 该平价样本被误拒'.format(verdict_broken))
  print('    （历史事故中受影响范围为当时全部下单请求，见 EVIDENCE.md A1）')
  print('  修复版 fixed  : 60分 → 归一化 0.60元 == 0.60元 → {} → 订单推进'.format(verdict_fixed))

  print('\n[3] 测试层·事故前的测试组（元值 mock）')
  print(run('test_with_yuan_mocks.py'))
  print('  → 测试全绿，但被测实现是错的：mock 与实现犯了同一个单位假设（同源假绿）')

  print('\n[4] 测试层·修复后的测试组（忠实契约 fixture）')
  print(run('test_with_faithful_fixtures.py'))
  print('  → 同一组业务用例，输入忠实于外部契约后：broken 1/3（唯一「过」的用例是碰巧），fixed 3/3')
  print('  → 测试的牙齿来自「输入忠实于外部契约」，不来自断言数量')

  print('\n[5] 事故后的体系响应（细节见 README 与 EVIDENCE.md）')
  print('  · 防同源假绿约束于事故前已书面化；事故后 trap 正式命名并在后续设计中持续引用')
  print('  · 同族问题系统性排查：事故当天 4 个「真机契约校准」同族修复')
  print('  · 失败案例当场固化为回归条目（evals/），修完必固化')
  print('\n诚实声明：本案例为机制级合成重建，历史证据与合成内容的区分见 EVIDENCE.md')


if __name__ == '__main__':
  main()
