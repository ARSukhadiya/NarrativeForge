import SwiftUI

struct ChoiceButton: View {
    let choice: StoryChoice
    let isSelected: Bool
    let action: () -> Void
    
    @State private var isPressed = false
    
    var body: some View {
        Button(action: {
            withAnimation(.easeInOut(duration: 0.1)) {
                isPressed = true
            }
            
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                withAnimation(.easeInOut(duration: 0.1)) {
                    isPressed = false
                }
                action()
            }
        }) {
            HStack {
                Text(choice.text)
                    .font(.body)
                    .fontWeight(.medium)
                    .foregroundColor(isSelected ? .white : .primary)
                    .multilineTextAlignment(.leading)
                    .lineLimit(nil)
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(isSelected ? .white.opacity(0.8) : .secondary)
            }
            .padding()
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(backgroundColor)
                    .shadow(color: shadowColor, radius: shadowRadius, x: 0, y: shadowOffset)
            )
            .scaleEffect(isPressed ? 0.95 : 1.0)
        }
        .buttonStyle(PlainButtonStyle())
        .disabled(isSelected)
    }
    
    private var backgroundColor: Color {
        if isSelected {
            return Color.blue
        } else {
            return Color(.systemGray6)
        }
    }
    
    private var shadowColor: Color {
        if isSelected {
            return Color.blue.opacity(0.3)
        } else {
            return Color.black.opacity(0.1)
        }
    }
    
    private var shadowRadius: CGFloat {
        if isSelected {
            return 8
        } else {
            return 4
        }
    }
    
    private var shadowOffset: CGFloat {
        if isSelected {
            return 4
        } else {
            return 2
        }
    }
}

struct ChoiceButton_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 15) {
            ChoiceButton(
                choice: StoryChoice(
                    text: "Enter the caverns boldly",
                    action: "bold_entrance",
                    description: "Charge forward with confidence"
                ),
                isSelected: false,
                action: {}
            )
            
            ChoiceButton(
                choice: StoryChoice(
                    text: "Study the entrance first",
                    action: "cautious_approach",
                    description: "Take a careful look around"
                ),
                isSelected: true,
                action: {}
            )
        }
        .padding()
        .previewLayout(.sizeThatFits)
    }
}
