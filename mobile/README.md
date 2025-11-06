# AdultingOS Mobile App

React Native/Expo mobile application for AdultingOS life admin assistant.

## Setup

1. **Install Expo CLI:**
   ```bash
   npm install -g @expo/cli
   ```

2. **Install dependencies:**
   ```bash
   cd mobile
   npm install
   ```

3. **Update API URL:**
   - Edit `src/services/apiService.js`
   - Replace `your-project.vercel.app` with your actual Vercel URL

4. **Start development:**
   ```bash
   npm start
   ```

## Running on Device

- **Android:** `npm run android`
- **iOS:** `npm run ios`
- **Web:** `npm run web`

## Features

- **Bottom Tab Navigation** - Tasks, Chat, Profile
- **AI Assistant Chat** - Full conversation interface with your backend
- **Task Management** - List, create, complete tasks via chat commands
- **Clean UI** - Modern React Native design
- **API Integration** - Connects to your existing FastAPI backend

## Development

The app connects to your AdultingOS backend at:
- Local: `http://localhost:8001/api/`
- Production: `https://your-project.vercel.app/api/`

All task management and AI chat functionality works through the existing backend API endpoints.