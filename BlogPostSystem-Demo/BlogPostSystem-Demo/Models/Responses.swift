//
//  Responses.swift
//  BlogPostSystem-Demo
//
//  Created by Doyoung Song on 10/5/25.
//

import Foundation

struct GraphQLResponse<T: Decodable & Sendable>: Decodable, Sendable {
    let data: T?
    let errors: [GraphQLErrorDetail]?
}

struct GraphQLErrorDetail: Decodable, Sendable {
    let message: String
}

struct GraphQLError: Error, Sendable {
    let errors: [GraphQLErrorDetail]
}

nonisolated struct User: Decodable, Sendable {
    let email: String
    let id: Int
    let name: String
}

nonisolated struct Post: Decodable, Sendable {
    let author: User
    let content: String
    let id: Int
    let title: String
}

nonisolated struct PostsResponse: Decodable, Sendable {
    let posts: [Post]
    let total: Int
    let user: User
}

nonisolated struct UsersResponse: Decodable, Sendable {
    let data: [User]
    let total: Int
}

nonisolated struct GraphQLPostsResponse: Decodable, Sendable {
    let users: [GraphQLUser]
    
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
    
    nonisolated struct GraphQLUser: Decodable, Sendable {
        let email: String
        let name: String
        let posts: [GraphQLPost]
    }
    
    nonisolated struct GraphQLPost: Decodable, Sendable {
        let id: Int
        let title: String
        let content: String
    }
}
