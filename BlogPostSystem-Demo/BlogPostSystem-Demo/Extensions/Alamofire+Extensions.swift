//
//  Alamofire+Extensions.swift
//  BlogPostSystem-Demo
//
//  Created by Doyoung Song on 10/3/25.
//

import Foundation

extension URLSession {
    
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
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
        
        print("📡 GraphQL Request:")
        print("   Method: POST")
        print("   URL: \(url.absoluteString)")
        print("   Query: \(query)")
        print("   Status: \(httpResponse.statusCode)")
        if let jsonObject = try? JSONSerialization.jsonObject(with: data),
           let prettyData = try? JSONSerialization.data(withJSONObject: jsonObject, options: .prettyPrinted),
           let prettyString = String(data: prettyData, encoding: .utf8) {
            print("   Response:\n\(prettyString)")
        }
        print("---")
        
        let decoded = try JSONDecoder().decode(GraphQLResponse<T>.self, from: data)
        
        if let data = decoded.data {
            return data
        } else if let errors = decoded.errors {
            throw GraphQLError(errors: errors)
        } else {
            throw NSError(domain: "GraphQL", code: -1)
        }
    }
    
    func requestRestAPI<T: Decodable & Sendable>(url: String) async throws -> T {
        let urlObj = URL(string: url)!
        let (data, response) = try await self.data(from: urlObj)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }
        
        print("📡 REST API Request:")
        print("   Method: GET")
        print("   URL: \(url)")
        print("   Status: \(httpResponse.statusCode)")
        if let jsonObject = try? JSONSerialization.jsonObject(with: data),
           let prettyData = try? JSONSerialization.data(withJSONObject: jsonObject, options: .prettyPrinted),
           let prettyString = String(data: prettyData, encoding: .utf8) {
            print("   Response:\n\(prettyString)")
        }
        print("---")
        
        return try JSONDecoder().decode(T.self, from: data)
    }
}
