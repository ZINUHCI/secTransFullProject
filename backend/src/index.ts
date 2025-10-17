
// Main server: Express + Socket.io + routes

import express from 'express';
import http from 'http';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { Server } from 'socket.io';
import path from 'path';

import { User } from './models/User';
import { authMiddleware, AuthRequest } from './utils/auth';
import authRouter from './routes/AuthRoutes' ;
import pubKeyRouter from "@src/routes/publicKey";
import viewRouter from "@src/routes/view";
import msgsRouter from "@src/routes/sendEncryptedRoutes"
import { socketAuthMiddleware, socketOnConnection } from './middlewares/socket';

dotenv.config();

const MONGO = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/secure_messenger';
const PORT = Number(process.env.PORT || 5000);
const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(__dirname, '..', 'uploads');

// connect mongo
mongoose.connect(MONGO).then(() => console.log('MongoDB connected')).catch(err => {
  console.error('MongoDB connection error', err);
  process.exit(1);
});

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: '*' } });

app.use(cors());
app.use(express.json({ limit: '10mb' }));


app.use("/auth", authRouter);
app.use("/pubKey", pubKeyRouter);

app.use("/view", viewRouter)

app.use("/messages", msgsRouter)

io.use(socketAuthMiddleware);

io.on("connection", socketOnConnection(io))



// logout
app.post('/logout', authMiddleware, async (req: AuthRequest, res) => {
  await User.findByIdAndUpdate(req.user!.id, { status: 'offline', socketId: null });
  return res.json({ message: 'ok' });
});


server.listen(PORT, () => console.log(`Server listening on ${PORT}`));
