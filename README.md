# Blog API Server - REST & GraphQL

iOS 앱 연동을 위한 로컬 백엔드 서버 (REST API & GraphQL)

**Date**: 2025-10-03
**Category**: Backend Development / API Design

---

## 📋 Overview

REST API와 GraphQL의 차이점을 체감할 수 있는 블로그 시스템 백엔드입니다.

**주요 기능**:

- REST API와 GraphQL API 동시 제공
- SQLite 데이터베이스 (파일 기반, Docker 불필요)
- 페이지네이션, 정렬, 검색 기능
- CORS 지원 (iOS 앱 연동)

**기술 스택**:

- Python 3.13+
- Flask (REST API)
- Strawberry GraphQL
- SQLite

---

## 🚀 서버 실행 방법

### 1단계: 가상환경 생성 및 활성화

```bash
# 가상환경 생성 (최초 1회만)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate
```

### 2단계: 패키지 설치

```bash
# 필요한 패키지 설치
pip install flask strawberry-graphql flask-cors
```

### 3단계: 데이터베이스 초기화

```bash
# SQLite 데이터베이스 생성 및 샘플 데이터 삽입
python init_db.py
```

**출력 예시**:

```text
==================================================
Database Initialization Started
==================================================
✓ Connected to database: blog.db
✓ Created 'users' table
✓ Created 'posts' table
✓ Inserted 3 users into database
✓ Inserted 15 posts into database
==================================================
Database Initialization Completed Successfully!
==================================================
```

### 4단계: 서버 실행

```bash
# Flask 서버 시작
python app.py
```

**출력 예시**:

```text
======================================================================
Blog API Server - REST + GraphQL
======================================================================

Server starting...

REST API Endpoints:
  - Root:        http://localhost:5001/
  - Posts:       http://localhost:5001/posts
  - Users:       http://localhost:5001/users
  - Health:      http://localhost:5001/health

GraphQL Endpoint:
  - GraphQL:     http://localhost:5001/graphql
  - Playground:  Open http://localhost:5001/graphql in browser

Press CTRL+C to stop the server
======================================================================

 * Running on http://127.0.0.1:5001
```

**서버 종료**: 터미널에서 `Ctrl + C`

---

## 📡 API 사용 방법

### REST API 예제

**게시글 목록 조회** (페이지네이션, 정렬, 검색):

```bash
curl "http://localhost:5001/posts?page=1&limit=10&sort=created_at&order=desc&search=Python"
```

**사용자 정보 조회**:

```bash
curl "http://localhost:5001/users/1"
```

**사용자 게시글 조회**:

```bash
curl "http://localhost:5001/users/1/posts?limit=3"
```

**모든 사용자 목록**:

```bash
curl "http://localhost:5001/users"
```

### GraphQL API 예제

**브라우저에서 테스트**:

1. 브라우저에서 `http://localhost:5001/graphql` 접속
2. GraphQL Playground에서 쿼리 실행

**예제 쿼리 1** - 게시글 목록:

```graphql
{
  posts(page: 1, limit: 5, sortBy: "created_at", order: "desc") {
    data {
      id
      title
      content
      author {
        name
        email
      }
    }
    pagination {
      page
      total
      totalPages
    }
  }
}
```

**예제 쿼리 2** - 사용자 + 게시글 (N+1 문제 해결):

```graphql
{
  user(id: 1) {
    name
    email
    posts(limit: 3) {
      title
      createdAt
    }
  }
}
```

**예제 쿼리 3** - 모든 사용자 + 게시글 (1회 요청):

```graphql
{
  users {
    name
    email
    posts(limit: 3) {
      title
      createdAt
    }
  }
}
```

**curl로 GraphQL 요청**:

```bash
curl -X POST http://localhost:5001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ posts(limit: 5) { data { id title author { name } } } }"
  }'
```

---

## 🍎 iOS 앱 연동

### 프로젝트 구조

iOS 앱은 다음과 같은 구조로 되어 있습니다:

```text
BlogPostSystem-Demo/
├── Models/
│   └── Responses.swift          # 데이터 모델 정의
├── Extensions/
│   └── Alamofire+Extensions.swift  # URLSession 확장
├── BlogService.swift            # API 서비스 레이어
├── ViewModels/
│   └── ContentViewModel.swift   # 비즈니스 로직
└── ContentView.swift            # UI
```

---

### 1. URLSession 확장 (Alamofire+Extensions.swift)

REST API와 GraphQL 요청을 위한 재사용 가능한 메서드:

