import requests
import arrow

from decimal import Decimal
import matplotlib

# fix ubuntu no display name and no $DISPLAY environment variable
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os

from config import (
    CoinmarketcapApiUrl,
    CoinmarketcapChatUrl,
    CoinmarketcapImagePath,
    CAPS,
)
from config import RpcUrl, Fid

from functools import wraps
from beaker.cache import cache_regions, cache_region

# configure regions
cache_regions.update(
    {
        "short_term": {"expire": 60 * 5, "type": "memory"},
        "topx": {"expire": 60 * 60 * 24, "type": "memory"},
        "cryptohero": {"expire": 60 * 60 * 24, "type": "memory"},
    }
)


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return getinstance


@cache_region("short_term")
def chart(t, b):
    print("get chat {},{}".format(t, b))
    b = CAPS[b.upper()]
    now = arrow.now().timestamp * 1000
    if t == "1d":
        label = "1 Days"
        before = arrow.now().shift(days=-1).timestamp * 1000
    elif t == "1m":
        label = "1 Months"
        before = arrow.now().shift(months=-1).timestamp * 1000
    elif t == "1w":
        label = "1 Weeks"
        before = arrow.now().shift(days=-7).timestamp * 1000
    url = CoinmarketcapChatUrl.format(b, before, now)
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8",
        "cache-control": "max-age=0",
        "dnt": "1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    }
    z = requests.get(url, headers=headers, verify=False)
    if z.ok:
        x, y = [], []
        for i in z.json()["price_usd"]:
            x.append(i[0])
            y.append(i[1])

        fig = plt.figure()
        ax = plt.subplot(111)
        ax.plot(x, y, label="{} Charts ~{}".format(b, label))
        ax.legend()
        save_path = os.path.join(CoinmarketcapImagePath, "{}_{}.png".format(b, now))
        fig.savefig(save_path)
        return save_path
    else:
        return ""


# @singleton
class coinmarketcap:

    def __init__(self):
        self.apiurl = CoinmarketcapApiUrl

    @cache_region("short_term")
    def get_all_coinmarketcap(self):
        print("get source page")
        z = requests.get(self.apiurl)
        # 去除掉有price_btc 为Null的情况
        # l = [i for i in z.json() if i['price_btc']]
        # return sorted(l, key=itemgetter('price_btc'), reverse=True)
        return z.json()

    def getCoinmarketcap(self, ticker_id, all=False):
        ticker_id = ticker_id.lower()
        Coinmarketcaps = self.get_all_coinmarketcap()
        for i in Coinmarketcaps:
            if i["symbol"].lower() == ticker_id:
                if not all:
                    return "{}价格为${}".format(ticker_id, format2x(i["price_usd"]))
                else:
                    return self.formatmsg(i)
        return "{} 币没有找到...".format(ticker_id)

    def getTopCoinmarketcap(self, top):
        top = int(top)
        if top > 50:
            return ""
        msg = "综合市场排名前{}\n".format(top)
        for i, t in enumerate(self.get_all_coinmarketcap()[:top]):
            msg += "{}. {}:${:,} ({}%) \n".format(
                i,
                t["symbol"],
                format2x(t["market_cap_usd"]),
                format2x(t["percent_change_24h"]),
            )
        return msg

    def formatmsg(self, r):
        "格式化输出"
        return """{}当前的情况:
名称：{}
总市值：{} $
市值排名：{}
对 USD 价:{} $
对 CNY 价：{} RMB
对 BTC 价：{}
总供应量：{}
流通量：{}
24h 交易量：{}
24h 波动：{}%
7d 波动：{}%""".format(
            r["name"],
            r["name"],
            format2x(r["market_cap_usd"]),
            r["rank"],
            format2x(r["price_usd"]),
            format2x(r["price_cny"]),
            r["price_btc"],
            r["max_supply"],
            r["total_supply"],
            format2x(r["24h_volume_usd"]),
            format2x(r["percent_change_24h"]),
            format2x(r["percent_change_7d"]),
        )


def format2x(s):
    "把金额格式化成两位小数"
    if s:
        if isinstance(s, int) or isinstance(s, str):
            s = str(s)
        return Decimal(s).quantize(Decimal("0.00"))
    else:
        return ""


@cache_region("cryptohero")
def getprice(itemid):
    "根根itemid获取价格"
    itemid = "{:0>64}".format(hex(int(itemid)).replace("0x", ""))
    jsdata = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [
            {
                "to": "0xd0792ac0de7ef31197c5f452b21a34389ecc725f",
                "data": "{}{}".format(Fid, itemid),
            },
            "latest",
        ],
    }
    z = requests.post(RpcUrl, json=jsdata)
    result = int(z.json()["result"], 16)
    return result
