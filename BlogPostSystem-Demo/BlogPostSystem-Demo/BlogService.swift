//
//  BlogService.swift
//  BlogPostSystem-Demo
//
//  Created by Doyoung Song on 10/3/25.
//

import Alamofire
import Foundation

struct BlogService {
    
    func requestAllUsers() async throws -> UsersResponse {
        try await URLSession.shared.requestRestAPI(url: "http://localhost:5001/users")
    }
    
    func requestPosts(by user: User) async throws -> PostsResponse {
        try await URLSession.shared.requestRestAPI(url: "http://localhost:5001/users/\(user.id)/posts?limit=3")
    }
    
    func requestUsersAndPosts() async throws -> GraphQLPostsResponse {
        try await URLSession.shared.requestGraphQL(
            query: """
            query
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
            """
        )
    }
}
