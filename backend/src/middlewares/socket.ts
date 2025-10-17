import express from "express";
import { Server, Socket, ExtendedError } from "socket.io";
import dotenv from "dotenv";
import { User } from "@src/models/User";
import jwt from "jsonwebtoken";
import { Message } from "@src/models/Message";

dotenv.config();

const JWT_SECRET = process.env.JWT_SECRET || 'change_this_secret';

const app = express();

// ---------- socket.io auth middleware ----------

export const socketAuthMiddleware = (socket: Socket, next:(err?: ExtendedError | undefined) => void) => {
  try {
    const token = socket.handshake.auth?.token as string | undefined;
    if (!token) return next(new Error('Authentication error: token missing'));
    const payload = jwt.verify(token, JWT_SECRET) as { id: string; username: string };
    (socket as any).user = payload;
    next();
  } catch (err) {
    console.error('Socket auth failed', err);
    next(new Error('Authentication error'));
  }
};

export const socketOnConnection = (io: Server) => {
  return async function(socket: Socket){
  const payload = (socket as any).user as { id: string; username: string };
  const username = payload.username;
  console.log('socket connected', socket.id, 'user', username);
  await User.findOneAndUpdate({ username }, { socketId: socket.id, status: 'online' });

  socket.on('send_message', async (payload) => {
    try {
      const { recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, filename, filesize } = payload;
      const msg = new Message({
        sender: username,
        recipient,
        encryptedAesKey: Buffer.from(encryptedAesKeyB64, 'base64'),
        nonce: Buffer.from(nonceB64, 'base64'),
        ciphertext: Buffer.from(ciphertextB64, 'base64'),
        filename: filename || null,
        filesize: filesize || null
      });
      await msg.save();
      const rUser = await User.findOne({ username: recipient });
      if (rUser && rUser.socketId) {
        io.to(rUser.socketId).emit('receive_message', {
          id: msg._id,
          from: msg.sender,
          encryptedAesKeyB64,
          nonceB64,
          ciphertextB64,
          filename,
          filesize
        });
        msg.delivered = true;
        await msg.save();
      }
    } catch (err) {
      console.error('send_message error', err);
    }
  });
  
  
  socket.on('logout_user', async (u: string) => {
    await User.findOneAndUpdate({ username: u }, { status: 'offline', socketId: null });
    socket.disconnect(true);
  });

  socket.on('disconnect', async (reason) => {
    console.log('socket disconnected', socket.id, reason);
    await User.findOneAndUpdate({ socketId: socket.id }, { socketId: null, status: 'offline' });
  });
}
}
