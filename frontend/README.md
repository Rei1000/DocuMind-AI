# DocuMind-AI Frontend

Next.js 14 + TypeScript Frontend für DocuMind-AI QMS

## Features

- **Next.js 14** mit App Router
- **TypeScript** für Type Safety
- **Tailwind CSS** für Styling
- **shadcn/ui** Komponenten (geplant)
- **API Client** mit Bearer Token Authentication

## Seiten

- `/` - Homepage mit Navigation
- `/login` - Authentication (POST /api/auth/login)
- `/models` - AI Model Management
- `/interest-groups` - Interest Groups CRUD

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp env.example .env.local
```

3. Start development server:
```bash
npm run dev
```

## API Integration

Das Frontend kommuniziert mit dem Backend über:
- Base URL: `NEXT_PUBLIC_API_BASE_URL` (default: http://localhost:8000)
- Authentication: Bearer Token in localStorage
- API Client: `lib/api.ts` mit automatischer Token-Injection

## OpenAPI Integration

Für automatische API-Client-Generierung:
1. Backend starten: `cd ../backend && python -m uvicorn app.main:app --reload`
2. OpenAPI Schema generieren: `curl http://localhost:8000/openapi.json > openapi.json`
3. Client generieren: `npx @openapitools/openapi-generator-cli generate -i openapi.json -g typescript-fetch -o src/generated`

## Development

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run lint` - ESLint
- `npm run type-check` - TypeScript check
