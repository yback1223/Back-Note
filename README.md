# Back Note - AI-Powered Note-Taking and Quiz Generation Application

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.47+-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Back Note is an intelligent note-taking application that leverages AI (Google Gemini) to automatically generate quizzes from your notes, grade quiz attempts, and provide detailed feedback. It's designed to enhance learning through interactive quiz-based review sessions.

## 🌟 Features

### 📝 Smart Note Management
- **Rich Text Notes**: Create and organize notes with comprehensive content
- **Hashtag System**: Tag notes for easy categorization and search
- **Search & Filter**: Find notes by hashtags, titles, or content with autocomplete suggestions
- **Note History**: Track creation dates and view note history

### 🤖 AI-Powered Quiz Generation
- **Automatic Quiz Creation**: AI generates multiple-choice questions from your notes
- **Intelligent Question Types**: Various question formats based on note content
- **Context-Aware**: Questions are tailored to the specific content and context of your notes

### 📊 Advanced Quiz System
- **Interactive Quiz Taking**: Take quizzes with real-time feedback
- **AI Grading**: Intelligent grading with detailed explanations
- **Performance Tracking**: Monitor your quiz performance over time
- **Review Mode**: Re-take quizzes to improve understanding
- **Detailed Analytics**: View correct/incorrect answers with explanations

### 🔧 User-Friendly Interface
- **Modern UI**: Clean, responsive design built with Streamlit
- **Multi-language Support**: English and Korean interfaces
- **Intuitive Navigation**: Easy-to-use sidebar navigation
- **Real-time Updates**: Dynamic content updates without page refresh

### 🔒 Security & Configuration
- **API Key Management**: Secure storage and management of Gemini API keys
- **Model Selection**: Choose from different AI models for various use cases
- **Configurable Settings**: Customize quiz generation parameters

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- Google Gemini API key
- Docker (optional, for containerized deployment)

### Installation

#### Option 1: Local Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/back-note.git
cd back-note

# Install dependencies using uv
uv sync

# Run the application
uv run streamlit run main.py
```

#### Option 2: Docker Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/back-note.git
cd back-note

# Start with Docker (Development)
./scripts/start.sh dev

# Or start with Docker (Production)
./scripts/start.sh prod
```

### Access the Application
- **Local**: http://localhost:8501
- **Docker**: http://localhost:8501 (dev) or https://localhost (prod)

## 📖 How to Use

### 1. Getting Started

#### Setting Up Your API Key
1. Navigate to the "New Note" tab
2. Enter your Google Gemini API key in the API Key field
3. Select your preferred AI model (e.g., gemini-1.5-pro)
4. Your API key will be securely stored for future use

### 2. Creating Notes

#### Step-by-Step Note Creation
1. **Go to "New Note"**: Click on the "New Note" tab in the sidebar
2. **Enter Note Content**: Write your note in the text area
   - Use clear, structured content for better quiz generation
   - Include key concepts, definitions, and examples
3. **Configure Quiz Settings**:
   - **Number of Questions**: Choose how many questions to generate (1-10)
   - **Question Types**: Select from various question formats
4. **Submit**: Click "Submit Note" to process your content

#### Best Practices for Note Writing
- **Be Specific**: Include clear definitions and examples
- **Use Structure**: Organize content with headings and bullet points
- **Include Context**: Provide background information for better understanding
- **Add Examples**: Include practical examples for more diverse questions

### 3. Managing Your Notes

#### Viewing Notes
1. **Note List**: Go to "Note List" to see all your notes
2. **Search & Filter**:
   - Use hashtag search for specific topics
   - Search by title or content with autocomplete
   - Combine searches with AND logic
3. **Sort Options**: Sort by newest or oldest first

#### Note Details
1. **Click on a Note**: Select any note from the list to view details
2. **Note Content Tab**: View your note content and associated hashtags
3. **Quiz Results Tab**: See your quiz performance history (if available)
4. **Review Quiz Tab**: Take new quiz attempts

### 4. Taking Quizzes

#### Quiz Interface
1. **Access Quiz**: Go to the "Review Quiz" tab in note details
2. **Answer Questions**: Select your answers for each multiple-choice question
3. **Submit Quiz**: Click "Submit Quiz" to get AI grading
4. **Review Results**: Check your performance in the "Quiz Result" tab

#### Understanding Quiz Results
- **Overall Performance**: See correct, partially correct, and incorrect answers
- **Detailed Feedback**: Review each question with:
  - Your selected answer
  - The correct answer
  - AI-generated explanation
  - Performance score

### 5. Advanced Features

#### Hashtag Management
- **Add Hashtags**: Include relevant hashtags when creating notes
- **Search by Hashtags**: Use hashtag search to find related notes
- **Autocomplete**: Get suggestions for existing hashtags

#### Quiz Customization
- **Question Count**: Adjust the number of questions per quiz
- **Model Selection**: Choose different AI models for various content types
- **Retry Quizzes**: Take multiple attempts to improve understanding

## 🏗️ Architecture

### Project Structure
```
back-note/
├── core/                     # Core AI and business logic
│   ├── gemini_work.py       # Gemini API integration
│   ├── submit_note.py       # Note processing and quiz generation
│   └── submit_quiz.py       # Quiz grading and feedback
├── pages_english/           # English interface
│   ├── app.py              # Main application controller
│   ├── controller.py       # Business logic controller
│   └── views/              # UI components
├── repositories/           # Data access layer
│   ├── my_db.py           # Database connection
│   ├── note_repository.py # Note CRUD operations
│   └── ...                # Other repositories
├── main.py                # Application entry point
└── pyproject.toml         # Dependencies and project config
```

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.12+
- **AI Integration**: Google Gemini API
- **Database**: SQLite (with repository pattern)
- **Package Management**: uv
- **Containerization**: Docker & Docker Compose

## 🔧 Configuration

### Environment Variables
```bash
# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true

# AI Model Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-pro
```

### Database Schema
The application uses SQLite with the following main tables:
- `notes`: Note content and metadata
- `note_hashtags`: Hashtag associations
- `questions`: Generated quiz questions
- `options`: Multiple choice options
- `gradings`: Quiz attempt results

## 🚀 Deployment

### Docker Deployment
For production deployment, see [README-Docker.md](README-Docker.md) for detailed instructions.

### Local Development
```bash
# Install development dependencies
uv sync --dev

# Run with hot reload
uv run streamlit run main.py --server.runOnSave=true
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Google Gemini](https://ai.google.dev/) for AI capabilities
- [uv](https://github.com/astral-sh/uv) for fast Python package management

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/back-note/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/back-note/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/back-note/wiki)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Made with ❤️ for better learning and knowledge retention**