# 네이버 오픈 API 개발 가이드 및 반응형 대시보드 구축 참조 문서

본 문서는 안티그래비티 IDE 환경에서 파이썬(Python) 기반 반응형 대시보드를 개발할 때 참조할 수 있도록 네이버 오픈 API의 비로그인 인증 체계, 검색 API(쇼핑 검색 중심), 데이터랩 API(통합검색어 및 쇼핑인사이트)의 명세와 파이썬 구현 코드를 상세히 정리한 기술 가이드입니다.

---

## 1. 네이버 오픈 API 인증 및 개발 가이드

### 1.1 네이버 오픈 API 분류
네이버 오픈 API는 사용자 인증 필요 여부에 따라 **로그인 방식**과 **비로그인 방식**으로 구분됩니다.

| 구분 | 인증 방식 | 주요 전달 파라미터 | 사용 목적 및 대상 API |
| :--- | :--- | :--- | :--- |
| **비로그인 방식 API** | 클라이언트 ID/Secret 인증 | HTTP 요청 헤더 (`X-Naver-Client-Id`, `X-Naver-Client-Secret`) | 네이버 로그인 없이 오픈 API 호출 가능. <br>• 검색 API (쇼핑, 뉴스, 블로그, 이미지, 책, 카페글 등)<br>• 데이터랩 API (통합검색어 트렌드, 쇼핑인사이트)<br>• 캡차 API (이미지/음성), 네이버 공유하기, 네이버 오픈메인 |
| **로그인 방식 API** | 네이버 로그인 (OAuth 2.0) | 접근 토큰 (Access Token) | 네이버 회원 계정 연동 및 사용자 권한 필요 기능. <br>• 네이버 로그인 회원 프로필 조회<br>• 카페 가입 및 글쓰기 API<br>• 캘린더 일정 등록 API |

---

### 1.2 비로그인 방식 API 특징 및 인증 헤더
- **인증 메커니즘**: 네이버 개발자 센터에서 애플리케이션 등록 시 발급되는 `Client ID`와 `Client Secret`을 HTTP 요청 헤더에 포함하여 호출합니다.
- **주요 인증 헤더 명세**:
  - `X-Naver-Client-Id`: 애플리케이션 등록 시 발급받은 클라이언트 아이디 값
  - `X-Naver-Client-Secret`: 애플리케이션 등록 시 발급받은 클라이언트 시크릿 값
- **API 사용량 합산**: API 일일 사용량 및 호출 한도는 클라이언트 아이디별로 합산 관리됩니다.
- **계정 보안 및 권한**: 애플리케이션을 등록한 네이버 아이디는 '관리자' 권한을 가지므로 보안 유지가 필수적이며, 기업/단체 개발 시 **네이버 단체 회원 계정** 이용을 권장합니다.

---

### 1.3 애플리케이션 등록 및 사전 준비 절차
1. **개발자 센터 접속**: 네이버 개발자 센터 로그인 후 `Application > 애플리케이션 등록` 메뉴 선택.
2. **이용약관 및 계정 등록**: 약관 동의 및 휴대폰 본인 인증(최초 1회), 담당자/회사 정보 입력.
3. **애플리케이션 세부 정보 입력**:
   - **애플리케이션 이름**: 최대 40자 설정.
   - **사용 API 선택**: 사용하고자 하는 서비스 API 선택 (예: `검색`, `데이터랩 (쇼핑인사이트)` 등).
   - **비로그인 오픈 API 서비스 환경**: 웹(Web) URL, 안드로이드/iOS 패키지명 등 서비스 환경 등록.
4. **인증키 확인**: 등록 완료 후 `Application > 내 애플리케이션 > 개요` 탭에서 발급된 `Client ID` 및 `Client Secret` 수집.

---

## 2. 네이버 검색 API (쇼핑 검색) 상세 명세

### 2.1 쇼핑 검색 API 개요
- **설명**: 네이버 검색의 쇼핑 검색 결과를 XML 또는 JSON 형식으로 반환하는 RESTful API입니다.
- **일일 호출 한도**: 25,000회 / 일 (검색 API 공통)
- **프로토콜 및 HTTP 메서드**: `HTTPS` / `GET`
- **요청 엔드포인트 URL**:
  - `JSON` 반환: `https://openapi.naver.com/v1/search/shop.json`
  - `XML` 반환: `https://openapi.naver.com/v1/search/shop.xml`

---

### 2.2 요청 파라미터 (Query String)
검색어와 검색 조건 파라미터를 쿼리 스트링(Query String) 형태로 전달합니다.

