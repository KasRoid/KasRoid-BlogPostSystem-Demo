//
//  ContentViewModel.swift
//  BlogPostSystem-Demo
//
//  Created by Doyoung Song on 10/5/25.
//

import Combine

final class ContentViewModel: ObservableObject {
    
    @Published private(set) var posts: [Post] = []
    
    private let service = BlogService()
    
    func requestRestAPI() {
        Task { @MainActor in
            do {
                let users = try await service.requestAllUsers().data
                
                var posts: [Post] = []
                for user in users {
                    posts.append(contentsOf: try await service.requestPosts(by: user).posts)
                }
                self.posts = posts
            } catch {
                print(error)
            }
        }
    }
    
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
    
    func reset() {
        posts = []
    }
}
