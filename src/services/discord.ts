import dotenv from "dotenv";
import { DiscordHelper } from "../helpers/discord.ts";
import { delay, exceptionHandler } from "../utils/helpers.ts";
import { ClientService } from "./client.ts";
import { ContextService } from "./context.ts";
import type { Channel, Client } from "discord.js";
import { pick } from 'ramda';

dotenv.config();
const { DISCORD_CLIENT_TOKEN, CHANNEL_ID, PODSUMOWYWATOR_ID } = process.env;

export class DiscordService {
  private client: Client;

  private discordHelper: DiscordHelper;

  private isReady: boolean = false;

  async fetchMessages(channelId: string, startDate: string, endDate: string) {
    while (!this.isReady) {
      console.log("Waiting for Discord client to be ready...");
      await delay(1000);
    }

    const messages = await this.discordHelper.fetchMessages(
      channelId,
      startDate,
      endDate
    )

    const picked = messages.map(m => pick(['content'], m))

    return picked;
  }

  constructor() {
    console.log("inits");
    const contextService = new ContextService([]);
    const clientService = new ClientService();
    this.client = clientService.getClient();
    this.discordHelper = new DiscordHelper(this.client);

    console.log("listeners");
    if (JSON.parse(process.env.ENABLE_INITIAL_MESSAGE)) {
      console.log("initial message enabled");
      this.client.on("ready", async () => {
        const channel = this.client.channels.cache.get(CHANNEL_ID) as Channel;

        try {
          console.log(`Logged in as ${this.client.user.tag}!`);
          channel.send(`Elo, jestem gotowy do podsumowywania!`);
        } catch (error: any) {
          return exceptionHandler(error, channel);
        }
      });
    }

    if (JSON.parse(process.env.ENABLE_RESPONDING)) {
    this.client.on("messageCreate", async (message: any) => {
      // Skip messages from the bot itself
      if (message.author.username === "Podsumowywator") return;

      // Check if message is in a thread
      if (message.channel.isThread()) {
        const thread = message.channel;

        // Check if the thread owner is the bot
        // In Discord.js, the thread owner is the one who created the thread
        const threadOwner = thread.ownerId;

        // Ensure the bot only responds to user messages in its own threads
        if (
          threadOwner === this.client.user.id &&
          message.author.id !== this.client.user.id
        ) {
          // This is a reply in a thread created by the bot
          try {
            message.channel.sendTyping();
            // Respond to the message in the thread
            await message.channel.send("Odpowiadam w wątku");
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
    }

    console.log("login");

    this.client.login(DISCORD_CLIENT_TOKEN);

    console.log("after login");

    this.isReady = true;
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
