import express from "express";
import { createServer as createViteServer } from "vite";
import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const db = new Database("sdr_history.db");

// Initialize DB
db.exec(`
  CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    company TEXT,
    campaign TEXT,
    pain_point TEXT,
    summary TEXT,
    message TEXT,
    match_score INTEGER,
    status TEXT DEFAULT 'Not Contacted',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.get("/api/history", (req, res) => {
    const rows = db.prepare("SELECT * FROM history ORDER BY created_at DESC").all();
    res.json(rows);
  });

  app.post("/api/history", (req, res) => {
    const { name, role, company, campaign, pain_point, summary, message, match_score } = req.body;
    const info = db.prepare(`
      INSERT INTO history (name, role, company, campaign, pain_point, summary, message, match_score)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(name, role, company, campaign, pain_point, summary, message, match_score);
    res.json({ id: info.lastInsertRowid });
  });

  app.patch("/api/history/:id", (req, res) => {
    const { status } = req.body;
    db.prepare("UPDATE history SET status = ? WHERE id = ?").run(status, req.params.id);
    res.json({ success: true });
  });

  app.get("/api/stats", (req, res) => {
    const total = db.prepare("SELECT COUNT(*) as count FROM history").get() as { count: number };
    const matches = db.prepare("SELECT COUNT(*) as count FROM history WHERE match_score >= 80").get() as { count: number };
    const sent = db.prepare("SELECT COUNT(*) as count FROM history WHERE status = 'Sent'").get() as { count: number };
    res.json({
      total: total.count,
      matches: matches.count,
      sent: sent.count
    });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static(path.join(__dirname, "dist")));
    app.get("*", (req, res) => {
      res.sendFile(path.join(__dirname, "dist", "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
