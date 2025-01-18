import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class Gesture_Recognizer:
    def __init__(self, model_path):
        # 创建手势识别器实例时使用选项
        options = vision.GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
        )
        # 创建分类器
        self.classifier = vision.GestureRecognizer.create_from_options(options)

    def classify_image(self, image):
        """
        对输入的图片进行分类，返回最有可能的结果的名称。

        Args:
            image (str): 图片文件。

        Returns:
            str: 最有可能的类别名称。如果没有识别到手势，返回 "none"。
        """
        # 进行分类
        recognition_result = self.classifier.recognize(image)

        # 找到最有可能的结果
        if recognition_result.gestures:  # 检查是否有识别结果
            top_gesture = max(recognition_result.gestures[0], key=lambda gesture: gesture.score)
            return top_gesture.category_name
        else:
            return "none"