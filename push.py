import requests
import json
import time

# 配置信息
APP_ID = "wx327b6cd9766d44a2"
APP_SECRET = "2e736e642a8e828b191a6503b73f7f33"
TEMPLATE_ID = "6CEGeZcG4WeDb3G_YJilDt7pucu1RgsNINdmDIzETA4"
OPEN_ID = "oabUC2eQmtwwHz7RIwZcrjCHg9qA"
WEATHER_KEY = "2a6e1a6ce43d4249af8215792b2bab0d"
CITY_ID = "CN101200103"
# 优先使用开发版域名（确认Key是开发版）
WEATHER_API_URL = f"https://devapi.qweather.com/v7/weather/now?location={CITY_ID}&key={WEATHER_KEY}"

def get_access_token():
    """获取微信公众号access_token"""
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
        response = requests.get(url, timeout=10)
        # 捕获403错误
        if response.status_code == 403:
            print(f"微信API 403错误: {response.text}")
            return None
        response.raise_for_status()
        res = response.json()
        
        access_token = res.get("access_token")
        if not access_token:
            raise Exception(f"获取access_token失败: {res}")
        
        return access_token
    except requests.exceptions.HTTPError as e:
        print(f"微信API HTTP错误: {str(e)}, 响应内容: {response.text}")
        return None
    except Exception as e:
        print(f"获取access_token异常: {str(e)}")
        return None

def get_weather():
    """获取实时天气信息（和风天气API）"""
    try:
        response = requests.get(WEATHER_API_URL, timeout=10)
        # 捕获和风天气403错误
        if response.status_code == 403:
            print(f"和风天气API 403错误: {response.text}")
            print("可能原因：Key无效/IP白名单/调用超限/域名错误")
            return None
        response.raise_for_status()
        res = response.json()
        
        code = res.get("code")
        if code != "200":
            raise Exception(f"天气API返回错误码: {code}, 信息: {res}")
        
        now = res.get("now", {})
        weather_data = {
            "temperature": now.get("temp", "未知"),
            "feels_like": now.get("feelsLike", "未知"),
            "weather": now.get("text", "未知"),
            "wind_dir": now.get("windDir", "未知"),
            "wind_scale": now.get("windScale", "未知"),
            "humidity": now.get("humidity", "未知"),
            "update_time": res.get("updateTime", "未知")
        }
        return weather_data
        
    except requests.exceptions.HTTPError as e:
        print(f"天气API HTTP错误: {str(e)}, 响应内容: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"天气API网络请求失败: {str(e)}")
        return None
    except Exception as e:
        print(f"解析天气数据异常: {str(e)}")
        return None

def push_wechat(access_token, weather_data):
    """推送天气到微信公众号模板消息"""
    if not access_token or not weather_data:
        print("缺少推送必要参数，跳过推送")
        return False
    
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        
        data = {
            "touser": OPEN_ID,
            "template_id": TEMPLATE_ID,
            "url": "",
            "data": {
                "temperature": {"value": weather_data["temperature"] + "℃", "color": "#1E90FF"},
                "feels_like": {"value": weather_data["feels_like"] + "℃", "color": "#FF6347"},
                "weather": {"value": weather_data["weather"], "color": "#32CD32"},
                "wind": {"value": f"{weather_data['wind_dir']} {weather_data['wind_scale']}级", "color": "#9370DB"},
                "humidity": {"value": weather_data["humidity"] + "%", "color": "#4169E1"},
                "update_time": {"value": weather_data["update_time"], "color": "#696969"}
            }
        }
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
            timeout=10
        )
        # 捕获推送403错误
        if response.status_code == 403:
            print(f"微信推送403错误: {response.text}")
            print("可能原因：公众号无模板消息权限/OpenID无效/模板ID错误")
            return False
        response.raise_for_status()
        res = response.json()
        
        if res.get("errcode") == 0:
            print(f"天气推送成功！消息ID: {res.get('msgid')}")
            return True
        else:
            raise Exception(f"推送失败: {res}")
            
    except requests.exceptions.HTTPError as e:
        print(f"微信推送HTTP错误: {str(e)}, 响应内容: {response.text}")
        return False
    except Exception as e:
        print(f"微信推送异常: {str(e)}")
        return False

# 新增：验证OpenID有效性
def check_openid(access_token):
    if not access_token:
        return False
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/user/info?access_token={access_token}&openid={OPEN_ID}&lang=zh_CN"
        response = requests.get(url, timeout=10)
        res = response.json()
        if res.get("errcode") == 40003:
            print(f"❌ OpenID {OPEN_ID} 无效（不属于该公众号）")
            return False
        elif res.get("errcode"):
            print(f"❌ 验证OpenID失败: {res}")
            return False
        else:
            print(f"✅ OpenID {OPEN_ID} 有效")
            return True
    except Exception as e:
        print(f"验证OpenID异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 开始执行天气推送 ===")
    
    # 1. 获取天气数据
    weather = get_weather()
    if not weather:
        print("❌ 获取天气数据失败，程序退出")
        exit(1)
    print(f"✅ 获取天气成功: {weather}")
    
    # 2. 获取微信access_token
    access_token = get_access_token()
    if not access_token:
        print("❌ 获取access_token失败，程序退出")
        exit(1)
    print("✅ 获取access_token成功")
    
    # 3. 验证OpenID
    if not check_openid(access_token):
        print("❌ OpenID无效，程序退出")
        exit(1)
    
    # 4. 推送天气到微信
    push_result = push_wechat(access_token, weather)
    if push_result:
        print("=== ✅ 天气推送任务完成 ===")
    else:
        print("=== ❌ 天气推送任务失败 ===")
        exit(1)
