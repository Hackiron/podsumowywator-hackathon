import { DiscordService } from "./services/discord.js";

const init = () => {
  try {
    new DiscordService();
  } catch (error: any) {
    console.log("Unexpected Error: ", error?.message);
  }
};

init();
