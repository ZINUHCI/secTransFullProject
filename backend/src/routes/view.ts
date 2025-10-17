
import { Router } from "express"
import { User } from "@src/models/User";
import { authMiddleware, AuthRequest } from "@src/utils/auth";

const router = Router()

router.get('/users', authMiddleware, async (req: AuthRequest, res) => {
  const users = await User.find({}).select("username");
  return res.status(200).json({users});
});

export default router;