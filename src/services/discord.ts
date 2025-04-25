import dotenv from "dotenv";
import { Message, OpenAi } from "./openai.js";
import { ContextService } from "./context.js";
import { exceptionHandler } from "../utils/helpers.js";
import { ClientService } from "./client.js";
import { DiscordHelper } from "../helpers/discord.js";

dotenv.config();
const { DISCORD_CLIENT_TOKEN, CHANNEL_ID, PODSUMOWYWATOR_ID } = process.env;

const openai = new OpenAi();

export class DiscordService {
  private client: any;
  private systemContext: Message;
  constructor() {
    const contextService = new ContextService([]);
    const clientService = new ClientService();
    this.client = clientService.getClient();
    const discordHelper = new DiscordHelper(this.client);

    this.systemContext = {
      role: "system",
      content:
        "Podsumuj Podane wiadomości. Z podanych wiadomości wyciągnij to o czym  była dyskusja i podsumuj. Podsumuj krótko zwięźle i na temat.",
    };

    this.client.on("ready", async () => {
      const channel = this.client.channels.cache.get(CHANNEL_ID);
      
      // TESTOWE POBIERANIE WIADOMOŚCI
      const messages = await discordHelper.fetchMessages(
        CHANNEL_ID,
        "2025-04-13T00:00:00Z",
        "2025-04-14T00:00:00Z"
      );

      console.log("messages: ", messages.map((msg: any) => msg.content));

      try {
        console.log(`Logged in as ${this.client.user.tag}!`);
        channel.send(`Dzień dobry, jestem gotowy do podsumowywania!`);
      } catch (error: any) {
        return exceptionHandler(error, channel);
      }
    });

    this.client.on("messageCreate", async (message: any) => {
      // Zapisz do kontekstu 6 ostatnich wiadomości.
      const userMessage = this.userResponseFactory(message);
      contextService.pushWithLimit(userMessage);

      console.log("last channel messages: ", contextService.getContext());
      if (
        message.content.includes(PODSUMOWYWATOR_ID) ||
        message.mentions?.repliedUser?.username === "Podsumowywator"
      ) {
        if (message.author.username !== "Podsumowywator") {
          try {
            message.channel.sendTyping();
            const assResponse = await openai.contextInteract([
              this.systemContext,
              ...contextService.getContext(),
            ]);

            assResponse && contextService.pushWithLimit(assResponse);

            const responseContent = `${assResponse.content.substring(0, 1950)}`;
            message.reply(responseContent);
          } catch (error: any) {
            return exceptionHandler(error, message);
          }
        }
      }
    });

    this.client.login(DISCORD_CLIENT_TOKEN);
  }

  userResponseFactory(message: any) {
    const modifiedUserResponseContent = `${message.author.globalName}: ${message.content}`;
    return openai.messageFactory(modifiedUserResponseContent);
  }

  destroy() {
    this.client.destroy();
  }
}
