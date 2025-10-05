//
//  ContentView.swift
//  BlogPostSystem-Demo
//
//  Created by Doyoung Song on 10/3/25.
//

import SwiftUI

struct ContentView: View {
    
    @ObservedObject var viewModel = ContentViewModel()
    
    var body: some View {
        VStack {
            buttonsView
            Divider()
            postsView
        }
        .padding()
    }
}

extension ContentView {
    
    private var postsView: some View {
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
            .padding(.vertical, 4)
        }
    }
    
    private var buttonsView: some View {
        HStack(spacing: 16) {
            Button("REST API") {
                viewModel.requestRestAPI()
            }
            Button("GraphQL") {
                viewModel.requestGraphQL()
            }
            Button("Reset") {
                viewModel.reset()
            }
        }
    }
}

#Preview {
    ContentView()
}
