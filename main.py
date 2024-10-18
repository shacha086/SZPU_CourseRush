import requests
import json
import random
import time
import toml
from concurrent.futures import ThreadPoolExecutor, as_completed

# 从配置文件载入配置
def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return toml.load(file)

# 配置和 URL
config = load_config("config.toml")
courses = config.get("courses", [])
token = config.get("token")
use_multithreading = config.get("use_multithreading", False)  # 控制是否启用多线程

list_url = "https://jwxk.shu.edu.cn/xsxk/elective/shu/clazz/list"
add_url = "https://jwxk.shu.edu.cn/xsxk/elective/shu/clazz/add"

# 随机 User-Agent 列表
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36"
]

headers = {"Authorization": token}

# 查询并尝试选课的任务函数
def query_and_add_course(course):
    KCH = course.get("KCH")
    JSH = course.get("JSH")
    class_type = course.get("class_type", "XGKC")

    # 准备查询数据
    list_data = {
        "teachingClassType": class_type,
        "pageNumber": 1,
        "pageSize": 10,
        "KCH": KCH,
        "JSH": JSH
    }

    # 设置随机 User-Agent
    headers["User-Agent"] = random.choice(user_agents)

    # 发送课程查询请求
    response = requests.post(list_url, headers=headers, data=list_data)

    if response.status_code == 200:
        print(f"查询课程成功: 课程号 {KCH}")
        response_data = response.json()

        if "data" in response_data and "list" in response_data["data"]:
            rows = response_data["data"]["list"].get("rows", [])

            for row in rows:
                class_capacity = row.get("classCapacity")
                number_of_selected = row.get("numberOfSelected")
                clazz_id = row.get("JXBID")
                secret_val = row.get("secretVal")

                print(f"课程 {KCH} 容量: {class_capacity}, 已选人数: {number_of_selected}")

                # 判断是否可以选课
                if number_of_selected < class_capacity:
                    add_data = {
                        "clazzType": class_type,
                        "clazzId": clazz_id,
                        "secretVal": secret_val
                    }

                    # 发送选课请求
                    add_response = requests.post(add_url, headers=headers, data=add_data)

                    if add_response.status_code == 200:
                        print(f"课程 {KCH} 添加成功!")
                        print("响应内容:", add_response.text)
                        return True  # 成功选课后返回
                    else:
                        print(f"课程 {KCH} 添加失败，状态码: {add_response.status_code}")
                else:
                    print(f"课程 {KCH} 已满，继续尝试...")
    else:
        print(f"查询课程失败，状态码: {response.status_code}")
    return False

# 多线程查询和选课逻辑
def query_courses_multithread():
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(query_and_add_course, course) for course in courses]
        for future in as_completed(futures):
            if future.result():  # 如果成功选课，停止进一步尝试
                return True
    return False

# 单线程查询和选课逻辑
def query_courses_singlethread():
    for course in courses:
        if query_and_add_course(course):
            return True  # 成功选课后停止尝试
    return False

# 主函数，根据配置选择单线程或多线程模式
def main():
    attempt = 0
    while True:
        attempt += 1
        print(f"第 {attempt} 次尝试...")

        # 根据配置选择执行模式
        success = (
            query_courses_multithread()
            if use_multithreading
            else query_courses_singlethread()
        )

        if success:
            print(f"抢课成功! 第 {attempt} 次尝试")
            break

        # 随机延时避免频繁请求
        delay = random.uniform(0.5, 1)
        print(f"延时: {delay:.2f} 秒")
        time.sleep(delay)

# 程序入口
if __name__ == "__main__":
    main()
