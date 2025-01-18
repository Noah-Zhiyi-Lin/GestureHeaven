from flask import Flask, render_template, Response, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import cv2
import mediapipe as mp
import numpy as np
import os
import base64
import random
from gesture_recognizer import Gesture_Recognizer
from pathlib import Path

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")


PREDEFINED_GESTURES = {
    "open": {
        "cn_name": "张开手掌",
        "description": "五指张开，掌心向前",
        "image": "张开手掌手机.png"
    },
    "claw": {
        "cn_name": "爪子",
        "description": "五指向下卷，掌心向前，作猫爪状",
        "image": "爪子.png"
    },
    "fist": {
        "cn_name": "拳头",
        "description": "握紧拳头",
        "image": "拳头.png"
    },
    "ok": {
        "cn_name": "OK",
        "description": "大拇指和食指形成圆圈，其他手指伸直",
        "image": "ok手势.png"
    },
    "yeah": {
        "cn_name": "Yeah",
        "description": "伸出食指和中指，做V字手势",
        "image": "Yeah手势.png"
    },
    "thumb": {
        "cn_name": "点赞",
        "description": "竖起大拇指，其他手指握拳",
        "image": "点赞手势.png"
    },
    "rock": {
        "cn_name": "脑瓜崩",
        "description": "大拇指与中指相连，欲弹出中指",
        "image": "脑瓜崩手势.png"
    },
    "index": {
        "cn_name": "按压食指",
        "description": "大拇指按住食指，其余手指放松",
        "image": "按压食指手势.png"
    },
    "pinky": {
        "cn_name": "按压小指",
        "description": "大拇指按住小拇指，其余手指放松",
        "image": "按压小指手势.png"
    },
    "together": {
        "cn_name": "五指并起",
        "description": "五指伸直并拢",
        "image": "五指并起手势.png"
    },
    "six": {
        "cn_name": "六",
        "description": "伸出大拇指和小指，其余手指紧握",
        "image": "六手势.png"
    },
    "c": {
        "cn_name": "C",
        "description": "手指弯曲成C形状",
        "image": "c手势.png"
    },
    "love": {
        "cn_name": "比心",
        "description": "大拇指和食指交叉，呈现心形",
        "image": "比心手势.png"
    }
}

# 游戏状态
class GameState:
    def __init__(self):
        self.difficulty = "medium"  # 初始难度为中等
        self.initial_time = 6.0  # 初始倒计时时间
        self.time_left = self.initial_time  # 当前倒计时时间
        self.gestures = list(PREDEFINED_GESTURES.keys())  # 所有手势，使用英文名称字典的键
        self.previous_gestures = []  # 已经出现过的手势
        self.current_gesture = None  # 当前需要做的手势
        self.completed_gestures = 0  # 已完成的手势数量
        self.game_over = False  # 游戏是否结束
        self.score = 0  # 玩家分数
        self.total_rounds = 8 # 一局总轮数

    def start_game(self):
        self.time_left = self.initial_time
        self.previous_gestures = []
        self.completed_gestures = 0
        self.game_over = False
        self.score = 0
        self.select_gesture()

    def select_gesture(self):
        # 从还未出现过的手势中随机选择一个
        available_gestures = [gesture for gesture in self.gestures if gesture not in self.previous_gestures]
        if available_gestures:
            self.current_gesture = random.choice(available_gestures)
            self.previous_gestures.append(self.current_gesture)
            return True
        else:
            return False

    def update_round_time(self):
        # 更新关卡时长
        reduction_factor = {
            "easy": 0,
            "medium": 0.2,
            "hard": 0.3
        }
        reduction = reduction_factor[self.difficulty] * self.initial_time
        self.time_left = max(self.initial_time - reduction, 1.0)  # 最短不少于1秒
        self.initial_time = self.time_left

    def next_round(self):
        self.completed_gestures += 1
        if self.completed_gestures >= self.total_rounds:
            self.game_over = True
            return False
        if self.select_gesture():
            return True
        else:
            self.game_over = True
            return False

    def check_gesture(self, recognized_gesture):    # 当手势正确且存在未选择的动作时，返回True
        if recognized_gesture == self.current_gesture:
            self.score += 1
            self.update_round_time()
            return self.next_round()    #进入下一关的入口一：手势正确
        return False


