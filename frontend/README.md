# SahaayAI Frontend

Beautiful, modern web interface for the SahaayAI AI-powered assistant.

## 🎨 Features

- **Modern UI/UX**: Clean, intuitive chat interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Multi-language Support**: 12 Indian languages
- **Real-time Chat**: Interactive conversation with AI
- **Action Plans**: Visual step-by-step guidance
- **Document Lists**: Clear requirements for schemes
- **Resource Links**: Helpful contacts and resources
- **Loading States**: Smooth UX with loading indicators
- **Error Handling**: Graceful error messages

## 🚀 Quick Start

The frontend is automatically served by the FastAPI backend.

### Access the Frontend

1. **Make sure the backend is running:**
   ```bash
   cd /Users/ajit/Desktop/Github\ Projects/SahaayAI
   source sahaayAI/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open in your browser:**
   ```
   http://localhost:8000
   ```
   
   This will automatically redirect to the frontend.

### Alternative URLs

- **Frontend**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **API Info**: http://localhost:8000/api
- **Health Check**: http://localhost:8000/health

## 📁 File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # Complete styling (modern gradient design)
├── app.js          # JavaScript application logic
└── README.md       # This file
```

## 🎯 Usage

### Starting a Conversation

1. Open the app in your browser
2. Select your preferred language from the dropdown
3. Type your question in the input box
4. Press Enter or click the send button

### Example Queries

Try these sample queries:
- "How do I apply for crop insurance?"
- "What is Ayushman Bharat scheme?"
- "I need help with opening a bank account"
- "Tell me about PM Kisan Yojana"
- "My crops failed due to drought. What compensation can I get?"

### Language Support

The interface supports 12 Indian languages:
- 🇮🇳 English
- 🇮🇳 हिंदी (Hindi)
- 🇮🇳 বাংলা (Bengali)
- 🇮🇳 தமிழ் (Tamil)
- 🇮🇳 తెలుగు (Telugu)
- 🇮🇳 मराठी (Marathi)
- 🇮🇳 ગુજરાતી (Gujarati)
- 🇮🇳 ಕನ್ನಡ (Kannada)
- 🇮🇳 മലയാളം (Malayalam)
- 🇮🇳 ਪੰਜਾਬੀ (Punjabi)
- 🇮🇳 ଓଡ଼ିଆ (Odia)
- 🇮🇳 অসমীয়া (Assamese)

## 🎨 Design Features

### Color Scheme
- Primary: Blue gradient (#2563eb → #1d4ed8)
- Secondary: Green (#10b981)
- Background: Purple gradient (#667eea → #764ba2)
- Clean white cards with subtle shadows

### Components
- **Header**: Logo, language selector, info button
- **Welcome Section**: Feature cards and quick query suggestions
- **Chat Interface**: Message bubbles with avatars
- **Action Plans**: Structured step-by-step guidance
- **Input Area**: Fixed bottom input with status indicator
- **Modal**: Info popup about the service

### Responsive Breakpoints
- Desktop: 1200px max-width
- Tablet: 768px
- Mobile: < 768px (optimized layout)

## 🔧 Customization

### Change API URL

Edit `app.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

### Modify Colors

Edit `styles.css`:
```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #10b981;
    /* ... more variables ... */
}
```

### Add More Quick Queries

Edit `index.html`:
```html
<button class="suggestion-btn" data-query="Your question here">
    "Your question here"
</button>
```

## 🌟 Key Features Explained

### 1. Action Plans
When the AI generates an action plan, it displays:
- **Summary**: Overview of the situation
- **Immediate Actions**: Urgent steps to take
- **Detailed Steps**: Full step-by-step guidance with icons
- **Documents Required**: List of necessary documents
- **Resources**: Helpful contacts and links

### 2. Intent Recognition
The system automatically:
- Detects the domain (agriculture, health, etc.)
- Identifies urgency level
- Extracts key entities
- Shows confidence score

### 3. Loading States
- Animated dots while AI is thinking
- Disabled input during processing
- Smooth transitions

### 4. Error Handling
- Connection status indicator
- Graceful error messages
- Automatic reconnection attempts

## 📱 Mobile Optimization

The interface is fully responsive:
- Touch-friendly buttons
- Optimized font sizes
- Flexible layouts
- Swipe-friendly scrolling

## 🔒 Privacy

- No data stored in browser (except session state)
- Secure API communication
- No tracking or analytics
- Privacy-first design

## 🐛 Troubleshooting

### Frontend Not Loading
1. Check if backend is running: http://localhost:8000/health
2. Clear browser cache
3. Check console for errors (F12)

### API Connection Error
1. Verify backend is running
2. Check CORS settings in backend
3. Ensure correct API_BASE_URL in app.js

### Messages Not Sending
1. Check browser console for errors
2. Verify API endpoint is accessible
3. Check network tab in browser DevTools

## 🚀 Production Deployment

### Build for Production
No build step required! The frontend uses vanilla HTML/CSS/JS.

### Deploy with Backend
1. Copy `frontend/` folder to your server
2. Configure backend to serve static files
3. Set appropriate CORS headers
4. Use reverse proxy (nginx/Apache) for better performance

### CDN Optimization
Consider hosting static assets on a CDN:
- CSS files
- JavaScript files
- Font files
- Image assets

## 📊 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 🎓 Learning Resources

### Frontend Technologies Used
- **HTML5**: Semantic markup
- **CSS3**: Grid, Flexbox, Animations
- **JavaScript ES6+**: Async/await, Fetch API
- **CSS Variables**: Dynamic theming
- **CSS Grid**: Responsive layouts

## 🤝 Contributing

Want to improve the frontend? Consider:
- Adding dark mode
- Implementing voice input
- Adding image upload support
- Creating PWA features
- Adding offline support
- Implementing multi-user chat

## 📝 License

Part of the SahaayAI project. See main project README for license information.

## 🆘 Support

For issues or questions:
1. Check the main project documentation
2. Review the API documentation at `/docs`
3. Check browser console for errors
4. Verify backend is running properly

---

**Built with ❤️ for underserved communities**
