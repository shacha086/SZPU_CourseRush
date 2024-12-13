# SHU 上海大学抢课助手（2024 新系统）

### 安装与使用

1. **安装依赖库**

   需要使用 `requests` 、 `toml` 、 `glog` 、`websockets`和 `selenium` 库，您可以使用以下命令安装：

   ```sh
   pip install requests toml glog selenium websockets
   ```

2. **配置 `config.toml` 文件**

   创建一个 `config.toml` 文件，并根据以下示例填写内容：

   ```toml
   # 用户认证 token
   use_multithreading = false # 将其更改为 true 来启用多线程
   wait_time = 5.0            # 每次尝试后的等待时间（秒）
   username = "your_username_here"
   password = "your_password_here"
   browser = "edge"  # 可以是 "chrome", "firefox", 或 "edge"

   # 课程信息列表
   [[courses]]
   KCH = "08305014"       # 课程号
   JSH = "1005"           # 教师号

   [[courses]]
   KCH = "08306096"
   JSH = "1007"
   ```

3. **运行脚本**

   在命令行中运行脚本：

   ```sh
   python main.py
   ```

### 使用说明

- 脚本会反复查询课程状态，并在有空位时尝试抢课。
- 脚本会打印每次请求的结果，包括是否成功添加课程。

### 注意事项

- **频率控制**：请勿过于频繁地发送请求，建议使用脚本中的随机延时设置，避免因频繁访问被封禁账号。
- **合法使用**：请遵守学校的选课规定，合理使用此脚本，避免对学校系统造成不必要的负担。
- **风险提示**：使用该脚本存在被学校系统封禁账号的风险，请自行评估并承担相关责任。