```swift
extension URLSession {

    // REST API 요청
    func requestRestAPI<T: Decodable & Sendable>(url: String) async throws -> T {
        let urlObj = URL(string: url)!
        let (data, response) = try await self.data(from: urlObj)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }

    // GraphQL 요청
    func requestGraphQL<T: Decodable & Sendable>(
        query: String,
        variables: [String: Any]? = nil
    ) async throws -> T {
        let parameters: [String: Any] = [
            "query": query,
            "variables": variables ?? [:]
        ]

        let url = URL(string: "http://localhost:5001/graphql")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: parameters)

        let (data, response) = try await self.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        let decoded = try JSONDecoder().decode(GraphQLResponse<T>.self, from: data)

        if let data = decoded.data {
            return data
        } else if let errors = decoded.errors {
            throw GraphQLError(errors: errors)
        } else {
            throw NSError(domain: "GraphQL", code: -1)
        }
    }
}
```

---

### 2. 데이터 모델 (Responses.swift)

```swift
// GraphQL 공통 응답 래퍼
struct GraphQLResponse<T: Decodable & Sendable>: Decodable, Sendable {
    let data: T?
    let errors: [GraphQLErrorDetail]?
}

// 사용자 모델
struct User: Decodable, Sendable {
    let id: Int
    let name: String
    let email: String
}

// 게시글 모델
struct Post: Decodable, Sendable {
    let id: Int
    let title: String
    let content: String
    let author: User
}

// REST API 응답
struct UsersResponse: Decodable, Sendable {
    let data: [User]
    let total: Int
}

struct PostsResponse: Decodable, Sendable {
    let user: User
    let posts: [Post]
    let total: Int
}

// GraphQL 응답
struct GraphQLPostsResponse: Decodable, Sendable {
    let users: [GraphQLUser]

    // GraphQL 응답을 Post 배열로 변환
    var conversion: [Post] {
        users.flatMap { user in
            user.posts.map { post in
                Post(
                    author: User(email: user.email, id: -1, name: user.name),
                    content: post.content,
                    id: post.id,
                    title: post.title
                )
            }
        }
    }

    struct GraphQLUser: Decodable, Sendable {
        let name: String
        let email: String
        let posts: [GraphQLPost]
    }

    struct GraphQLPost: Decodable, Sendable {
        let id: Int
        let title: String
        let content: String
    }
}
```

---

### 3. API 서비스 레이어 (BlogService.swift)

```swift
struct BlogService {

    // REST API: 모든 사용자 조회
    func requestAllUsers() async throws -> UsersResponse {
        try await URLSession.shared.requestRestAPI(
            url: "http://localhost:5001/users"
        )
    }

    // REST API: 특정 사용자의 게시글 조회
    func requestPosts(by user: User) async throws -> PostsResponse {
        try await URLSession.shared.requestRestAPI(
            url: "http://localhost:5001/users/\(user.id)/posts?limit=3"
        )
    }

    // GraphQL: 모든 사용자 + 게시글 한 번에 조회
    func requestUsersAndPosts() async throws -> GraphQLPostsResponse {
        try await URLSession.shared.requestGraphQL(
            query: """
            query {
              users {
                name
                email
                posts(limit: 3) {
                  id
                  title
                  content
                }
              }
            }
            """
        )
    }
}
```

---

### 4. ViewModel (ContentViewModel.swift)

```swift
final class ContentViewModel: ObservableObject {

    @Published private(set) var posts: [Post] = []
    private let service = BlogService()

    // REST API: N+1 문제 발생 (여러 번 요청)
    func requestRestAPI() {
        Task { @MainActor in
            do {
                // 1. 모든 사용자 조회
                let users = try await service.requestAllUsers().data

                // 2. 각 사용자의 게시글 개별 조회 (N번 반복)
                var posts: [Post] = []
                for user in users {
                    let response = try await service.requestPosts(by: user)
                    posts.append(contentsOf: response.posts)
                }
                self.posts = posts
            } catch {
                print(error)
            }
        }
    }

    // GraphQL: 단일 요청으로 모든 데이터 조회
    func requestGraphQL() {
        Task { @MainActor in
            do {
                let response = try await service.requestUsersAndPosts()
                self.posts = response.conversion
            } catch {
                print(error)
            }
        }
    }
}
```

---

### 5. UI (ContentView.swift)

