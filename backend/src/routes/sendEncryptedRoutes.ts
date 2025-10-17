import { authMiddleware, AuthRequest } from "@src/utils/auth";
import { Router } from "express";
import { User } from "@src/models/User";
import { Message } from "@src/models/Message";
import upload from "@src/utils/multer";
import fs from "fs";
import path from "path";
import { Server } from "socket.io";
import express from "express";
import http from "http";

const router = Router();

/**
 * ===============================
 * TEXT MESSAGE ENDPOINT
 * ===============================
 */
router.post("/send-text", authMiddleware, async (req: AuthRequest, res) => {
  try {
    const { recipient, encryptedAesKeyB64, nonceB64, ciphertextB64, tagB64 } = req.body;
    console.log(tagB64)
    if (!recipient || !encryptedAesKeyB64 || !nonceB64 || !ciphertextB64)
      return res.status(400).json({ message: "Missing required fields" });

    const msg = new Message({
      sender: req.user!.username,
      recipient,
      encryptedAesKey: Buffer.from(encryptedAesKeyB64, "base64"),
      nonce: Buffer.from(nonceB64, "base64"),
      ciphertext: Buffer.from(ciphertextB64, "base64"),
      tag: Buffer.from(tagB64, "base64"), // ← Added tag field
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
        type: "text",
        tagB64
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
router.post(
  "/send-file",
  authMiddleware,
  upload.single("file"),
  async (req: AuthRequest, res) => {
    try {
      const { recipient, encryptedAesKeyB64, nonceB64, ciphertextB64 } = req.body;
      if (!req.file) return res.status(400).json({ message: "Missing file" });

      const msg = new Message({
        sender: req.user!.username,
        recipient,
        encryptedAesKey: Buffer.from(encryptedAesKeyB64, "base64"),
        nonce: Buffer.from(nonceB64, "base64"),
        ciphertext: Buffer.from(ciphertextB64, "base64"), // encrypted file metadata or symmetric key
        filename: req.file.filename,
        filesize: req.file.size,
        filepath: req.file.path,
        type: "file",
      });
      await msg.save();

      // Notify recipient in real-time
      const recipientUser = await User.findOne({ username: recipient });
      if (recipientUser?.socketId) {
        io.to(recipientUser.socketId).emit("receive_message", {
          id: msg._id,
          from: msg.sender,
          encryptedAesKeyB64,
          nonceB64,
          ciphertextB64,
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
  }
);

/**
 * ===============================
 * FETCH MESSAGES ENDPOINT
 * ===============================
 */
router.get("/fetch", authMiddleware, async (req: AuthRequest, res) => {
  const msgs = await Message.find({ recipient: req.user!.username }).sort({ createdAt: 1 });
  return res.json(
    msgs.map((m) => ({
      id: m._id,
      sender: m.sender,
      encryptedAesKeyB64: m.encryptedAesKey.toString("base64"),
      nonceB64: m.nonce.toString("base64"),
      ciphertextB64: m.ciphertext.toString("base64"),
      filename: m.filename,
      filesize: m.filesize,
      type: m.type,
      delivered: m.delivered,
      createdAt: m.createdAt,
    }))
  );
});

/**
 * ===============================
 * DOWNLOAD ENCRYPTED FILE ENDPOINT
 * ===============================
 */
router.get("/download/:id", authMiddleware, async (req: AuthRequest, res) => {
  try {
    const msg = await Message.findById(req.params.id);
    if (!msg || msg.recipient !== req.user!.username)
      return res.status(404).json({ message: "File not found or access denied" });

    if (!msg.filepath) return res.status(400).json({ message: "No file path found" });

    const filePath = path.resolve(msg.filepath);
    if (!fs.existsSync(filePath)) return res.status(404).json({ message: "File missing on server" });

    res.setHeader("Content-Disposition", `attachment; filename="${msg.filename}"`);
    res.setHeader("Content-Type", "application/octet-stream");
    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Error downloading file" });
  }
});



/**
 * GET /messages/history/:otherUsername
 * Fetch all messages between the current user and another user.
 */
router.get("/history/:otherUsername", authMiddleware, async (req: AuthRequest, res) => {
  try {
    const { otherUsername } = req.params;
    const currentUser = req.user?.username;

    if (!otherUsername || !currentUser) {
      return res.status(400).json({ message: "Missing username(s)" });
    }

    // Find all messages where (sender=currentUser and recipient=otherUsername)
    // or (sender=otherUsername and recipient=currentUser)
    const msgs = await Message.find({
      $or: [
        { sender: currentUser, recipient: otherUsername },
        { sender: otherUsername, recipient: currentUser }
      ]
    }).sort({ createdAt: 1 }); // oldest first

    // Map to frontend-compatible format
    const formatted = msgs.map((m) => ({
      id: m._id,
      sender: m.sender,
      recipient: m.recipient,
      encryptedAesKeyB64: m.encryptedAesKey.toString("base64"),
      nonceB64: m.nonce.toString("base64"),
      ciphertextB64: m.ciphertext.toString("base64"),
      tagB64: m.tag ? m.tag.toString("base64") : null,
      type: m.type, // "text" or "file"
      filename: m.filename,
      filesize: m.filesize,
      createdAt: m.createdAt
    }));

    return res.status(200).json({ messages: formatted });
  } catch (err) {
    console.error("History fetch error:", err);
    return res.status(500).json({ message: "Server error fetching messages" });
  }
});





export default router;