| 파라미터명 | 타입 | 필수 여부 | 기본값 / 허용 범위 | 상세 설명 |
| :--- | :--- | :---: | :--- | :--- |
| `query` | String | **Y** | - | 검색어. 반드시 **UTF-8**로 URL 인코딩되어야 합니다. |
| `display` | Integer | N | 기본값 `10` (최대 `100`) | 한 번에 표시할 검색 결과 개수입니다. |
| `start` | Integer | N | 기본값 `1` (최대 `1000`) | 검색 시작 위치(페이지네이션 시작 인덱스)입니다. |
| `sort` | String | N | 기본값 `sim` | 검색 결과 정렬 기준:<br>• `sim`: 정확도순 내림차순<br>• `date`: 날짜순 내림차순<br>• `asc`: 가격순 오름차순<br>• `dsc`: 가격순 내림차순 |
| `filter` | String | N | 설정 안 함 | 검색 결과 상품 유형 필터링:<br>• `naverpay`: 네이버페이 연동 상품만 포함 |
| `exclude` | String | N | 설정 안 함 | 제외할 상품 유형 (`exclude={option}:{option}` 형태로 설정):<br>• `used`: 중고 상품 제외<br>• `rental`: 렌탈 상품 제외<br>• `cbshop`: 해외직구/구매대행 제외 (예: `exclude=used:cbshop`) |

---

### 2.3 응답 필드 명세 (JSON 기준)

| 속성명 (JSON) | 타입 | 설명 |
| :--- | :--- | :--- |
| `lastBuildDate` | dateTime / String | 검색 결과를 생성한 시간 |
| `total` | Integer | 검색 조건에 해당하는 총 검색 결과 개수 |
| `start` | Integer | 현재 검색 시작 위치 |
| `display` | Integer | 한 번에 표시된 검색 결과 개수 |
| `items` | Array(JSON) | 개별 상품 검색 결과 목록 배열 |
| `items[].title` | String | 상품 이름 (검색어와 일치하는 부분은 `<b>` 태그로 감싸짐) |
| `items[].link` | String | 상품 정보 페이지 URL |
| `items[].image` | String | 상품 썸네일 이미지 URL |
| `items[].lprice` | Integer | 최저가 (최저가 정보/가격비교 데이터 없으면 0 반환 또는 상품 가격) |
| `items[].hprice` | Integer | 최고가 (최고가 정보/가격비교 데이터 없으면 0 반환) |
| `items[].mallName` | String | 판매 쇼핑몰 이름 (쇼핑몰 정보 없으면 '네이버' 반환) |
| `items[].productId` | Integer | 네이버 쇼핑 상품 ID |
| `items[].productType` | Integer | 상품군 및 상품 종류에 따른 타입 코드 (하단 참조) |
| `items[].maker` | String | 제조사 이름 |
| `items[].brand` | String | 브랜드 이름 |
| `items[].category1` | String | 상품 카테고리 대분류 |
| `items[].category2` | String | 상품 카테고리 중분류 |
| `items[].category3` | String | 상품 카테고리 소분류 |
| `items[].category4` | String | 상품 카테고리 세분류 |

#### 상품군 타입 (`productType`) 코드표
| 상품군 | 가격비교 상품 | 가격비교 비매칭 일반 | 가격비교 매칭 일반 |
| :--- | :---: | :---: | :---: |
| **일반상품** | `1` | `2` | `3` |
| **중고상품** | `4` | `5` | `6` |
| **단종상품** | `7` | `8` | `9` |
| **판매예정상품** | `10` | `11` | `12` |

---

### 2.4 검색 API 오류 코드
| 오류 코드 | HTTP 상태 코드 | 오류 메시지 | 설명 및 조치 방법 |
| :--- | :---: | :--- | :--- |
| `SE01` | 400 | Incorrect query request | API 요청 URL, 프로토콜, 파라미터 구성 오류 확인 |
| `SE02` | 400 | Invalid display value | `display` 파라미터 값 범위(1~100) 확인 |
| `SE03` | 400 | Invalid start value | `start` 파라미터 값 범위(1~1000) 확인 |
| `SE04` | 400 | Invalid sort value | `sort` 파라미터 오타 확인 (`sim`, `date`, `asc`, `dsc`) |
| `SE05` | 404 | Invalid search api | 요청 URL 경로 오타 확인 |
| `SE06` | 400 | Malformed encoding | 검색어 인코딩을 UTF-8로 변환 필요 |
| `SE99` | 500 | System Error | 네이버 시스템 내부 오류 (개발자 포럼 신고) |
| `-` | **403** | API 권한 없음 | 내 애플리케이션 > API 설정 탭에서 '검색' API 선택 여부 확인 |