```swift
struct ContentView: View {

    @ObservedObject var viewModel = ContentViewModel()

    var body: some View {
        VStack {
            // 버튼
            HStack(spacing: 16) {
                Button("REST API") {
                    viewModel.requestRestAPI()  // N+1 문제 발생
                }
                Button("GraphQL") {
                    viewModel.requestGraphQL()  // 단일 요청
                }
                Button("Reset") {
                    viewModel.reset()
                }
            }

            Divider()

            // 게시글 목록
            List(viewModel.posts, id: \.id) { post in
                VStack(alignment: .leading) {
                    Text(post.title)
                        .font(.headline)
                    Text("by \(post.author.name)")
                        .font(.subheadline)
                    Text(post.content)
                        .font(.body)
                        .lineLimit(2)
                }
            }
        }
        .padding()
    }
}
```

---

### 🎯 핵심 차이점

#### REST API (N+1 문제)

```swift
// 1번: 사용자 조회
GET /users

// N번: 각 사용자의 게시글 조회
GET /users/1/posts?limit=3
GET /users/2/posts?limit=3
GET /users/3/posts?limit=3

// 총 4번의 네트워크 요청 필요
```

#### GraphQL (단일 요청)

```swift
// 1번: 사용자 + 게시글 한 번에 조회
POST /graphql
{
  users {
    name
    email
    posts(limit: 3) {
      id
      title
      content
    }
  }
}

// 총 1번의 네트워크 요청으로 완료
```

---

### 📊 성능 비교 결과

| 항목 | REST API | GraphQL | 개선율 |
|------|----------|---------|--------|
| **네트워크 요청 수** | 4회 | 1회 | **75% 감소** |
| **코드 복잡도** | 높음 (for 루프) | 낮음 (단일 호출) | - |
| **데이터 전송량** | ~4,800 bytes | ~1,200 bytes | **75% 감소** |

---

## 🗂️ 프로젝트 구조

```text
.
├── app.py              # Flask 서버 진입점 (REST + GraphQL)
├── database.py         # SQLite 데이터베이스 헬퍼 함수
├── init_db.py          # 데이터베이스 초기화 스크립트
├── models.py           # 데이터 모델 (User, Post)
├── rest_api.py         # REST API 엔드포인트
├── graphql_api.py      # GraphQL 스키마 및 리졸버
├── blog.db             # SQLite 데이터베이스 파일 (자동 생성)
├── venv/               # Python 가상환경 (자동 생성)
└── README.md           # 이 문서
```

---

## 🔍 문제 해결

### 포트 충돌 (Port 5001 already in use)

```bash
# 포트를 사용 중인 프로세스 종료
lsof -ti:5001 | xargs kill -9

# 또는 app.py에서 포트 번호 변경
# app.run(port=5002)
```

### 데이터베이스 초기화 오류

```bash
# blog.db 파일 삭제 후 재실행
rm blog.db
python init_db.py
```

### 패키지 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip

# 패키지 재설치
pip install --force-reinstall flask strawberry-graphql flask-cors
```

---

## 📊 REST vs GraphQL 성능 비교

### 시나리오: 모든 사용자 + 각 사용자의 게시글 3개 조회

#### REST API (N+1 문제):

```bash
# 1. 모든 사용자 조회
GET /users

# 2-4. 각 사용자의 게시글 조회 (3번 반복)
GET /users/1/posts?limit=3
GET /users/2/posts?limit=3
GET /users/3/posts?limit=3

# 총 4회 요청, 약 4,848 bytes
```

#### GraphQL (단일 요청):

```graphql
{
  users {
    name
    posts(limit: 3) {
      title
    }
  }
}

