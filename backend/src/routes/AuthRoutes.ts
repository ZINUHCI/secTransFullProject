import { Router } from "express"
import { User } from "@src/models/User";
import bcrypt from 'bcryptjs';
import dotenv from "dotenv";
import jwt from 'jsonwebtoken';

dotenv.config();

const router = Router()
const JWT_SECRET = process.env.JWT_SECRET || 'change_this_secret';


// ---- Auth routes ----
router.post('/register', async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ message: 'Missing fields' });
    const exists = await User.findOne({ username });
    if (exists) return res.status(400).json({ message: 'Username taken' });
    const hash = await bcrypt.hash(password, 10);
    const u = new User({ username, password: hash });
    await u.save();
    return res.status(200).json({ message: 'ok' });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'server error' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;
    if (!username || !password) return res.status(400).json({ message: 'Missing fields' });
    const user = await User.findOne({ username });
    if (!user) return res.status(400).json({ message: 'Invalid credentials' });
    const ok = await bcrypt.compare(password, user.password);
    if (!ok) return res.status(401).json({ message: 'Invalid credentials' });
    const token = jwt.sign({ id: user._id, username: user.username }, JWT_SECRET, { expiresIn: '12h' });
    user.status = 'online';
    await user.save();
    return res.status(200).json({ message: 'ok', token });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'server error' });
  }
});




export default router;