def create_gesture_image(gesture_name, width=800, height=600):
    gesture_data = PREDEFINED_GESTURES[gesture_name]
    # 返回图片的URL路径而不是图片内容
    return f'/static/poses/{gesture_data["image"]}'


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    emit('game_state', {
        'difficulty': game_state.difficulty,
        'current_gesture': game_state.current_gesture,
        'roundtime': game_state.initial_time,
        'score': game_state.score
    })


@socketio.on('set_difficulty')
def handle_difficulty(data):
    game_state.difficulty = data['difficulty']
    emit('difficulty_set', {'difficulty': game_state.difficulty})


@socketio.on('start_game')
def handle_start_game():
    game_state.start_game()
    image_url = create_gesture_image(game_state.current_gesture)
    chinese_gesture_name = PREDEFINED_GESTURES[game_state.current_gesture]["cn_name"]
    emit('gesture_changed', {
        'gesture': f"{chinese_gesture_name} - {PREDEFINED_GESTURES[game_state.current_gesture]['description']}",
        'image': image_url,
        'progress': f'{game_state.completed_gestures + 1}/ {game_state.total_rounds}',
        'roundtime': game_state.initial_time,
        'score': game_state.score
    })

@socketio.on('time_out')
def handle_time_out():
    #game_state.update_round_time()  # 若保留此行，则超时也会缩短下一关时长
    if game_state.next_round(): # 进入下一关的入口二：超时，此时不会缩短下一关时长
        image_url = create_gesture_image(game_state.current_gesture)
        chinese_gesture_name = PREDEFINED_GESTURES[game_state.current_gesture]["cn_name"]
        emit('gesture_changed', {
            'gesture': f"{chinese_gesture_name} - {PREDEFINED_GESTURES[game_state.current_gesture]['description']}",
            'image': image_url,
            'progress': f'{game_state.completed_gestures + 1}/ {game_state.total_rounds}',
            'roundtime': game_state.initial_time,
            'score': game_state.score
        })

    if game_state.game_over:    # 如果游戏结束
        emit('game_over', {
            'score': game_state.score
        })


@socketio.on('frame')
def handle_frame(data):
    # 解码Base64图像
    try:
        image_data = base64.b64decode(data['frame'].split(',')[1])
        frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将图像转换为灰度图
        print("图像解码成功")  # 添加日志输出
    except Exception as e:
        print(f"图像解码失败: {e}")
        return  # 退出函数，避免后续处理错误帧

    # 处理帧并使用模型进行手势识别
    try:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = g_recognizer.classify_image(mp_image)
    except Exception as e:
        print(f"手势识别失败: {e}")
        return  # 退出函数，避免后续处理错误的结果
    
    if result:
        if game_state.check_gesture(result):
            image_url = create_gesture_image(game_state.current_gesture)
            chinese_gesture_name = PREDEFINED_GESTURES[game_state.current_gesture]["cn_name"]
            emit('gesture_changed', {
                'gesture': f"{chinese_gesture_name} - {PREDEFINED_GESTURES[game_state.current_gesture]['description']}",
                'image': image_url,
                'progress': f'{game_state.completed_gestures + 1}/{game_state.total_rounds}',
                'roundtime': game_state.initial_time,
                'score': game_state.score
            })


    if game_state.game_over:  # 如果游戏结束
        emit('game_over', {
            'score': game_state.score
        })


@socketio.on('game_over')
def handle_game_over():
    # 游戏结束时发送总分
    emit('game_over', {
        'score': game_state.score
    })


if __name__ == '__main__':
    # 检查证书文件是否存在
    cert_path = os.path.abspath("ssl/cert.pem")
    key_path = os.path.abspath("ssl/key.pem")

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("SSL证书不存在，正在生成...")
        from generate_cert import generate_self_signed_cert

        generate_self_signed_cert()
        
    # 获取当前文件的路径
    current_dir = Path(__file__).resolve().parent
    # 构建相对路径
    model_path = current_dir / 'gesture_recognizer.task'
    # 检查模型文件是否存在  # 修改部分：检查模型文件
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件未找到: {model_path}")
    
    g_recognizer = Gesture_Recognizer(model_path)
    
    game_state = GameState()

    socketio.run(
        app,
        host='127.0.0.1',
        port=5002,
        certfile=cert_path,
        keyfile=key_path,
        debug=True,
        allow_unsafe_werkzeug=True
    )