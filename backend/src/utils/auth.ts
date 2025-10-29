// helper middleware for JWT verification

import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';


const JWT_SECRET = process.env.JWT_SECRET || 'change_this_secret';


export interface AuthRequest extends Request {
user?: { id: string; username: string };
}


export function authMiddleware(req: AuthRequest, res: Response, next: NextFunction) {
try {
    const auth = req.headers.authorization;
    console.log(auth)
if (!auth) return res.status(401).json({ message: 'Missing Authorization header' });
const token = auth.split(' ')[1];
const payload = jwt.verify(token, JWT_SECRET) as { id: string; username: string };
req.user = payload;
next();
} catch (err) {
return res.status(401).json({ message: 'Invalid token' });
}
}