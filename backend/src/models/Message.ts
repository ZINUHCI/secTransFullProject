import mongoose, { Schema, Document } from "mongoose";

export interface IMessage extends Document {
  sender: string;
  recipient: string;
  encryptedAesKey: Buffer;
  nonce: Buffer;
  ciphertext: Buffer; // encrypted text OR encrypted file metadata
  type: "text" | "file";
  filename?: string | null;
  filesize?: number | null;
  filepath?: string | null;
  delivered: boolean;
  createdAt: Date;
  tag: Buffer;
}

const MessageSchema = new Schema<IMessage>(
  {
    sender: { type: String, required: true },
    recipient: { type: String, required: true },
    encryptedAesKey: { type: Buffer, required: true },
    nonce: { type: Buffer, required: true },
    ciphertext: { type: Buffer, required: true },

    // differentiate between text and file messages
    type: {
      type: String,
      enum: ["text", "file"],
      required: true,
      default: "text",
    },

    // fields used only when type === 'file'
    filename: { type: String, default: null },
    filesize: { type: Number, default: null },
    filepath: { type: String, default: null },
    tag: { type: Buffer },

    delivered: { type: Boolean, default: false },
  },
  {
    timestamps: { createdAt: true, updatedAt: false },
  }
);

export const Message = mongoose.model<IMessage>("Message", MessageSchema);
