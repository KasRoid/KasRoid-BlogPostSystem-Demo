# GraphQL API Examples

This file contains example GraphQL queries you can run against the API.

**GraphQL Playground**: Open http://localhost:5001/graphql in your browser to use the interactive GraphQL Playground.

---

## Basic Queries

### 1. Get Posts (Simple)

Get a list of posts with only the fields you need:

```graphql
query {
  posts(limit: 5) {
    data {
      id
      title
    }
  }
}
```

### 2. Get Posts with Author (Nested Query)

Get posts and include author information in a single request:

```graphql
query {
  posts(limit: 5) {
    data {
      id
      title
      author {
        name
        email
      }
    }
  }
}
```

### 3. Get Posts with Pagination

Request specific page with pagination metadata:

```graphql
query {
  posts(page: 2, limit: 3) {
    data {
      id
      title
    }
    pagination {
      page
      limit
      total
      totalPages
    }
  }
}
```

---

## Advanced Queries

### 4. Search Posts

Search for posts containing specific keywords:

```graphql
query {
  posts(search: "Python", limit: 5) {
    data {
      title
      content
      author {
        name
      }
    }
  }
}
```

### 5. Sorted Posts

Get posts sorted by title in ascending order:

```graphql
query {
  posts(sortBy: "title", order: "asc", limit: 5) {
    data {
      id
      title
      createdAt
    }
  }
}
```

### 6. Get Single User

Get a specific user by ID:

```graphql
query {
  user(id: 1) {
    name
    email
  }
}
```

### 7. Get User with Posts (Solves N+1 Problem)

Get user information and their posts in a single request:

```graphql
query {
  user(id: 1) {
    name
    email
    posts(limit: 5) {
      title
      createdAt
    }
  }
}
```

### 8. Get All Users with Their Posts (Most Powerful)

This query demonstrates GraphQL's biggest advantage - getting all users and each user's posts in **ONE request**. With REST API, this would require 4 requests (1 for users + 3 for each user's posts).

```graphql
query {
  users {
    id
    name
    email
    posts(limit: 3) {
      id
      title
      createdAt
    }
  }
}
```

---

## Field Selection Examples

One of GraphQL's key advantages is that the client can request only the fields they need, reducing data transfer.

### 9. Minimal Data (Only IDs and Titles)

```graphql
query {
  posts(limit: 10) {
    data {
      id
      title
    }
  }
}
```

### 10. Complete Post Information

```graphql
query {
  posts(limit: 5) {
    data {
      id
      title
      content
      authorId
      createdAt
      author {
        id
        name
        email
      }
    }
  }
}
```

---

## Comparison: REST vs GraphQL

### Scenario: Get all users with their 3 most recent posts

**REST API** (Multiple Requests):
```bash
# Request 1: Get all users
GET /users

# Request 2: Get user 1's posts
GET /users/1/posts?limit=3

# Request 3: Get user 2's posts
GET /users/2/posts?limit=3

# Request 4: Get user 3's posts
GET /users/3/posts?limit=3

# Total: 4 HTTP requests
```

**GraphQL** (Single Request):
```graphql
query {
  users {
    name
    posts(limit: 3) {
      title
    }
  }
}

# Total: 1 HTTP request
```

**Benefits**:
- 75% reduction in HTTP requests (4 → 1)
- Lower latency (fewer round trips)
- Reduced data transfer (only requested fields)
- Simpler client code

---

## Testing with curl

You can test GraphQL queries from the command line:

```bash
# Simple query
curl -X POST http://localhost:5001/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ posts(limit: 2) { data { id title } } }"}'

# Query with variables (more complex)
curl -X POST http://localhost:5001/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetPosts($limit: Int!) { posts(limit: $limit) { data { title } } }",
    "variables": { "limit": 5 }
  }'
```

---

## Field Naming Convention

GraphQL uses camelCase for field names:

- `createdAt` (not `created_at`)
- `authorId` (not `author_id`)
- `sortBy` (not `sort_by`)
- `totalPages` (not `total_pages`)

This is automatically handled by Strawberry GraphQL.

---

## Error Handling

GraphQL will return helpful error messages:

```graphql
# Invalid field name
query {
  posts {
    data {
      invalid_field  # Will return error
    }
  }
}

# Response:
{
  "errors": [
    {
      "message": "Cannot query field 'invalid_field' on type 'Post'."
    }
  ]
}
```

---

## Next Steps

1. Open http://localhost:5001/graphql in your browser
2. Try the queries above in the GraphQL Playground
3. Explore the auto-complete features (press Ctrl+Space)
4. View the schema documentation in the Playground (Docs tab)
5. Compare the network traffic with REST API calls
