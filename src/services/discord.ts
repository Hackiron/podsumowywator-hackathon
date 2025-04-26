import type { Channel } from "discord.js";
import dotenv from "dotenv";
import { DiscordHelper } from "../helpers/discord.ts";
import { delay, exceptionHandler } from "../utils/helpers.ts";
import { replaceUserMentionsWithUsernames } from "../utils/replaceUserMentionsWithUsernames.ts";
import { ClientService } from "./client.ts";
import { ContextService } from "./context.ts";

dotenv.config();
const { DISCORD_CLIENT_TOKEN, CHANNEL_ID, PODSUMOWYWATOR_ID } = process.env;

export class DiscordService {
  private client: any;

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
    );

    return messages;
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

              // Fetch all messages and format them using the helper method
              const messagesArray = await this.formatMessagesArray(thread);
              console.log("Thread messages:", messagesArray);

              // Call the summary API and respond with the result
              // const channelId = thread.parentId;
              const channelId = "799677088609075212"; // Temporary for testing use ogólne
              const agentAnswer = await this.sendMessagesToAgent(
                messagesArray,
                channelId,
                thread.id
              );
              await message.channel.send(agentAnswer);
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

            // Get the messages to summarize
            const messagesArray = await this.formatMessagesArray(thread);

            // const channelId = thread.parentId || message.channelId;
            const channelId = "799677088609075212"; // Temporary for testing use ogólne
            const agentAnswer = await this.sendMessagesToAgent(
              messagesArray,
              channelId,
              thread.id
            );
            await thread.send(agentAnswer);
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

  /**
   * Call the summary API with messages and return the summarized result
   */
  private async sendMessagesToAgent(
    messages: any[],
    channelId: string,
    threadId: string
  ): Promise<string> {
    const res = await fetch("http://localhost:8000/ruchniecie", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        messages,
        channelId,
        threadId,
      }),
    });

    const data = await res.json();
    return data.message;
  }

  private async formatMessagesArray(channel: any) {
    const messages = await channel.messages.fetch();
    let formattedMessages = [];

    // If this is a thread, get the parent message that started it
    if (channel.isThread()) {
      try {
        const parentMessage = await channel.fetchStarterMessage();
        if (parentMessage) {
          formattedMessages.push({
            username:
              parentMessage.author.globalName || parentMessage.author.username,
            message: replaceUserMentionsWithUsernames(
              parentMessage.content,
              this.client
            ),
            images: [],
          });
        }
      } catch (error) {
        console.error("Could not fetch starter message:", error);
      }
    }

    // Format thread messages into {username, message} structure
    const threadMessages = messages
      .map(
        (msg: {
          author: { globalName?: string; username: string };
          content: string;
        }) => ({
          username: msg.author.globalName || msg.author.username,
          message: replaceUserMentionsWithUsernames(msg.content, this.client),
        })
      )
      .filter(
        (msg: { username: string; message: string }) =>
          msg.message.trim() !== ""
      )
      .reverse(); // Reverse the array to have oldest messages first

    // Combine the parent message with thread messages
    return [...formattedMessages, ...threadMessages];
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
