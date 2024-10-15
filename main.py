import requests
import json
import random
import time
import toml

# 从配置文件中载入配置
def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        config = toml.load(file)
    return config


# 查询课程信息的 URL
list_url = "https://jwxk.shu.edu.cn/xsxk/elective/shu/clazz/list"
# 添加课程的 URL
add_url = "https://jwxk.shu.edu.cn/xsxk/elective/shu/clazz/add"

# 从配置文件中读取课程号、教师号和 token
config = load_config("config.toml")
courses = config.get("courses", [])
token = config.get("token")

# 设置请求头，添加随机 User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
]

headers = {
    "Authorization": token
}

# 反复执行抢课的逻辑，直到成功为止
attempt = 0
while True:
    attempt += 1
    for course in courses:
        KCH = course.get("KCH")
        JSH = course.get("JSH")
        class_type = course.get("class_type", "XGKC")

        # 设置查询课程信息的请求数据
        list_data = {
            "teachingClassType": class_type,
            "pageNumber": 1,
            "pageSize": 10,
            "KCH": KCH,
            "JSH": JSH
        }

        # 设置一个随机的 User-Agent
        headers["User-Agent"] = random.choice(user_agents)

        # 发送 POST 请求以获取课程信息
        response = requests.post(list_url, headers=headers, data=list_data)

        # 检查响应状态
        if response.status_code == 200:
            print(f"查询课程请求成功! 第 {attempt} 次请求")

            # 解析响应内容为 JSON
            response_data = response.json()

            # 提取 classCapacity 和 numberOfSelected
            if "data" in response_data and "list" in response_data["data"]:
                rows = response_data["data"]["list"].get("rows", [])
                for row in rows:
                    class_capacity = row.get("classCapacity")
                    number_of_selected = row.get("numberOfSelected")
                    clazz_id = row.get("JXBID")
                    secret_val = row.get("secretVal")

                    print(f"classCapacity: {class_capacity}, numberOfSelected: {number_of_selected}")

                    # 如果选课人数小于课程容量，则执行添加课程请求
                    if number_of_selected > class_capacity:
                        add_data = {
                            "clazzType": class_type,
                            "clazzId": clazz_id,
                            "secretVal": secret_val
                        }

                        # 发送添加课程的请求
                        add_response = requests.post(add_url, headers=headers, data=add_data)

                        # 检查添加课程请求的响应状态
                        if add_response.status_code == 200:
                            print("添加课程请求成功!")
                            print("响应内容:", add_response.text)
                            break  # 抢课成功，退出循环
                        else:
                            print(f"添加课程请求失败，状态码: {add_response.status_code}")
                    else:
                        print("课程已满，继续尝试...")
            else:
                print("未找到所需课程数据!")
        else:
            print(f"查询课程请求失败，状态码: {response.status_code}")

        # 增加随机延时，避免频繁请求
        delay = random.uniform(0.5, 1)
        print(f"延时: {delay:.2f} 秒")
        time.sleep(delay)