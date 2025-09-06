# TheLibraryApp - Standalone Educational Library

A complete, self-contained Electron desktop application providing access to thousands of educational books with full registration frontend.

## 📁 Project Structure

```
TheLibraryApp/
├── 📁 Config/                               # Configuration files
│   ├── .env.template                        # Environment variables template
│   ├── email_config.json                    # Email service configuration
│   ├── google_credentials.json.template     # Google OAuth template
│   ├── ourlibrary_config.json              # Main app configuration
│   └── ourlibrary_google_config.json       # Google Drive integration config
│
├── 📁 Data/                                 # Database storage
│   └── 📁 Databases/
│       ├── OurLibrary.db                    # SQLite database (1,219+ books)
│       └── Schema_OurLibrary.pdf            # Database schema documentation
│
├── 📁 OurLibrary/                           # Project assets
│   └── ProjectHimalayaBanner.png            # Banner image for registration page
│
├── 📁 node_modules/                         # NPM dependencies (excluded from tree)
│
├── 🌐 Frontend Files
│   ├── index.html                           # Registration landing page
│   ├── setup-consent.html                   # Library setup consent page
│   ├── new-desktop-library.html             # Main library interface
│   └── web-shim.js                         # Database integration & Firebase bridge
│
├── ⚡ Electron App Core
│   ├── main.js                             # Electron main process
│   ├── preload.js                          # Security bridge for renderer
│   ├── package.json                        # App metadata & dependencies
│   └── package-lock.json                   # Dependency lock file
│
└── 🔧 Utilities
    ├── launch_server.py                     # Python web server launcher
    └── -home-herb-Desktop-OurLibrary-Confi.txt  # Configuration notes
```

## 🚀 Quick Start

### Desktop Application

```bash
npm start
```

### Web Browser Testing

```bash
python -m http.server 8090
# Visit: http://localhost:8090
```

## 🔥 Features

### ✅ Complete Registration Flow

- **Landing Page**: Beautiful mission-driven interface
- **Registration Options**: Google OAuth or Email/Password
- **Email Verification**: 6-digit code system with Firebase
- **Consent Process**: Detailed setup explanation
- **User Experience**: Seamless flow from signup to library access

### ✅ Educational Library

- **1,219+ Books**: Comprehensive educational catalog
- **26 Categories**: Organized by subject and level
- **Search Functionality**: Title and author search
- **Offline Reading**: Download books for offline access
- **SQLite Database**: Fast, local book catalog

### ✅ Technical Stack

- **Electron**: Cross-platform desktop app
- **Firebase**: Authentication and email services
- **SQLite**: Local database with SQL.js web compatibility
- **Responsive Design**: Works on desktop and mobile
- **Security**: Context isolation and secure IPC

## 🎯 Mission

> "Getting education into the hands of people who can least afford it"

This application democratizes access to educational resources by providing a completely free, offline-capable digital library for students worldwide.

## 📊 Database

- **Books Table**: 1,219+ educational titles
- **Categories**: 26 subject classifications  
- **Metadata**: Authors, filenames, thumbnails
- **Format**: SQLite for desktop, SQL.js for web
- **Size**: ~10-20MB initial, grows with downloads

## 🔧 Dependencies

### Core Dependencies

- `electron`: Desktop app framework
- `sqlite3`: Database connectivity  
- `googleapis`: Google Drive integration
- `puppeteer`: Web automation (optional)

### Web Dependencies (CDN)

- Firebase SDK v8
- SQL.js for browser database
- Tailwind CSS for styling
- Inter font family

## 🌐 Deployment Modes

### Desktop (Electron)

- Native desktop application
- Full system integration
- Local database access
- Cross-platform support

### Web (Browser)

- HTTP server deployment
- CORS-proof database access
- Firebase authentication
- Progressive Web App ready

## 🔐 Security Features

- Context isolation enabled
- Node integration disabled
- Secure IPC communication
- Firebase authentication
- Local data storage only

## 🎨 User Interface

### Registration Flow

1. **Landing Page**: Mission statement and call-to-action
2. **Registration Modal**: Choose signup method
3. **Form/OAuth**: Complete registration process
4. **Email Verification**: Confirm account via code
5. **Consent Page**: Setup explanation and agreement
6. **Library Access**: Full educational library interface

### Design System

- **Colors**: Dark theme with blue/purple gradients
- **Typography**: Inter font family
- **Components**: Glass-effect cards and modals
- **Icons**: Emoji-based iconography
- **Animation**: Smooth transitions and hover effects

## 📱 Cross-Platform Support

- **Linux**: AppImage and .deb packages
- **Windows**: NSIS installer and portable
- **macOS**: DMG with app signing
- **Web**: Any modern browser

## 🔄 Development Workflow

### Setup

```bash
npm install              # Install dependencies
```

### Development

```bash
npm start               # Launch Electron app
python -m http.server   # Web development server
```

### Testing

- Browser: http://localhost:8090
- Desktop: Electron window
- Debug: DevTools available in both modes

## 📈 Analytics & Monitoring

- User registration tracking
- Library usage metrics
- Book download statistics
- Error reporting and logging

## 🤝 Contributing

This is an educational project focused on providing free access to learning materials. The codebase is designed to be:

- **Maintainable**: Clear structure and documentation
- **Extensible**: Modular architecture
- **Secure**: Best practices for user data
- **Accessible**: Works across platforms and devices

## 📄 License

Educational use - focused on democratizing access to learning resources.

---

*Built with ❤️ for students who need educational resources the most.*