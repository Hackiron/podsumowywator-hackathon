import { createServer } from "./server.ts";
import { DiscordService } from "./services/discord.ts";

const init = () => {
  const discordService = new DiscordService();

  createServer(discordService);
};

init();
