import SwiftUI

struct StoryView: View {
    let sessionId: String
    @StateObject private var storyService = StoryService()
    @State private var storyState: StoryState?
    @State private var storyHistory: [StorySegment] = []
    @Environment(\.presentationMode) var presentationMode
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Navigation Bar
                HStack {
                    Button(action: {
                        presentationMode.wrappedValue.dismiss()
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .font(.title2)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Text("NarrativeForge")
                        .font(.headline)
                        .fontWeight(.semibold)
                    
                    Spacer()
                    
                    Button(action: showHistory) {
                        Image(systemName: "clock.arrow.circlepath")
                            .font(.title2)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color(.systemBackground))
                .shadow(radius: 1)
                
                // Story Content
                ScrollView {
                    VStack(spacing: 20) {
                        // Story History
                        if !storyHistory.isEmpty {
                            VStack(alignment: .leading, spacing: 15) {
                                ForEach(storyHistory) { segment in
                                    StorySegmentView(segment: segment, isHistory: true)
                                }
                            }
                            .padding(.horizontal)
                        }
                        
                        // Current Story Segment
                        if let currentState = storyState {
                            StorySegmentView(segment: currentState.currentSegment, isHistory: false)
                                .padding(.horizontal)
                        }
                        
                        // Loading State
                        if storyService.isLoading {
                            LoadingView()
                                .padding()
                        }
                        
                        // Error State
                        if let errorMessage = storyService.errorMessage {
                            Text(errorMessage)
                                .foregroundColor(.red)
                                .font(.caption)
                                .multilineTextAlignment(.center)
                                .padding()
                        }
                    }
                    .padding(.vertical)
                }
            }
            .navigationBarHidden(true)
        }
        .onAppear {
            loadStoryState()
        }
    }
    
    private func loadStoryState() {
        storyService.getStoryState(sessionId: sessionId)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to load story state: \(error)")
                    }
                },
                receiveValue: { state in
                    self.storyState = state
                    self.storyHistory = state.storyHistory
                }
            )
            .store(in: &storyService.cancellables)
    }
    
    private func showHistory() {
        // This could show a modal with full story history
        print("Show history tapped")
    }
}

struct StorySegmentView: View {
    let segment: StorySegment
    let isHistory: Bool
    @StateObject private var storyService = StoryService()
    
    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            // Story Text
            Text(segment.text)
                .font(.body)
                .foregroundColor(.primary)
                .lineSpacing(4)
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color(.systemGray6))
                )
            
            // Location and Mood (if available)
            if let location = segment.location, let mood = segment.mood {
                HStack {
                    Label(location, systemImage: "location.fill")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Label(mood.capitalized, systemImage: moodIcon(for: mood))
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding(.horizontal)
            }
            
            // Choices (only for current segment)
            if !isHistory && !segment.choices.isEmpty {
                VStack(spacing: 10) {
                    Text("What will you do?")
                        .font(.headline)
                        .foregroundColor(.primary)
                    
                    ForEach(Array(segment.choices.enumerated()), id: \.element.id) { index, choice in
                        ChoiceButton(
                            choice: choice,
                            isSelected: false,
                            action: {
                                makeChoice(index: index)
                            }
                        )
                        .disabled(storyService.isLoading)
                    }
                }
                .padding(.top, 10)
            }
        }
    }
    
    private func makeChoice(index: Int) {
        // This would need to be connected to the parent view's session ID
        // For now, just print the choice
        print("Made choice: \(segment.choices[index].text)")
    }
    
    private func moodIcon(for mood: String) -> String {
        switch mood.lowercased() {
        case "tense", "scary":
            return "exclamationmark.triangle.fill"
        case "cheerful", "happy":
            return "sun.max.fill"
        case "mysterious":
            return "questionmark.circle.fill"
        default:
            return "circle.fill"
        }
    }
}

struct StoryView_Previews: PreviewProvider {
    static var previews: some View {
        StoryView(sessionId: "preview-session")
    }
}
