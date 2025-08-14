import SwiftUI

struct ContentView: View {
    @StateObject private var storyService = StoryService()
    @State private var selectedGenre = "fantasy"
    @State private var selectedDifficulty = "medium"
    @State private var currentSessionId: String?
    @State private var showingStory = false
    @State private var genres: [Genre] = []
    @State private var difficulties: [Difficulty] = []
    
    var body: some View {
        NavigationView {
            VStack(spacing: 30) {
                // Header
                VStack(spacing: 10) {
                    Text("NarrativeForge")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .foregroundColor(.primary)
                    
                    Text("⚔️ Forge your own unique adventure!")
                        .font(.title2)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(.top, 50)
                
                Spacer()
                
                // Story Creation Form
                VStack(spacing: 25) {
                    // Genre Selection
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Choose Your Genre")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        Picker("Genre", selection: $selectedGenre) {
                            ForEach(genres) { genre in
                                Text(genre.name).tag(genre.id)
                            }
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        
                        if let selectedGenreObj = genres.first(where: { $0.id == selectedGenre }) {
                            Text(selectedGenreObj.description)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.leading)
                        }
                    }
                    
                    // Difficulty Selection
                    VStack(alignment: .leading, spacing: 10) {
                        Text("Choose Difficulty")
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        Picker("Difficulty", selection: $selectedDifficulty) {
                            ForEach(difficulties) { difficulty in
                                Text(difficulty.name).tag(difficulty.id)
                            }
                        }
                        .pickerStyle(SegmentedPickerStyle())
                        
                        if let selectedDifficultyObj = difficulties.first(where: { $0.id == selectedDifficulty }) {
                            Text(selectedDifficultyObj.description)
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .multilineTextAlignment(.leading)
                        }
                    }
                }
                .padding(.horizontal, 30)
                
                Spacer()
                
                // Start Adventure Button
                Button(action: startAdventure) {
                    HStack {
                        Image(systemName: "play.fill")
                        Text("Start Adventure")
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(
                        LinearGradient(
                            gradient: Gradient(colors: [Color.blue, Color.purple]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .cornerRadius(15)
                    .shadow(radius: 5)
                }
                .padding(.horizontal, 30)
                .disabled(storyService.isLoading)
                
                // Loading and Error States
                if storyService.isLoading {
                    ProgressView("Creating your adventure...")
                        .padding()
                }
                
                if let errorMessage = storyService.errorMessage {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal, 30)
                }
                
                Spacer()
            }
            .navigationBarHidden(true)
        }
        .onAppear {
            loadGenresAndDifficulties()
        }
        .fullScreenCover(isPresented: $showingStory) {
            if let sessionId = currentSessionId {
                StoryView(sessionId: sessionId)
            }
        }
    }
    
    private func loadGenresAndDifficulties() {
        // Load genres
        storyService.getGenres()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to load genres: \(error)")
                    }
                },
                receiveValue: { genres in
                    self.genres = genres
                }
            )
            .store(in: &storyService.cancellables)
        
        // Load difficulties
        storyService.getDifficulties()
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to load difficulties: \(error)")
                    }
                },
                receiveValue: { difficulties in
                    self.difficulties = difficulties
                }
            )
            .store(in: &storyService.cancellables)
    }
    
    private func startAdventure() {
        storyService.createStory(genre: selectedGenre, difficulty: selectedDifficulty)
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        print("Failed to create story: \(error)")
                    }
                },
                receiveValue: { sessionId in
                    self.currentSessionId = sessionId
                    self.showingStory = true
                }
            )
            .store(in: &storyService.cancellables)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