---

## 3. 네이버 데이터랩(DataLab) API 상세 명세

### 3.1 데이터랩 API 특징 및 일일 한도
- **일일 호출 한도**: 1,000회 / 일 (쇼핑인사이트 API)
- **데이터 산출 방식**: absolute(절댓값)가 아닌 **상대적 비율(ratio)** 제공.
  - 요청한 기간 중 검색/클릭 횟수가 가장 높은 시점의 값을 **100**으로 두고, 나머지를 상대적인 수치(0~100)로 변환하여 제공합니다.
- **프로토콜 및 HTTP 메서드**: `HTTPS` / `POST`
- **Content-Type**: `application/json`

---

### 3.2 쇼핑인사이트 엔드포인트 라우팅 및 카테고리 ID
#### 엔드포인트 목록
1. **분야별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/categories`
2. **분야 내 기기별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/device`
3. **분야 내 성별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/gender`
4. **분야 내 연령별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/age`
5. **키워드별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/keywords`
6. **키워드 기기별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/keyword/device`
7. **키워드 성별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/keyword/gender`
8. **키워드 연령별 트렌드**: `https://openapi.naver.com/v1/datalab/shopping/category/keyword/age`

#### 쇼핑 분야 코드 (`cat_id`) 확인 방법
네이버쇼핑 카테고리 페이지 URL의 `cat_id` 파라미터 수치를 사용합니다.
- 예: `https://search.shopping.naver.com/search/category.nhn?cat_id=50000805` -> `cat_id` = **`50000805`** (패션의류 > 여성의류 > 니트/스웨터)

---

### 3.3 요청 JSON 구조 및 주요 파라미터

| 필드명 | 타입 | 필수 여부 | 허용 값 및 설명 |
| :--- | :--- | :---: | :--- |
| `startDate` | String | **Y** | 조회 시작 날짜 (`yyyy-mm-dd` 형식, 2017년 8월 1일부터 조회 가능) |
| `endDate` | String | **Y** | 조회 종료 날짜 (`yyyy-mm-dd` 형식) |
| `timeUnit` | String | **Y** | 구간 단위: `date` (일간), `week` (주간), `month` (월간) |
| `category` | Array(JSON) / String | **Y** | 분야 정보. 단일 카테고리 코드 또는 `[{"name": "분야명", "param": ["cat_id"]}]` 배열 (최대 3개) |
| `keyword` | Array(JSON) / String | 필수(키워드 API) | 키워드 정보. `[{"name": "그룹명", "param": ["키워드"]}]` 배열 (최대 5개) 또는 키워드 문자열 |
| `device` | String | N | 기기 조건: 설정 안 함(전체), `pc` (PC), `mo` (모바일) |
| `gender` | String | N | 성별 조건: 설정 안 함(전체), `m` (남성), `f` (여성) |
| `ages` | Array(String) | N | 연령대 조건: `["10", "20", "30", "40", "50", "60"]`<br>• `10`: 10~19세, `20`: 20~29세, `30`: 30~39세, `40`: 40~49세, `50`: 50~59세, `60`: 60세 이상 |

---

### 3.4 응답 JSON 구조

```json
{
  "startDate": "2017-08-01",
  "endDate": "2017-09-30",
  "timeUnit": "month",
  "results": [
    {
      "title": "패션의류",
      "category": ["50000000"],
      "data": [
        {
          "period": "2017-08-01",
          "ratio": 84.01252
        },
        {
          "period": "2017-09-01",
          "ratio": 100.0
        }
      ]
    }
  ]
}
```

---

## 4. 안티그래비티 IDE 연동을 위한 파이썬(Python) 대시보드 개발 가이드

안티그래비티 IDE(Anti-Gravity IDE)에서 파이썬 데이터 프레임워크(예: Streamlit, Dash)를 활용하여 네이버 오픈 API 기반 반응형 대시보드를 구축할 때 참조 가능한 래퍼 클래스 및 데이터 가공 가이드입니다.

### 4.1 네이버 Open API 통합 파이썬 Client 모듈 코드

