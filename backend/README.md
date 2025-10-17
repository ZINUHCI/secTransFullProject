# Secure Messenger - Backend (TypeScript)

1. copy `.env.example` to `.env` and edit values
2. install deps: `npm install`
3. dev: `npm run dev` (requires ts-node-dev)
4. build: `npm run build` then `npm start`

Server exposes REST endpoints for register/login/publish-key/messages and a Socket.IO server for realtime delivery. The server **does not** decrypt messages; it stores and relays encrypted packages.

