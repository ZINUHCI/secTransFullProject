import { Schema, model, Document } from 'mongoose';


export interface IUser extends Document {
username: string;
password: string; // hashed
publicKeyPem?: string | null;
socketId?: string | null;
status: 'online' | 'offline';
}


const UserSchema = new Schema<IUser>({
username: { type: String, required: true, unique: true },
password: { type: String, required: true },
publicKeyPem: { type: String, default: null },
socketId: { type: String, default: null },
status: { type: String, enum: ['online', 'offline'], default: 'offline' }
}, { timestamps: true });


export const User = model<IUser>('User', UserSchema);