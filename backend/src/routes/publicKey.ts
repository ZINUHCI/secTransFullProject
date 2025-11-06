import { Router } from "express"
import { User } from "@src/models/User";
import { authMiddleware, AuthRequest } from "@src/middlewares/auth";

const router = Router()


// publish public key
router.post('/publish-public-key', authMiddleware, async (req: AuthRequest, res) => {
  const { publicKeyPem } = req.body;
  console.log(req.body);
  if (!publicKeyPem) return res.status(400).json({ message: 'publicKeyPem required' });
  await User.findByIdAndUpdate(req.user!.id, { publicKeyPem });
  return res.status(200).json({ message: 'ok' });
});


// Access public key
router.get('/public-key/:username', authMiddleware, async (req: AuthRequest, res) => {
  const u = await User.findOne({ username: req.params.username });
  if (!u || !u.publicKeyPem) return res.status(404).json({ message: 'Key not found' });
  return res.json({ publicKey: u.publicKeyPem });
});

export default router;