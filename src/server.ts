import express from "express";
import { DiscordService } from "./services/discord.ts";
import { logger } from "./logger.ts";
import morgan from "morgan";

export function createServer(discordService: DiscordService) {
  const app = express();
  const PORT = process.env.PORT || 3000;

  app.use(express.json());

  // Create a morgan stream that writes to our winston logger
  const morganStream = {
    write: (message: string) => {
      // Remove the newline character that morgan adds
      const trimmedMessage = message.trim();
      logger.info(trimmedMessage);
    }
  };

  // Use morgan middleware with our custom stream
  app.use(morgan('combined', { stream: morganStream }));

  // Define your routes here
  app.get("/", (req, res) => {
    res.send("Hello World!");
  });

  app.get("/matchenatinderze", (req, res) => {
    if (!req.query.channelId || !req.query.startDate || !req.query.endDate) {
      return res
        .status(400)
        .json({ error: "parameters: channelId, startDate, endDate" });
    }

    discordService
      .fetchMessages(
        req.query.channelId as string,
        req.query.startDate as string,
        req.query.endDate as string
      )
      .then((messages) => {
        res.json(messages);
      })
      .catch((error) => {
        logger.error("Error fetching messages:", error);
        res.status(500).json({ error: "Failed to fetch messages" });
      });
  });

  // Start the server
  const server = app.listen(PORT, () => {
    logger.info(`Server is running on port ${PORT}`);
  });

  return {
    server,
  };
}
