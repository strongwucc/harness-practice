# 契约模拟层：第三方渠道与本方系统的金额单位约定
#
# 本文件是对真实事故机制的合成重建（非实测渠道报文）：
#   原事故发生在 PHP/Laravel 栈（渠道契约按分传递、本地按元记账、bccomp 直接比较），
#   本重建以 Python 表达同一机制——契约失真与语言无关。
#
# 单位约定（事故的核心就在这两行）：
#   渠道侧：金额字段按「分」传递（int，如 60 = 0.60 元）
#   本地侧：冻结成本按「元」记账（字符串/Decimal，如 '0.60'）

from decimal import Decimal


# 渠道 render 响应的合成 fixture——模拟「渠道按分返回」的外部契约。
# 注意：这是对契约结构的抽象，不是任何真实渠道的报文。
def channel_render_response(item_price_yuan: str) -> dict:
  """渠道 render 接口的合成响应。

  参数用元值便于构造场景，返回值忠实模拟渠道行为：按分回传。
  仅接受可精确转为整数分的金额（两位小数）——可整除性是渠道契约的一部分，
  fixture 不能静默截断（0.605 元悄悄变 0.60 元本身就是本案例批判的错误形态）。
  """
  price_fen = Decimal(item_price_yuan) * 100
  if price_fen != price_fen.to_integral_value():
    raise ValueError('fixture 仅接受可精确转为整数分的金额: {}'.format(item_price_yuan))
  return {
    'item_price': int(price_fen),  # 单位：分（渠道契约）
    'currency': 'CNY',
  }


# 本地冻结成本的合成数据——模拟「本方按元记账」。
def local_frozen_cost(cost_yuan: str) -> str:
  """本方下单时冻结的供应商成本（单位：元，字符串保持与事故一致的表示）"""
  return cost_yuan
