# 校验层·事故版：渠道价格与本地冻结成本的匹配校验
#
# 这就是事故中的写法：直接比较两个数值，没有任何单位归一。
# 事故现场：渠道回 60（分），本地冻结 0.60（元）→ 60 != 0.60 → 全量订单被误拒。

from decimal import Decimal


def assert_price_match(channel_item_price, local_frozen_cost_yuan) -> bool:
  """校验渠道返回价与本地冻结成本是否一致。

  参数 channel_item_price 是渠道契约原样值（按分），本版实现直接按数值比较
  ——隐含假设了「对方按元传」，这个假设没有写在任何地方，直到真机炸掉。
  """
  return Decimal(str(channel_item_price)) == Decimal(str(local_frozen_cost_yuan))
