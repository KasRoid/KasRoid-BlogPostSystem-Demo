# REST API와 GraphQL을 이용한 게시글 목록 조회 기능 구현

**Date**: 2025-09-30
**Category**: Backend Development / API Design

---

## 📋 Overview

REST API와 GraphQL을 비교하며 게시글 조회 시스템을 구현하는 과제.

모든 기능을 반드시 구현할 필요는 없으며, 시간과 역량에 따라 가능한 부분까지 구현.

---

## 🎯 Required Features

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

```
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
