import { DiscordService } from "./services/discord.ts";

const init = () => {
  try {
    new DiscordService();
  } catch (error: any) {
    console.log("Unexpected Error: ", error?.message);
  }
};

init();
