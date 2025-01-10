from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
import torch

class SentimentAnalyzer:
    def __init__(self):
        # 모델 설정을 강제로 수정
        config = AutoConfig.from_pretrained("hun3359/mdistilbertV3.1-sentiment", num_labels=3)
        self.tokenizer = AutoTokenizer.from_pretrained("hun3359/mdistilbertV3.1-sentiment")
        
        # 모델 로드 시 크기 불일치 오류 무시
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "hun3359/mdistilbertV3.1-sentiment",
            config=config,
            ignore_mismatched_sizes=True  # 불일치하는 크기 무시
        )
        self.model.eval()  # 평가 모드로 설정

        # 감정 레이블 정의 (Negative, Neutral, Positive)
        self.emotion_labels = ["Negative", "Neutral", "Positive"]

    def analyze_sentiment(self, text: str) -> str:
        # 입력 텍스트가 비어 있는지 확인
        if not text.strip():
            raise ValueError("입력된 텍스트가 비어 있습니다.")

        # KoBERT 입력 데이터 생성
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            max_length=128,
            truncation=True,
            padding="max_length"
        )

        # 디버깅: 토큰화된 입력 확인
        print(f"토큰화된 입력: {inputs}")

        # 모델 추론
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

            # 디버깅: 출력값 확인
            print(f"모델 출력값(Logits): {logits}")
            print(f"Logits 크기: {logits.size()}")  # 출력 텐서 크기 확인

        # 예측 레이블 추출
        if logits.size(0) == 0:
            raise ValueError("모델 출력값이 비어 있습니다.")

        predicted_label = logits.argmax(dim=1).item()
        print(f"예측된 레이블: {predicted_label}")

        # 감정 레이블 반환
        return self.emotion_labels[predicted_label]

# 테스트 코드
if __name__ == "__main__":
    # 감정 분석기 초기화
    analyzer = SentimentAnalyzer()

    # 테스트 입력 문장
    test_text = "오늘 정말 행복한 날이야!"
    
    try:
        # 감정 분석
        result = analyzer.analyze_sentiment(test_text)
        print(f"분석된 감정: {result}")
    except Exception as e:
        print(f"오류 발생: {e}")
