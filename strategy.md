# REST API & GraphQL 간단 구현 전략 (iOS 연동용)

**Date**: 2025-10-03
**Purpose**: iOS 앱과 연동할 로컬 서버 구현을 위한 최소 구성 전략
**Project**: [[REST API & GraphQL 과제]]

---

## 🎯 구현 목표

**핵심**:

- iOS 앱에서 REST API와 GraphQL을 각각 호출하여 차이점 체감
- 최소한의 설정으로 빠르게 구현
- 로컬에서 실행 가능한 간단한 서버
- **Docker 없이 Python 가상환경만으로 실행**

**비교 포인트**:

- 요청 횟수 (REST: N+1회 vs GraphQL: 1회)
- 응답 데이터 크기 (Over-fetching vs 필요한 데이터만)
- 개발 편의성 (여러 엔드포인트 vs 단일 쿼리)

---

## 🛠️ 기술 스택 선택

### 서버: Python (Flask + Strawberry GraphQL)

**선택 이유**:

- Python이 JavaScript보다 설정이 간단함
- Flask는 최소한의 코드로 REST API 구현 가능
- Strawberry는 Python에서 가장 간단한 GraphQL 라이브러리
- 타입 힌트 기반으로 스키마 자동 생성
- **가상환경(venv)만으로 격리된 환경 구성 (Docker 불필요)**

### 데이터베이스: SQLite

**선택 이유**:

- 별도 설치 불필요 (Python 내장)
- 파일 기반으로 관리 간단 (blog.db 파일 하나로 완결)
- 실습용으로 충분한 성능
- 초기화 및 시드 데이터 생성 용이
- **서버형 DB(PostgreSQL/MySQL) 불필요 = Docker 컨테이너 불필요**

### iOS: URLSession + SwiftUI

**역할**:

- REST API 호출: URLSession 사용
- GraphQL 호출: POST 요청으로 쿼리 전송
- 결과 비교 UI 구현

---

## 📋 구현 단계 (6단계)

### STEP 1: 환경 준비 (Docker 없이 로컬 실행)

**목표**: Python 가상환경만으로 격리된 개발 환경 구성

**작업**:

1. Python 가상환경 생성 (`python -m venv venv`)
2. 가상환경 활성화 (`source venv/bin/activate`)
3. 필요한 패키지 설치
   - Flask (REST API 서버)
   - Strawberry-GraphQL (GraphQL 서버)
   - SQLite3 (Python 내장, 별도 설치 불필요)

**Docker를 사용하지 않는 이유**:

- Python 가상환경만으로 충분한 격리 환경 제공
- SQLite는 파일 기반 DB로 컨테이너 불필요
- 로컬에서 바로 실행 가능하여 설정 간단

**완료 기준**:

- 가상환경 활성화됨
- `pip list`에서 Flask, Strawberry 확인
- `python --version` 확인 (3.8 이상 권장)

---

### STEP 2: 데이터베이스 설계 및 초기화

**목표**: SQLite 데이터베이스에 테이블 생성 및 샘플 데이터 입력

**테이블 구조**:

**users 테이블**:

- id (정수, 기본키)
- name (텍스트)
- email (텍스트)

**posts 테이블**:

- id (정수, 기본키)
- title (텍스트)
- content (텍스트)
- author_id (정수, users.id 참조)
- created_at (타임스탬프)

**샘플 데이터**:

- 사용자 3명
- 각 사용자당 게시글 5개 (총 15개)

**완료 기준**:

- `blog.db` 파일 생성됨
- 테이블에 데이터 입력 확인 (SQLite 브라우저 또는 쿼리)

---

### STEP 3: REST API 구현

**목표**: Flask로 게시글 조회 REST API 엔드포인트 구현

**구현할 엔드포인트**:

1. **게시글 목록 조회** (페이지네이션)

   - `GET /posts?page=1&limit=10`
   - 응답: 고정된 JSON 구조 (id, title, content, author, created_at)

2. **정렬 기능**

   - `GET /posts?sort=createdAt&order=desc`
   - created_at 기준 오름차순/내림차순

3. **검색 기능**

   - `GET /posts?search=keyword`
   - title 또는 content에 키워드 포함된 게시글

4. **사용자 정보 조회**

   - `GET /users/{id}`
   - 특정 사용자 정보 반환

