# Python Study: 공공 API를 활용한 데이터 수집 및 분석 프로젝트

**"혼자 공부하는 파이썬"** 책의 내용을 기반으로 스터디를 진행하며, 직접 다양한 공공 API를 활용하여 데이터를 수집하고 분석한 실습 프로젝트를 모은 레포지토리입니다.


## 📚 프로젝트 구성

### Chapter 07: 웹 스크래핑을 활용한 주식 데이터 수집 및 분석
- **주요 기술**: Playwright, Pandas, Plotly
- **내용**: 네이버 금융에서 코스피 시가총액 데이터를 웹 스크래핑하고, 시가총액 기반 상위 종목을 분석하여 트리맵으로 시각화
- **추가 미니 프로젝트**: AI 기반 주식 유형 분석기 (Streamlit) - K-Means 클러스터링과 t-SNE를 활용한 주식 그룹화 및 OpenAI GPT를 통한 투자 전략 분석
- **자세한 내용**: [Chapter_07/README.md](./Chapter_07/README.md)

### Chapter 09: 공공 API를 활용한 경제 지표 데이터 수집 및 시각화
- **주요 기술**: Datakart, Pandas, Matplotlib, Seaborn
- **내용**: 한국은행 ECOS API를 활용하여 기준금리, 국고채, 회사채, 코스피지수, 원달러환율 등 경제 지표를 수집하고 시각화
- **자세한 내용**: [Chapter_09/README.md](./Chapter_09/README.md)

### Chapter 10: 금융 API를 활용한 금리 정보 수집 및 문서 생성
- **주요 기술**: Datakart, Pandas, Python-docx, Matplotlib
- **내용**: 금융감독원 FSS API와 한국은행 ECOS API를 활용하여 금융 상품 정보 및 금리 데이터를 수집하고, Word 문서로 자동 생성
- **추가 미니 프로젝트**: GitHub Actions를 활용한 금융권 채용 공고 자동 업데이트 시스템
- **자세한 내용**: [Chapter_10/README.md](./Chapter_10/README_PROJECT.md)

### Chapter 11: 공공 API를 활용한 부동산 데이터 분석 및 지도 시각화
- **주요 기술**: Datakart, Geopandas, Pandas, Matplotlib, Seaborn
- **내용**: 공공데이터포털 API를 활용하여 서울시 아파트 실거래가 데이터를 수집하고, 자치구별 단위 면적당 평균 가격, 거래 빈도, 가격 변동률을 지도 위에 단계 구분도로 시각화
- **자세한 내용**: [Chapter_11/README.md](./Chapter_11/README.md)



## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/10mm-notebook/python-study.git
cd python-study
```

### 2. 가상 환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. Playwright 브라우저 설치 (Chapter 7 실행 시 필요)

```bash
playwright install chromium
```

## 📦 주요 패키지

이 프로젝트에서 사용하는 주요 패키지들:

- **데이터 수집**: `playwright`, `datakart`, `requests`
- **데이터 처리**: `pandas`, `numpy`
- **데이터 시각화**: `plotly`, `matplotlib`, `seaborn`, `geopandas`
- **머신러닝**: `scikit-learn`
- **웹 애플리케이션**: `streamlit`
- **AI/LLM**: `openai`
- **문서 생성**: `python-docx`
- **파일 처리**: `openpyxl`
- **기타**: `python-dotenv`, `tqdm`, `kaleido`

전체 패키지 목록은 [requirements.txt](./requirements.txt)를 참고하세요.

## ⚙️ 환경 변수 설정

각 챕터의 프로젝트를 실행하기 전에 `.env` 파일을 생성하고 필요한 API 키를 설정해야 합니다.

### Chapter 7 (미니프로젝트)
```env
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

### Chapter 9
```env
ECOS_KEY="YOUR_ECOS_API_KEY"
```

### Chapter 10
```env
FSS_KEY="YOUR_FSS_API_KEY"
ECOS_KEY="YOUR_ECOS_API_KEY"
```

### Chapter 11
```env
DATAGO_KEY="YOUR_DATAGO_API_KEY"
SGIS_KEY="YOUR_SGIS_API_KEY"
SGIS_SECRET="YOUR_SGIS_API_SECRET"
```

### API 키 발급 사이트
- **OpenAI API**: [OpenAI Platform](https://platform.openai.com/api-keys) (Chapter 7 미니프로젝트)
- **ECOS API**: [한국은행 경제통계시스템](https://ecos.bok.or.kr/)
- **FSS API**: [금융감독원 공공데이터포털](https://www.fss.or.kr/)
- **공공데이터포털**: [data.go.kr](https://www.data.go.kr/)
- **통계지리정보서비스**: [SGIS](https://sgis.kostat.go.kr/)

## 📖 사용 방법

각 챕터의 README 파일에서 상세한 실행 방법을 확인할 수 있습니다:

- [Chapter 07 실행 방법](./Chapter_07/README.md#실행-순서)
- [Chapter 07 미니프로젝트 실행 방법](./Chapter_07/README.md#미니프로젝트-ai-기반-주식-유형-분석기-apppy)
- [Chapter 09 실행 방법](./Chapter_09/README.md#실행-순서)
- [Chapter 10 실행 방법](./Chapter_10/README_PROJECT.md#실행-순서)
- [Chapter 11 실행 방법](./Chapter_11/README.md#실행-순서)

## 📝 참고사항

- 이 프로젝트는 학습 목적으로 작성되었습니다.
- API 호출 시 일일 제한이 있을 수 있으니 주의하세요.
- 웹 스크래핑 시 해당 웹사이트의 이용약관을 준수해야 합니다.
- 각 챕터의 프로젝트는 독립적으로 실행할 수 있습니다.