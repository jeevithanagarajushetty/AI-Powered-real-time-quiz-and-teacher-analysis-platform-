# AI-Powered Real-Time Adaptive Quiz and Teaching Analytics Platform

A comprehensive MCA-level project that transforms classroom learning through AI-powered quiz generation, real-time monitoring, and detailed analytics.

## 🚀 Features

### 🎯 Core Features
- **AI Quiz Generation**: Automatically generate quizzes from PDFs, PPTs, YouTube links, and other teaching materials
- **Unique Quiz Codes**: Each quiz gets a unique 6-character code for easy access
- **Real-Time Monitoring**: Advanced malactivity detection with tab-switch prevention
- **Adaptive Difficulty**: Support for easy, medium, and hard difficulty levels
- **Instant Results**: Real-time result generation with student rankings
- **Comprehensive Analytics**: Detailed performance tracking and insights

### 👥 Multi-Role System
- **Students**: Attend quizzes, view results, track progress
- **Teachers**: Create quizzes, monitor students, generate reports
- **Admins**: Platform management, comprehensive analytics, user management

### 🛡️ Security Features
- **Malactivity Detection**: 3-strike warning system
- **Auto-Submit**: Automatic submission on malactivity
- **Tab Switch Prevention**: Real-time browser monitoring
- **Copy/Paste Protection**: Prevent content copying during quizzes

### 📊 Analytics & Reporting
- **Performance Analytics**: Student and teacher performance insights
- **Engagement Metrics**: User activity and participation tracking
- **Security Reports**: Malactivity incidents and security scores
- **Export Features**: CSV reports for further analysis

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **MongoDB**: Database for storing user data, quizzes, and analytics
- **Python**: Core programming language
- **Transformers**: AI model for quiz generation

### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript**: Real-time monitoring and interactions
- **Font Awesome**: Icons and visual elements
- **Glassmorphism Design**: Modern UI with animations

### AI/ML
- **T5-base Question Generation**: Advanced NLP model
- **Content Analysis**: Smart extraction from teaching materials
- **Adaptive Algorithms**: Difficulty adjustment based on performance

## 📋 Installation Guide

### Prerequisites
- Python 3.8 or higher
- MongoDB (local or cloud instance)
- Git for cloning the repository

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd AI_Quiz_Generator
```

### Step 2: Set Up Virtual Environment
```bash
python -m venv quiz_env
# On Windows
quiz_env\Scripts\activate
# On Mac/Linux
source quiz_env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
1. Install MongoDB on your system or use MongoDB Atlas
2. Update the MongoDB connection string in `config.py` if needed
3. Ensure MongoDB is running on `localhost:27017` (default)

### Step 5: Environment Setup
Create a `.env` file in the root directory:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017/
```

### Step 6: Run the Application
```bash
python app_new.py
```

The application will be available at `http://localhost:5000`

## 🎮 Usage Guide

### For Teachers
1. **Registration**: Sign up as a teacher with your details
2. **Create Quiz**: Upload teaching materials (PDF, PPT, YouTube links)
3. **Configure Settings**: Set difficulty, duration, and question count
4. **Generate Quiz**: AI creates questions and generates unique code
5. **Monitor**: Real-time monitoring during quiz sessions
6. **View Results**: Access comprehensive analytics and student performance

### For Students
1. **Registration**: Sign up with your register number and details
2. **Attend Quiz**: Enter quiz code provided by teacher
3. **Take Quiz**: Answer questions under monitored conditions
4. **View Results**: See your score, ranking, and detailed performance

### For Admins
1. **Platform Management**: Oversee all users and activities
2. **Analytics**: Access comprehensive platform statistics
3. **Reports**: Generate detailed performance and security reports
4. **User Management**: Manage user accounts and permissions

## 📁 Project Structure

```
AI_Quiz_Generator/
├── app_new.py              # Main Flask application
├── config.py               # Database configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── modules/               # Core functionality modules
│   ├── database_models.py # Database schemas and models
│   ├── quiz_manager.py    # Quiz creation and management
│   ├── quiz_monitor.py    # Real-time monitoring system
│   ├── analytics_engine.py # Analytics and reporting
│   ├── quiz_generator.py  # AI quiz generation
│   └── file_reader.py     # File processing utilities
├── templates/             # HTML templates
│   ├── modern_home.html    # Modern home page
│   ├── modern_login.html   # Login page
│   ├── modern_register.html # Registration page
│   ├── admin_dashboard.html # Admin interface
│   ├── results.html        # Results and rankings
│   └── ...                # Other templates
├── static/                # Static assets
│   └── css/
│       └── modern-style.css # Modern CSS styling
└── uploads/               # File upload directory
```

## 🔧 Configuration

### Database Configuration
Update `config.py` with your MongoDB settings:
```python
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_quiz_system"]
```

### Quiz Generation Settings
Modify `modules/quiz_generator.py` for different AI models or parameters.

### Monitoring Settings
Adjust malactivity detection settings in `modules/quiz_monitor.py`.

## 🧪 Testing

### Manual Testing Steps
1. **User Registration**: Test all three roles (student, teacher, admin)
2. **Quiz Creation**: Upload different file types and test AI generation
3. **Quiz Taking**: Test monitoring features and malactivity detection
4. **Results**: Verify ranking system and score calculations
5. **Analytics**: Test report generation and data accuracy

### Test Cases
- Registration with valid/invalid data
- Quiz creation with various file types
- Malactivity detection (tab switching, copy/paste)
- Real-time monitoring accuracy
- Result calculation and ranking
- Analytics report generation

## 🚀 Deployment

### Local Deployment
1. Ensure all dependencies are installed
2. Configure MongoDB connection
3. Run `python app_new.py`
4. Access at `http://localhost:5000`

### Production Deployment
1. Set environment variables
2. Configure production database
3. Use WSGI server (Gunicorn)
4. Set up reverse proxy (Nginx)
5. Enable HTTPS

## 🔒 Security Considerations

- Password hashing (implement bcrypt)
- Session security
- Input validation and sanitization
- Rate limiting for API endpoints
- HTTPS enforcement in production
- Database security and backups

## 📈 Performance Optimization

- Database indexing for frequently queried fields
- Caching for analytics data
- Lazy loading for large datasets
- Image optimization for uploads
- CDN for static assets

## 🐛 Troubleshooting

### Common Issues
1. **MongoDB Connection**: Ensure MongoDB is running
2. **File Upload**: Check upload directory permissions
3. **AI Model**: Ensure transformers library is properly installed
4. **Port Conflicts**: Change port if 5000 is in use

### Debug Mode
Enable debug mode in Flask:
```python
app.run(debug=True)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 Future Enhancements

- Mobile app development
- Video proctoring
- Advanced AI models
- Real-time collaboration
- Integration with LMS systems
- Multi-language support
- Advanced analytics dashboard
- Gamification features

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the code comments
- Test with different configurations
- Create detailed bug reports

## 📄 License

This project is for educational purposes. Use appropriate licensing for production use.

---

**Note**: This is an MCA-level project demonstrating modern web development, AI integration, and educational technology. The system is designed to be scalable, secure, and user-friendly while providing comprehensive learning analytics.
