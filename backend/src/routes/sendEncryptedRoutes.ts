import { Router } from "express";
import { Server } from "socket.io";
import { User } from "@src/models/User";
import { Message } from "@src/models/Message";
import { authMiddleware, AuthRequest } from "@src/utils/auth";
import upload from "@src/utils/multer";
import fs from "fs";
import path from "path";

// Instead of exporting a plain router, export a function that takes io
export default function msgsRouter(io: Server) {
  const router = Router();

  /**
   * ===============================
   * TEXT MESSAGE ENDPOINT
   * ===============================
   */
  router.post("/send-text", authMiddleware, async (req: AuthRequest, res) => {
    try {
      const { recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64 } = req.body;
      if (!recipient || !encryptedAesKeyB64 || !nonceB64 || !ciphertextB64 || !tagB64)
        return res.status(400).json({ message: "Missing required fields" });

      const msg = new Message({
        sender: req.user!.username,
        recipient,
        encryptedAesKey: Buffer.from(encryptedAesKeyB64, "base64"),
        nonce: Buffer.from(nonceB64, "base64"),
        ciphertext: Buffer.from(ciphertextB64, "base64"),
        tag: Buffer.from(tagB64, "base64"),
        type: "text",
      });
      await msg.save();

      // Try real-time delivery
      const recipientUser = await User.findOne({ username: recipient });
      if (recipientUser?.socketId) {
        io.to(recipientUser.socketId).emit("receive_message", {
          id: msg._id,
          from: msg.sender,
          encryptedAesKeyB64,
          nonceB64,
          ciphertextB64,
          tagB64,
          type: "text",
        });
        msg.delivered = true;
        await msg.save();
      }

      return res.status(200).json({ message: "Text message stored" });
    } catch (err) {
      console.error(err);
      return res.status(500).json({ message: "Server error" });
    }
  });

  /**
   * ===============================
   * FILE MESSAGE ENDPOINT
   * ===============================
   */
  router.post("/send-file", authMiddleware, upload.single("file"), async (req: AuthRequest, res) => {
    try {
      const { recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64 } = req.body;
      if (!req.file) return res.status(400).json({ message: "Missing file" });

      const msg = new Message({
        sender: req.user!.username,
        recipient,
        encryptedAesKey: Buffer.from(encryptedAesKeyB64, "base64"),
        nonce: Buffer.from(nonceB64, "base64"),
        ciphertext: Buffer.from(ciphertextB64, "base64"),
        tag: Buffer.from(tagB64, "base64"),
        filename: req.file.filename,
        filesize: req.file.size,
        filepath: req.file.path,
        type: "file",
      });
      await msg.save();

      const recipientUser = await User.findOne({ username: recipient });
      if (recipientUser?.socketId) {
        io.to(recipientUser.socketId).emit("receive_message", {
          id: msg._id,
          from: msg.sender,
          encryptedAesKeyB64,
          nonceB64,
          ciphertextB64,
          tagB64,
          filename: msg.filename,
          filesize: msg.filesize,
          type: "file",
        });
        msg.delivered = true;
        await msg.save();
      }

      return res.status(200).json({
        message: "Encrypted file message stored",
        fileInfo: { name: msg.filename, size: msg.filesize },
      });
    } catch (err) {
      console.error(err);
      return res.status(500).json({ message: "Server error" });
    }
  });


    /**
   * ===============================
   * FETCH UNDELIVERED (MISSED) MESSAGES
   * ===============================
   */
  router.get("/missed", authMiddleware, async (req: AuthRequest, res) => {
    try {
      const username = req.user!.username;

      // Find messages that were sent TO this user but not yet delivered
      const missed = await Message.find({
        recipient: username,
        delivered: false
      }).sort({ timestamp: 1 });

      // Mark them as delivered immediately (to prevent resend on next call)
      await Message.updateMany(
        { recipient: username, delivered: false },
        { $set: { delivered: true } }
      );

      // Prepare response with Base64 fields for client-side decryption
      const formatted = missed.map(m => ({
        id: m._id,
        from: m.sender,
        encryptedAesKeyB64: m.encryptedAesKey.toString("base64"),
        nonceB64: m.nonce.toString("base64"),
        ciphertextB64: m.ciphertext.toString("base64"),
        tagB64: m.tag.toString("base64"),
        type: m.type,
        filename: m.filename,
        filesize: m.filesize,
        timestamp: m.createdAt,
      }));

      return res.status(200).json({ missed: formatted });
    } catch (err) {
      console.error(err);
      return res.status(500).json({ message: "Server error" });
    }
  });



  return router;
}
