import os
import pickle
import re
import requests

HERE = os.path.abspath(os.path.dirname(__file__))

CoinmarketcapApiUrl = (
    "https://api.coinmarketcap.com/v1/ticker/?convert=CNY&limit=0&convert=USD"
)
CoinmarketcapChatUrl = "https://graphs2.coinmarketcap.com/currencies/{}/{}/{}/"
CoinmarketcapImagePath = os.path.join(HERE, "chatimage")

if not os.path.exists(CoinmarketcapImagePath):
    os.mkdir(CoinmarketcapImagePath)

# 所有的币list


def topxxx(top=30):
    "默认返回前30的币"
    print("get top{} 币".format(top))
    url = "https://api.coinmarketcap.com/v1/ticker/?limit={}".format(top)
    z = requests.get(url)
    top = {i["symbol"]: i["id"] for i in z.json()}
    if "DDD" not in top:
        top["DDD"] = "scryinfo"
    return top


CAPS = topxxx()

HELP_Message = """
币价查询:
1. btc >>> btc价格为$1324.23
2. btc 1d >>> btc1天内价格波动图
3. btc 1w >>> btc1周内价格波动图
4. btc 1m >>>  btc1月内价格波动图
5. btc all >>>  btc当前的情况
            名称：Bitcoin
            总市值：163198616004 $
            市值排名：1
            对 USD 价:9692.0 $
            对 CNY 价：61004.394368 RMB
            对 BTC 价：1.0
            总供应量：21000000.0
            流通量：16838487.0
            24h 交易量：7195430000.0
            24h 波动：-5.04%
            7d 波动：-15.18%
5. topx  >>>按照价格返回前xx币
综合市值排名前x：
1. BTC：$234,322,324,233.22 (-12.25%)
2. ETH：$234,322,324,233.22 (-12.25%)
3. XRP：$234,322,324,233.22 (-12.25%)
"""

patterns1 = "^" + "$|^".join(CAPS.keys()) + "$"
patterns2 = "^" + "$|^".join([i + " (all|1[dmw])" for i in CAPS.keys()]) + "$"
patterns = [patterns1, patterns2]
coinquery = re.compile("|".join(patterns), re.I)

patterns3 = "^top(\d+)"
topx = re.compile(patterns3, re.I)

TOKEN = "370611738:AAHZWg0JQsuF154ltAf_V1U8DeSTPFEXU8c"


# 卡牌查询参数与接口
# 所有英雄的名字
with open("nameAndNickname.pk", "rb") as f:
    NameAndNickname = pickle.load(f)

# 名字和id的对应关系
with open("nameVid.pk", "rb") as f:
    NamevId = pickle.load(f)

RpcUrl = "https://node.web3api.com/"

# 方法的前缀
Fid = "0xb9186d7d"

# 正则匹配
cryptoHero_re = re.compile("^" + "$|^".join(NameAndNickname))
