# Frontend (React Web)

Dev server
```
cd C:\AdultingOS\frontend
npm install
npm start
```

Configure API base URL
- Default is http://127.0.0.1:8000 in `src/services/apiService.js`
- For different environments, set `REACT_APP_API_URL` in `.env`

Auth flow
- Register → Login → store token → call /api/tasks/
- Token header: `Authorization: Token <token>`
