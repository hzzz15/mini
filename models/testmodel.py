# 토크나이저 및 모델 로드
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# KoBERT 토크나이저와 모델 로드
tokenizer = AutoTokenizer.from_pretrained("monologg/kobert", trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained("rkdaldus/ko-sent5-classification")

# 사용자 입력 텍스트 감정 분석
text = "오늘 미니 프로젝트 발표날이야 일주일동안 잠도 못자고 드디어 끝난다 휴~"
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    outputs = model(**inputs)
predicted_label = torch.argmax(outputs.logits, dim=1).item()

# 감정 레이블 정의
emotion_labels = {
    0: ("Angry", "😡"),
    1: ("Fear", "😨"),
    2: ("Happy", "😊"),
    3: ("Tender", "🥰"),
    4: ("Sad", "😢")
}

# 예측된 감정 출력
print(f"예측된 감정: {emotion_labels[predicted_label][0]} {emotion_labels[predicted_label][1]}")