5. **사용자 게시글 조회**
   - `GET /users/{id}/posts?limit=3`
   - 특정 사용자의 게시글 목록

**완료 기준**:

- Flask 서버가 `http://localhost:5000`에서 실행됨
- 브라우저 또는 curl로 모든 엔드포인트 테스트 성공
- JSON 응답이 올바르게 반환됨

---

### STEP 4: GraphQL API 구현

**목표**: Strawberry를 사용하여 GraphQL API 구현

**구현할 쿼리**:

1. **게시글 목록 조회** (페이지네이션, 정렬, 검색)

   - Query: `posts(page: Int, limit: Int, sortBy: String, order: String, search: String)`
   - 클라이언트가 원하는 필드만 선택 가능

2. **사용자 정보 조회**

   - Query: `user(id: Int)`
   - 중첩 쿼리로 해당 사용자의 게시글도 함께 조회 가능

3. **중첩 데이터 조회**
   - Query: `users { id, name, posts(limit: 3) { title } }`
   - 한 번의 요청으로 모든 사용자와 각 게시글 조회

**타입 정의**:

- User 타입 (id, name, email, posts)
- Post 타입 (id, title, content, author, createdAt)
- Query 타입 (posts, user, users)

**완료 기준**:

- GraphQL 서버가 `/graphql`에서 실행됨
- GraphQL Playground 또는 브라우저에서 쿼리 테스트 성공
- 필드 선택이 올바르게 동작함 (일부 필드만 요청 시 해당 필드만 반환)

---

### STEP 5: iOS 앱 구현

**목표**: iOS 앱에서 REST와 GraphQL API를 각각 호출하여 비교

**구현할 화면**:

**1. 메인 화면**

- REST API 버튼
- GraphQL 버튼
- 결과 비교 화면으로 이동

**2. REST API 테스트 화면**

- 게시글 목록 표시 (페이지네이션)
- 정렬 옵션 (최신순/오래된순)
- 검색 기능
- 사용자 선택 → 해당 사용자 게시글 조회
- 네트워크 요청 횟수 표시

**3. GraphQL 테스트 화면**

- 동일한 데이터를 GraphQL로 조회
- 필요한 필드만 선택하여 요청
- 네트워크 요청 횟수 표시 (항상 1회)

**4. 비교 화면**

- REST vs GraphQL 요청 횟수 비교
- 응답 데이터 크기 비교
- 응답 시간 비교

**네트워크 구현**:

- REST: URLSession으로 각 엔드포인트 호출
- GraphQL: POST 요청으로 쿼리 전송 (`/graphql`)

**완료 기준**:

- iOS 앱에서 로컬 서버 API 호출 성공
- REST는 여러 번 요청, GraphQL은 1번 요청 확인
- UI에 데이터 올바르게 표시됨

---

### STEP 6: 성능 비교 및 검증

**목표**: REST와 GraphQL의 차이점을 측정하고 문서화

**비교 시나리오**:

**시나리오 1: 게시글 목록 조회**

- REST: `/posts?page=1&limit=10` (1회 요청)
- GraphQL: `posts(page: 1, limit: 10) { id, title }` (1회 요청)
- 비교: 응답 데이터 크기 (GraphQL이 필요한 필드만 반환)

**시나리오 2: 사용자 + 게시글 조회**

- REST:
  1. `/users/1` (사용자 정보)
  2. `/users/1/posts?limit=3` (게시글)
     → 총 2회 요청
- GraphQL:
  ```graphql
  user(id: 1) {
    name
    posts(limit: 3) { title }
  }
  ```
  → 총 1회 요청
- 비교: 요청 횟수 50% 감소

**시나리오 3: 모든 사용자 + 각각 게시글 3개**

- REST:
  1. `/users` (모든 사용자)
  2. `/users/1/posts?limit=3`
  3. `/users/2/posts?limit=3`
  4. `/users/3/posts?limit=3`
     → 총 4회 요청 (N+1 문제)
- GraphQL:
  ```graphql
  users {
    name
    posts(limit: 3) { title }
  }
  ```
  → 총 1회 요청
- 비교: 요청 횟수 75% 감소

**측정 항목**:

- HTTP 요청 횟수
- 응답 데이터 크기 (bytes)
- 응답 시간 (milliseconds)
- Over-fetching 여부 (불필요한 필드 포함)

**완료 기준**:

- iOS 앱에서 각 시나리오별 측정 결과 표시
- REST가 GraphQL보다 요청 횟수가 많음을 확인
- GraphQL이 필요한 데이터만 반환함을 확인
- 결과를 간단한 보고서로 정리

---

## 🎯 필수 구현 vs 선택 구현

### 필수 (실습 목표 달성을 위한 최소 구성)

**REST API**:

- ✅ 게시글 목록 조회 (페이지네이션)
- ✅ 사용자 정보 조회
- ✅ 사용자 게시글 조회

**GraphQL**:

- ✅ 게시글 목록 조회
- ✅ 중첩 쿼리 (user + posts)

**iOS**:

- ✅ REST API 호출 (N+1 시나리오)
- ✅ GraphQL 호출 (단일 쿼리)
- ✅ 요청 횟수 비교 UI

### 선택 (시간 여유 시 추가)

**서버**:

- ⭐ 정렬 기능 (REST, GraphQL)
- ⭐ 검색 기능 (REST, GraphQL)
- ⭐ DataLoader 적용 (GraphQL N+1 DB 쿼리 최적화)

**iOS**:

- ⭐ 정렬/검색 UI
- ⭐ 응답 시간 그래프
- ⭐ 데이터 크기 비교 차트

---

## 📂 프로젝트 구조

### 서버 구조 (Python)

```
blog-api/
├── app.py                 # Flask + GraphQL 서버 엔트리
├── database.py            # SQLite 초기화 및 쿼리 함수
├── rest_api.py            # REST API 엔드포인트
├── graphql_api.py         # GraphQL 스키마 및 리졸버
├── models.py              # User, Post 데이터 모델
├── init_db.py             # 데이터베이스 테이블 생성 및 시드
├── blog.db                # SQLite 데이터베이스 파일
└── requirements.txt       # 패키지 목록
```

### iOS 구조 (SwiftUI)

```
BlogAPIComparison/
├── Models/
│   ├── Post.swift         # Post 데이터 모델
│   └── User.swift         # User 데이터 모델
├── Services/
│   ├── RESTService.swift  # REST API 호출 로직
│   └── GraphQLService.swift # GraphQL 호출 로직
├── Views/
│   ├── MainView.swift     # 메인 화면
│   ├── RESTView.swift     # REST API 테스트 화면
│   ├── GraphQLView.swift  # GraphQL 테스트 화면
│   └── ComparisonView.swift # 비교 결과 화면
└── Utilities/
    └── NetworkMonitor.swift # 요청 횟수/크기 측정
```

---

## 🚀 실행 순서 (Docker 없이 로컬 실행)

### 1. 서버 실행

```bash
# 1. Python 가상환경 생성 및 활성화 (Docker 대신 venv 사용)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# 2. 패키지 설치 (requirements.txt 없이 직접 설치)
pip install flask strawberry-graphql

# 3. 데이터베이스 초기화 (SQLite 파일 생성)
python init_db.py
# → blog.db 파일 생성됨 (컨테이너 볼륨 불필요)

# 4. 서버 실행 (로컬 프로세스로 실행)
python app.py

# → http://localhost:5000 (REST API)
# → http://localhost:5000/graphql (GraphQL)
# → Docker 포트 매핑 불필요, 바로 localhost 접근
```

**로컬 실행의 장점**:

- Docker 이미지 빌드/컨테이너 실행 단계 생략
- 코드 수정 시 즉시 반영 (컨테이너 재시작 불필요)
- 디버깅 간편 (IDE에서 바로 중단점 설정 가능)
- 리소스 사용 최소화

### 2. 서버 테스트

```bash
# REST API 테스트
curl "http://localhost:5000/posts?page=1&limit=5"
curl "http://localhost:5000/users/1"
curl "http://localhost:5000/users/1/posts?limit=3"

# GraphQL 테스트 (브라우저에서)
# http://localhost:5000/graphql 접속
# 쿼리 실행:
# query { posts(page: 1, limit: 5) { id title } }
```

### 3. iOS 앱 실행