```python
import os
import json
import urllib.request
import urllib.parse
import pandas as pd

class NaverOpenAPIClient:
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.environ.get("NAVER_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("NAVER_CLIENT_SECRET", "")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("X-Naver-Client-Id 및 X-Naver-Client-Secret 설정이 필요합니다.")

    def _get_headers(self, content_type: str = "application/json"):
        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": content_type
        }

    def search_shopping(self, query: str, display: int = 20, start: int = 1, sort: str = "sim") -> pd.DataFrame:
        base_url = "https://openapi.naver.com/v1/search/shop.json"
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort
        }
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, headers=self._get_headers())
        
        try:
            with urllib.request.urlopen(request) as response:
                res_code = response.getcode()
                if res_code == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    items = data.get("items", [])
                    df = pd.DataFrame(items)
                    if not df.empty:
                        df['clean_title'] = df['title'].str.replace('<b>', '', regex=False).str.replace('</b>', '', regex=False)
                        df['lprice'] = pd.to_numeric(df['lprice'], errors='coerce')
                        df['hprice'] = pd.to_numeric(df['hprice'], errors='coerce')
                    return df
                else:
                    raise Exception(f"API Error Code: {res_code}")
        except Exception as e:
            print(f"쇼핑 검색 API 호출 실패: {e}")
            return pd.DataFrame()

    def get_shopping_category_trend(self, start_date: str, end_date: str, time_unit: str, categories: list, device: str = "", gender: str = "", ages: list = None) -> pd.DataFrame:
        url = "https://openapi.naver.com/v1/datalab/shopping/categories"
        body_dict = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "category": categories
        }
        if device: body_dict["device"] = device
        if gender: body_dict["gender"] = gender
        if ages: body_dict["ages"] = ages
        
        body = json.dumps(body_dict).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=self._get_headers())
        
        try:
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 200:
                    res_json = json.loads(response.read().decode('utf-8'))
                    records = []
                    for result in res_json.get("results", []):
                        title = result.get("title")
                        for d in result.get("data", []):
                            records.append({
                                "category_title": title,
                                "period": d.get("period"),
                                "ratio": d.get("ratio")
                            })
                    return pd.DataFrame(records)
                else:
                    raise Exception(f"HTTP Error: {response.getcode()}")
        except Exception as e:
            print(f"데이터랩 쇼핑인사이트 API 호출 실패: {e}")
            return pd.DataFrame()


if __name__ == "__main__":
    CLIENT_ID = "YOUR_CLIENT_ID"
    CLIENT_SECRET = "YOUR_CLIENT_SECRET"
    
    client = NaverOpenAPIClient(CLIENT_ID, CLIENT_SECRET)
    
    shopping_df = client.search_shopping(query="캠핑용품", display=5)
    print("=== 쇼핑 검색 결과 DataFrame ===")
    print(shopping_df[['clean_title', 'lprice', 'mallName', 'category1']])
    
    trend_df = client.get_shopping_category_trend(
        start_date="2023-01-01",
        end_date="2023-12-31",
        time_unit="month",
        categories=[{"name": "패션의류", "param": ["50000000"]}, {"name": "화장품/미용", "param": ["50000002"]}],
        device="mo",
        gender="f"
    )
    print("\n=== 쇼핑인사이트 카테고리 트렌드 DataFrame ===")
    print(trend_df.head())
```

---

### 4.2 대시보드 개발 시 구현 권장사항
1. **API 호출 캡슐화 및 예외 처리**:
   - `400` Error 발생 시 파라미터 인코딩(`UTF-8`) 및 입력범위(`display`: 1~100, `start`: 1~1000)를 사전에 가리키는 유효성 검사 적용.
   - `403` Error 발생 시 네이버 개발자 센터 내 해당 애플리케이션의 API 권한 설정 체크 안내 UI 구성.
2. **데이터 전처리 및 시각화**:
   - **검색 결과**: `title` 속성의 `<b>`, `</b>` 태그를 정규식으로 제거 후 청정 텍스트로 가공. `lprice` 데이터를 수치화하여 가격 분포 히스토그램 및 쇼핑몰별 가격 비교 차트 생성.
   - **데이터랩 트렌드**: `ratio` 값은 절댓값이 아닌 상대적 지수(0~100)이므로, 시각화 시 Y축 라벨을 '상대적 검색/클릭 지수(MAX=100)'로 명확히 표시하여 오해 소지를 방지.
3. **캐싱(Caching) 및 쿼터 절감**:
   - 데이터랩 API 호출 한도(일 1,000회)와 쇼핑 검색 한도(일 25,000회)를 고려하여, 동일 파라미터 요청에 대해 파이썬 메모리 캐시(`functools.lru_cache` 또는 Streamlit `@st.cache_data`)를 활용하여 API 호출을 최적화.
