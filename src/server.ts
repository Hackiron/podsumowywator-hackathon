import axios from "axios"; // Add axios for HTTP requests
import express from "express";
import morgan from "morgan";
import { logger } from "./logger.ts";
import { DiscordService } from "./services/discord.ts";
import { formatMessage } from "./utils/helpers.ts";

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
    },
  };

  // Use morgan middleware with our custom stream
  app.use(morgan("combined", { stream: morganStream }));

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
        logger.info(`Fetched ${messages.length} messages`);
        const formatted = messages.map(formatMessage);
        res.json(formatted);
      })
      .catch((error) => {
        logger.error("Error fetching messages:", error);
        res.status(500).json({ error: "Failed to fetch messages" });
      });
  });

  app.post("/nudes", async (req, res) => {
    if (!req.body.url) {
      return res
        .status(400)
        .json({ error: "Missing required parameter: url in request body" });
    }

    const imageUrl = req.body.url as string;

    // Check if the URL is from Discord's CDN
    if (
      !imageUrl.includes("cdn.discordapp.com") &&
      !imageUrl.includes("media.discordapp.net")
    ) {
      return res.status(400).json({ error: "URL must be from Discord's CDN" });
    }

    try {
      logger.info(`Downloading image from: ${imageUrl}`);

      // Use Discord bot's authorization for private images
      const headers = {
        Authorization: `Bot ${process.env.DISCORD_CLIENT_TOKEN}`,
      };

      // Download the image
      const response = await axios.get(imageUrl, {
        headers,
        responseType: "arraybuffer",
      });

      // Convert the image to base64
      const base64Image = Buffer.from(response.data).toString("base64");

      // Get content type from headers
      const contentType = response.headers["content-type"];

      logger.info(`Successfully downloaded and converted image to base64`);

      // Return the base64 encoded image with its content type
      res.json({
        base64: base64Image,
        contentType,
        originalUrl: imageUrl,
      });
    } catch (error) {
      logger.error("Error downloading image:", error);
      res.status(500).json({ error: "Failed to download image" });
    }
  });

  // Start the server
  const server = app.listen(PORT, () => {
    logger.info(`Server is running on port ${PORT}`);
  });

  return {
    server,
  };
}
