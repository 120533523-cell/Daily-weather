import requests
import os
import time

# 从环境变量读取配置
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
TEMPLATE_ID = os.getenv("TEMPLATE_ID")
OPEN_ID = os.getenv("OPEN_ID")
WEATHER_KEY = os.getenv("WEATHER_KEY")
CITY_ID = os.getenv("CITY_ID")

# 获取微信access_token
def get_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    res = requests.get(url).json()
    return res.get("access_token")

# 获取天气数据
def get_weather():
    url = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"
    res = requests.get(url).json()
    if res["code"] == "200":
        now = res["now"]
        return {
            "date": time.strftime("%Y-%m-%d"),
            "city": "你所在的城市", # 可替换为API返回的城市名
            "weather": now["text"],
            "temp": now["temp"],
            "tip": "天冷加衣，天热避暑哦😘" # 自定义小贴士
        }
    return None

# 发送模板消息
def send_msg(token, data):
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={token}"
    payload = {
        "touser": OPEN_ID,
        "template_id": TEMPLATE_ID,
        "data": {
            "date": {"value": data["date"]},
            "city": {"value": data["city"]},
            "weather": {"value": data["weather"]},
            "temp": {"value": data["temp"]},
            "tip": {"value": data["tip"]}
        }
    }
    res = requests.post(url, json=payload).json()
    print("推送结果：", res)

if __name__ == "__main__":
    token = get_token()
    weather = get_weather()
    if token and weather:
        send_msg(token, weather)
