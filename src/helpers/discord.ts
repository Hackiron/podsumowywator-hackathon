import { Client, TextChannel, Message } from 'discord.js';
import dotenv from "dotenv";

dotenv.config();
const { DISCORD_CLIENT_TOKEN } = process.env;

export class DiscordHelper {
  private client: Client;

  constructor(client: Client) {
    this.client = client
    this.client.login(DISCORD_CLIENT_TOKEN).catch((err) => {
      console.error('Failed to login to Discord:', err);
    });
  }

  /**
   * Fetches messages from a specified channel within a given time range.
   * @param channelId ID of the Discord channel.
   * @param startDate Start date (ISO string).
   * @param endDate End date (ISO string).
   * @returns Array of messages from the specified time period.
   */
  async fetchMessages(channelId: string | undefined, startDate: string, endDate: string): Promise<Message[]> {
    console.log('Fetching messages...');
    if (!channelId) {
      throw new Error('Channel ID is required.');
    }
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      throw new Error('Invalid date format. Use ISO string format.');
    }

    const channel = this.client.channels.cache.get(channelId);

    if (!channel || !(channel instanceof TextChannel)) {
      throw new Error('Channel not found or is not a text channel.');
    }

    const messages: Message[] = [];
    let lastMessageId: string | undefined;

    while (true) {
      const fetchedMessages = await channel.messages.fetch({ limit: 100, before: lastMessageId });
      if (fetchedMessages.size === 0) break;

      for (const message of fetchedMessages.values()) {
        const messageDate = message.createdAt;
        if (messageDate >= start && messageDate <= end) {
          messages.push(message);
        } else if (messageDate < start) {
          return messages; // If messages are older than startDate, stop fetching.
        }
      }

      lastMessageId = fetchedMessages.last()?.id;
    }

    return messages;
  }
}

