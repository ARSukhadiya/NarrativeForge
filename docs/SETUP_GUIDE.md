# NarrativeForge Setup Guide

## Prerequisites

Before setting up NarrativeForge, ensure you have the following installed:

### Backend Requirements
- Python 3.8 or higher
- pip (Python package manager)
- Git

### iOS Requirements
- Xcode 14.0 or higher
- iOS 16.0+ deployment target
- macOS (for iOS development)

## Backend Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd NarrativeForge
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the backend directory:
```bash
# Backend configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# LLM Configuration
MODEL_NAME=microsoft/DialoGPT-medium
MAX_LENGTH=512
TEMPERATURE=0.8
TOP_P=0.9

# Logging
LOG_LEVEL=INFO
```

### 5. Run the Backend
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 6. Verify Installation
```bash
# Test the API
curl http://localhost:8000/health
```

You should see:
```json
{"status": "healthy", "service": "narrative-forge"}
```

## iOS Setup

### 1. Open the Project
```bash
cd ios/NarrativeForge
open NarrativeForge.xcodeproj
```

### 2. Configure API Endpoint
In `StoryService.swift`, update the `baseURL` to match your backend:
```swift
private let baseURL = "http://localhost:8000/api/v1"
```

### 3. Configure Network Security (iOS 9+)
Add the following to your `Info.plist` to allow HTTP connections to localhost:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### 4. Build and Run
1. Select your target device or simulator
2. Press `Cmd + R` to build and run
3. The app should launch and connect to your backend

## Development Workflow

### Backend Development
1. Start the backend server
2. Make changes to Python files
3. The server will auto-reload on file changes
4. Test API endpoints using the interactive docs at `http://localhost:8000/docs`

### iOS Development
1. Ensure backend is running
2. Make changes to Swift files
3. Build and run in Xcode
4. Test the complete flow

## Testing

### Backend Testing
```bash
# Run tests (when implemented)
cd backend
python -m pytest

# Test API endpoints
curl -X POST "http://localhost:8000/api/v1/stories" \
  -H "Content-Type: application/json" \
  -d '{"genre": "fantasy", "difficulty": "medium"}'
```

### iOS Testing
1. Use Xcode's built-in testing framework
2. Test on different device sizes and orientations
3. Test network connectivity scenarios

## Troubleshooting

### Common Backend Issues

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

**LLM Model Loading Issues**
- Check internet connection for model download
- Verify sufficient disk space
- Check GPU memory if using CUDA

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Common iOS Issues

**Network Connection Failed**
- Verify backend is running
- Check API endpoint URL
- Ensure network security settings

**Build Errors**
- Clean build folder (`Cmd + Shift + K`)
- Reset package caches
- Check Xcode version compatibility

**Simulator Issues**
- Reset simulator content and settings
- Use different simulator device
- Check iOS deployment target

## Production Deployment

### Backend Deployment
1. Use a production WSGI server (Gunicorn)
2. Set up reverse proxy (Nginx)
3. Configure environment variables
4. Set up monitoring and logging

### iOS Deployment
1. Configure production API endpoints
2. Set up code signing
3. Test on physical devices
4. Submit to App Store

## Performance Optimization

### Backend
- Use model quantization for faster inference
- Implement caching for story templates
- Optimize database queries (when implemented)
- Use async processing for long operations

### iOS
- Implement image caching
- Optimize network requests
- Use background processing for story generation
- Implement offline mode

## Security Considerations

### Backend
- Implement authentication and authorization
- Validate all input data
- Use HTTPS in production
- Implement rate limiting
- Sanitize LLM outputs

### iOS
- Secure API communication
- Implement certificate pinning
- Protect sensitive data
- Follow Apple security guidelines

## Monitoring and Logging

### Backend Logging
The application uses `loguru` for logging. Configure log levels and outputs in the main application.

### iOS Logging
Use Xcode's console for debugging and implement crash reporting for production.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check GitHub issues
4. Create a new issue with detailed information