# 총 1회 요청, 약 1,220 bytes
```

#### 성능 개선 결과:

- 요청 횟수: **75% 감소** (4회 → 1회)
- 데이터 전송량: **75% 감소** (4,848 → 1,220 bytes)
- 네트워크 왕복: **75% 감소**

---

## 🎯 Required Features (원본 과제 명세)

### 1. 게시글 목록 조회 (페이지네이션)

#### REST API

- **Endpoint**: `GET /posts?page=1&limit=10`
- **특징**: 항상 동일한 필드 반환 (title, createdAt 등)
- **고정된 응답 구조**

#### GraphQL

- **Query**: 클라이언트가 원하는 필드 선택 가능
- **예시**:
  - `title`, `createdAt`만 요청
  - `content`, `author` 정보까지 요청
- **유연한 응답 구조**

---

### 2. 정렬 기능

**정렬 기준**: 작성일(`createdAt`) 오름차순/내림차순

#### REST API

- **Query Parameter**: `GET /posts?sort=createdAt&order=desc`
- 쿼리 파라미터로 정렬 기준과 순서 지정

#### GraphQL

- **Query Argument**: `posts(sortBy: "createdAt", order: DESC)`
- 쿼리 인자로 정렬 기준과 순서 지정

---

### 3. 검색 기능

**기능**: 특정 키워드를 포함하는 게시글 조회

#### REST API

- **Query Parameter**: `GET /posts?search=keyword`
- 쿼리 파라미터로 검색어 전달

#### GraphQL

- **Query Argument**: `posts(search: "keyword")`
- 검색어를 인자로 받는 쿼리 구현

---

### 4. 관계형 데이터 조회

**기능**: 사용자와 해당 사용자가 작성한 게시글을 함께 조회

#### REST API

- **여러 엔드포인트 호출 필요**:
  1. `GET /users/{id}` - 사용자 정보
  2. `GET /users/{id}/posts` - 해당 사용자의 게시글
- **N+1 문제 발생 가능**

#### GraphQL

- **하나의 쿼리로 해결**:

```graphql
query {
  user(id: 1) {
    id
    name
    posts {
      id
      title
      createdAt
    }
  }
}
```

- **단일 요청으로 중첩 데이터 조회**

---

### 5. 네트워크 요청 비교

**목표**: 동일한 데이터 조회 시 REST vs GraphQL 비교

#### 비교 항목

- **요청 횟수**: REST는 여러 번, GraphQL은 1번
- **응답 크기**: Over-fetching vs 필요한 데이터만
- **네트워크 효율성**: 대역폭, 지연시간

#### 예시 시나리오

모든 사용자와 각 사용자의 게시글 3개씩 조회:

**REST API**:

```text
1. GET /users (모든 사용자)
2. GET /users/1/posts?limit=3
3. GET /users/2/posts?limit=3
4. GET /users/3/posts?limit=3
...
→ N+1 요청 (사용자 수 + 1)
```

**GraphQL**:

```graphql
query {
  users {
    id
    name
    posts(limit: 3) {
      id
      title
    }
  }
}
→ 1번의 요청
```

---

### 6. GraphQL 성능 최적화 (DataLoader 적용)

**문제**: GraphQL의 N+1 문제

#### N+1 문제 확인

- 사용자 목록 조회 (1번 쿼리)
- 각 사용자마다 게시글 조회 (N번 쿼리)
- **총 N+1번의 DB 쿼리 발생**

#### DataLoader 적용

- **배치 처리**: 여러 사용자의 게시글을 하나의 쿼리로 조회
- **캐싱**: 동일 요청 내에서 중복 조회 방지
- **성능 개선**: N+1 → 2번의 쿼리

#### 적용 전후 비교

| 항목           | DataLoader 적용 전 | DataLoader 적용 후 |
| -------------- | ------------------ | ------------------ |
| **DB 쿼리 수** | N+1                | 2                  |
| **응답 속도**  | 느림               | 빠름               |
| **DB 부하**    | 높음               | 낮음               |

---

## 🔑 Key Comparisons

### REST API vs GraphQL

| 구분              | REST API              | GraphQL         |
| ----------------- | --------------------- | --------------- |
| **요청 수**       | 여러 엔드포인트 (N+1) | 단일 요청       |
| **응답 구조**     | 고정 (Over-fetching)  | 클라이언트 정의 |
| **관계 데이터**   | 여러 번 호출          | 중첩 쿼리       |
| **네트워크 효율** | 낮음                  | 높음            |
| **캐싱**          | HTTP 캐싱 용이        | 구현 복잡       |
| **학습 곡선**     | 낮음                  | 높음            |

---

## 📝 Implementation Checklist

- [ ] 1. 게시글 목록 조회 (페이지네이션)
  - [ ] REST API 엔드포인트 구현
  - [ ] GraphQL 쿼리 구현
- [ ] 2. 정렬 기능
  - [ ] REST API 정렬 파라미터
  - [ ] GraphQL 정렬 인자
- [ ] 3. 검색 기능
  - [ ] REST API 검색 파라미터
  - [ ] GraphQL 검색 인자
- [ ] 4. 관계형 데이터 조회
  - [ ] REST API 여러 엔드포인트
  - [ ] GraphQL 중첩 쿼리
- [ ] 5. 네트워크 요청 비교
  - [ ] 요청 횟수 측정
  - [ ] 응답 크기 비교
  - [ ] 결과 문서화
- [ ] 6. DataLoader 적용
  - [ ] N+1 문제 확인
  - [ ] DataLoader 구현
  - [ ] 성능 비교 측정

---

## 🔗 Related Concepts

- **REST API**: Representational State Transfer
- **GraphQL**: Query Language for APIs
- **N+1 Problem**: Database query anti-pattern
- **DataLoader**: Batch loading and caching library
- **Pagination**: Data pagination strategies
- **Over-fetching**: Retrieving more data than needed
- **Under-fetching**: Requiring multiple requests for needed data
