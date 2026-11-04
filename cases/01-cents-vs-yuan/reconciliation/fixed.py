# 校验层·修复版：先归一化单位，再做精确比较
#
# 修复 = 把「单位约定」从隐含假设变成显式代码：
#   ① 入参命名携带单位（channel_item_price_fen / local_frozen_cost_yuan）
#   ② 归一化函数显式换算，边界值有单测（见 tests/test_with_faithful_fixtures.py）
#   ③ 非整数分输入（字段漂移信号）不硬拒，转探查——对应原事故的
#      「非整数分 item_price 走探查不终态」边界处理

from decimal import Decimal, InvalidOperation


class PriceFieldDriftError(Exception):
  """渠道价格字段不可解析/非有限值/非整数分——契约可能漂移，转人工探查"""


def cents_to_yuan(price_fen) -> Decimal:
  """分 → 元 的唯一归一入口（对应原事故修复中的 Formatter.centsToYuan）

  承诺边界：不可解析、非有限值（Infinity/NaN）、非整数分一律转探查；
  本函数不声称处理所有形式的字段漂移（如结构性字段错位）。
  """
  try:
    fen = Decimal(str(price_fen))
  except InvalidOperation:
    raise PriceFieldDriftError('非数值: {}'.format(price_fen))
  if not fen.is_finite():
    raise PriceFieldDriftError('非有限值: {}'.format(price_fen))
  if fen != fen.to_integral_value():
    # 分值出现小数 = 字段漂移信号：不是本函数该裁决的事
    raise PriceFieldDriftError('非整数分: {}'.format(price_fen))
  return fen / 100


def assert_price_match(channel_item_price_fen, local_frozen_cost_yuan) -> bool:
  """归一化后比较：两个金额必须先在同一单位下才能判断相等"""
  return cents_to_yuan(channel_item_price_fen) == Decimal(str(local_frozen_cost_yuan))
