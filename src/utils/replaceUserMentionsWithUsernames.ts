export function replaceUserMentionsWithUsernames(
  content: string,
  client: any
): string {
  return content.replace(/<@!?(\d+)>/g, (match, userId) => {
    const user = client.users.cache.get(userId);
    return user ? user.globalName || user.username : match;
  });
}
