import { Message } from "discord.js";

export const exceptionHandler = (error: any, message: any) => {
  console.log("err: ", error?.message);

  message.reply(
    `Przykro mi, nie mogę teraz tego zrobić... POWÓD: ${error?.message?.substring(
      0,
      1800
    )}
      Zapytaj mnie proszę ponownie.`
  );
};

export const delay = (ms: number) => {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

export const formatMessage = (message: Message) => ({
    id: message.id,
    message: message.content,
    username: message.author.username,
})
