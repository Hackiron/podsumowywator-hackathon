import dotenv from "dotenv";
// import { Message, OpenAi } from "./openai.js";
import { DiscordHelper } from "../helpers/discord.ts";
import { exceptionHandler } from "../utils/helpers.ts";
import { ClientService } from "./client.ts";
import { ContextService } from "./context.ts";

dotenv.config();
const { DISCORD_CLIENT_TOKEN, CHANNEL_ID, PODSUMOWYWATOR_ID } = process.env;

// const openai = new OpenAi();

export class DiscordService {
  private client: any;
  // private systemContext: Message;
  constructor() {
    const contextService = new ContextService([]);
    const clientService = new ClientService();
    this.client = clientService.getClient();
    const discordHelper = new DiscordHelper(this.client);

    // this.systemContext = {
    //   role: "system",
    //   content:
    //     "Podsumuj Podane wiadomości. Z podanych wiadomości wyciągnij to o czym  była dyskusja i podsumuj. Podsumuj krótko zwięźle i na temat.",
    // };

    this.client.on("ready", async () => {
      const channel = this.client.channels.cache.get(CHANNEL_ID);

      // TESTOWE POBIERANIE WIADOMOŚCI
      const messages = await discordHelper.fetchMessages(
        CHANNEL_ID,
        "2025-04-13T00:00:00Z",
        "2025-04-14T00:00:00Z"
      );

      console.log(
        "messages: ",
        messages.map((msg: any) => msg.content)
      );

      try {
        console.log(`Logged in as ${this.client.user.tag}!`);
        channel.send(`Elo, jestem gotowy do podsumowywania!`);
      } catch (error: any) {
        return exceptionHandler(error, channel);
      }
    });

    this.client.on("messageCreate", async (message: any) => {
      // Skip messages from the bot itself
      if (message.author.username === "Podsumowywator") return;

      // Check if message is in a thread
      if (message.channel.isThread()) {
        // Check if the thread was created by the bot
        const thread = message.channel;
        const threadStarter = await thread.fetchStarterMessage();

        if (threadStarter && threadStarter.author.id === this.client.user.id) {
          // This is a reply in a thread created by the bot
          console.log(`Message in bot thread: ${message.content}`);
          try {
            message.channel.sendTyping();
            // Handle thread reply here
          } catch (error: any) {
            return exceptionHandler(error, message);
          }
        }
      }
      // Not in a thread, check for mentions
      else if (
        message.content.includes(PODSUMOWYWATOR_ID) ||
        message.mentions?.users?.has(this.client.user.id) ||
        message.mentions?.repliedUser?.username === "Podsumowywator"
      ) {
        try {
          message.channel.sendTyping();

          // Create a thread from this message
          const thread = await message.startThread({
            name: `Podsumowanie: ${message.content
              .substring(0, 50)
              .replace(`<@${this.client.user.id}>`, "")}${
              message.content.length > 50 ? "..." : ""
            }`,
            autoArchiveDuration: 1440, // Auto archive after 24 hours (in minutes)
          });

          await thread.send("Rozpoczynam podsumowanie w tym wątku!");
        } catch (error: any) {
          return exceptionHandler(error, message);
        }
      }
    });

    this.client.login(DISCORD_CLIENT_TOKEN);
  }

  userResponseFactory(message: any) {
    return {
      username: message.author.globalName,
      message: message.content,
    };
  }

  destroy() {
    this.client.destroy();
  }
}
