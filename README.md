# 动作模仿游戏 (Web版)

这是一个基于Web的动作模仿游戏，使用摄像头捕捉玩家动作并与示例动作进行比较，根据相似度给出得分。

## 功能特点

- 三种难度级别：简单、适中、困难
- 实时摄像头画面显示
- 实时的手势识别
- 刺激的倒计时系统
- 浏览器访问，无需安装客户端

## 安装要求

1. Python 3.8 或更高版本
2. 摄像头设备
3. 现代浏览器（支持WebRTC）

## 安装步骤

1. 克隆或下载此仓库
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 使用说明

1. 启动服务器：
```bash
python app.py
```

2. 在浏览器中访问：
```
http://localhost:5000
```

3. 在主菜单中：
   - 选择难度级别（简单/适中/困难）
   - 简单：动作时限不会缩短。适中/困难：动作时间逐渐变短
   - 点击"开始游戏"按钮开始游戏
   - 允许浏览器访问摄像头

4. 游戏过程中：
   - 左侧显示示例动作图片
   - 右侧显示玩家实时摄像头画面
   - 底部显示当前进度和倒计时
   - 每个动作有时限，时限会随游戏进行逐渐缩短
   - 系统会判定手势是否正确，规定时间内完成就会得一分

## 游戏规则

1. 每轮游戏包含8个动作，每个动作有一定的完成时限
2. 系统会判定玩家动作是否和示例相同
3. 相同则得分并进入下一个动作，时限内未完成会直接进入下一个动作，不得分
4. 适中和困难难度下，每完成一个动作，时限都会缩短一定比例；若未完成，时限不会缩短
5. 8个动作结束后，将呈现最终得分，尽可能获得高分吧！

## 注意事项

1. 确保摄像头正常工作且未被其他程序占用
2. 保持适当的光线条件以获得更好的识别效果
3. 站在摄像头前保持适当距离（建议1.5-2米）
4. 确保有足够的活动空间
5. 使用支持WebRTC的现代浏览器（如Chrome、Firefox、Edge等）
6. 允许浏览器访问摄像头权限

## 自定义动作

你可以在`static/poses`目录下添加自己的示例动作图片：
1. 支持的图片格式：jpg、png、jpeg
2. 建议图片尺寸：800x600像素
3. 建议使用清晰的人物轮廓图片

## 技术栈

- 后端：Flask + Flask-SocketIO
- 前端：HTML5 + JavaScript
- 计算机视觉：OpenCV + MediaPipe
- 实时通信：WebSocket
- 视频流：WebRTC 