1. Xcode에서 프로젝트 열기
2. 시뮬레이터 선택 (iPhone 15 Pro 권장)
3. Run (⌘R)
4. REST/GraphQL 버튼 클릭하여 각각 테스트
5. 요청 횟수 차이 확인

---

## ✅ 검증 체크리스트

### 서버 검증

- [ ] Flask 서버가 정상 실행됨 (`http://localhost:5000`)
- [ ] SQLite DB에 3명의 사용자와 15개의 게시글 존재
- [ ] REST API 엔드포인트 5개 모두 응답 성공
- [ ] GraphQL Playground에서 쿼리 실행 가능
- [ ] 중첩 쿼리 (`user { posts { ... } }`) 정상 동작

### iOS 앱 검증

- [ ] REST API 호출 시 여러 번 요청 발생 (N+1)
- [ ] GraphQL 호출 시 1번 요청으로 모든 데이터 수신
- [ ] 요청 횟수가 UI에 올바르게 표시됨
- [ ] REST와 GraphQL 응답 데이터가 동일한 내용 포함
- [ ] 비교 화면에서 차이점 시각화

### 학습 목표 달성

- [ ] REST API의 Over-fetching 문제 이해
- [ ] REST API의 N+1 요청 문제 체감
- [ ] GraphQL의 단일 요청으로 중첩 데이터 조회 경험
- [ ] GraphQL의 필드 선택 기능 활용
- [ ] 네트워크 효율성 차이 측정 및 비교

---

## 📊 예상 결과

### 시나리오: 모든 사용자 + 각 사용자 게시글 3개 조회

**REST API**:

- HTTP 요청: 4회 (`/users` 1회 + `/users/{id}/posts` 3회)
- 응답 데이터: ~5KB (모든 필드 포함, Over-fetching)
- 응답 시간: ~200ms (로컬이므로 빠름)

**GraphQL**:

- HTTP 요청: 1회
- 응답 데이터: ~2KB (필요한 필드만)
- 응답 시간: ~80ms

**개선율**:

- 요청 횟수: 75% 감소 (4회 → 1회)
- 데이터 크기: 60% 감소 (5KB → 2KB)
- 응답 시간: 60% 개선 (200ms → 80ms)

---

## 🎓 학습 포인트

### REST API 특성

**장점**:

- 구조가 명확하고 이해하기 쉬움
- HTTP 캐싱 활용 가능
- 각 엔드포인트의 역할이 분명함

**단점**:

- 관계형 데이터 조회 시 여러 번 요청 필요 (N+1)
- 고정된 응답 구조로 Over-fetching 발생
- 클라이언트 요구에 맞춘 커스터마이징 어려움

### GraphQL 특성

**장점**:

- 단일 요청으로 복잡한 데이터 조회
- 클라이언트가 필요한 필드만 선택
- Under-fetching/Over-fetching 문제 해결
- 강력한 타입 시스템

**단점**:

- 학습 곡선이 높음
- HTTP 캐싱 활용이 REST보다 복잡
- 서버 측 쿼리 복잡도 제어 필요
- N+1 DB 쿼리 문제 발생 가능 (DataLoader로 해결)

### 실무 적용 시나리오

**REST API가 적합한 경우**:

- 단순한 CRUD 작업
- 캐싱이 중요한 경우
- 팀의 REST 경험이 많은 경우

**GraphQL이 적합한 경우**:

- 복잡한 관계형 데이터 조회
- 모바일 앱 (네트워크 효율성 중요)
- 다양한 클라이언트 요구사항 (Web, iOS, Android)
- 빠른 프로토타이핑

---

## 🔗 참고 자료

- **Flask 공식 문서**: https://flask.palletsprojects.com/
- **Strawberry GraphQL**: https://strawberry.rocks/
- **SQLite**: https://www.sqlite.org/
- **GraphQL 기초**: https://graphql.org/learn/

---

## 📝 다음 단계 (선택)

실습 완료 후 추가로 학습하고 싶다면:

1. **DataLoader 적용** (GraphQL N+1 DB 쿼리 최적화)
2. **Mutation 구현** (게시글 생성/수정/삭제)
3. **Authentication** (JWT 기반 인증)
4. **Subscription** (실시간 데이터 업데이트)
5. **Error Handling** (에러 처리 및 검증)
6. **Unit Testing** (API 테스트 작성)
