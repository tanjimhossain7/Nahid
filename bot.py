import discord
from discord.ext import commands
import openai

# OpenAI API Key
openai.api_key = ""
# Configure intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Create the bot instance with the configured intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Keywords to detect ticket advertisements
TICKET_KEYWORDS = ["selling", "buying", "reselling", "tickets", "ticket sale"]

# AI-based ticket advertisement detection function
async def is_ticket_ad_with_ai(message_content):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=(
                f"Analyze the following message and determine if it is an advertisement for selling or buying tickets. "
                f"Consider mentions of selling, buying, reselling tickets, or event-related ticket discussions. "
                f"Respond with 'Yes' if it's an advertisement for ticket sales or purchases and 'No' if it's a casual discussion or unrelated.\n\n"
                f"Message: {message_content}"
            ),
            max_tokens=10,
            temperature=0
        )
        return response["choices"][0]["text"].strip().lower() == "yes"
    except Exception as e:
        print(f"Error during AI detection: {e}")
        return False

# Combined detection function (Keywords + AI)
async def is_ticket_ad(message_content):
    # Check if the message contains relevant keywords
    if any(keyword in message_content.lower() for keyword in TICKET_KEYWORDS):
        # Use AI for final validation
        return await is_ticket_ad_with_ai(message_content)
    return False

# Event: When the bot is ready
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

# Event: Monitor messages for ticket advertisements
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Check if the message advertises tickets
    if await is_ticket_ad(message.content):
        # Delete the message
        await message.delete()

        # Notify the chat that a ticket advertisement was detected
        notification = (
            f"⚠️ A potential ticket advertisement from {message.author.mention} "
            f"has been detected and removed. Advertising tickets is not allowed in this server."
        )
        await message.channel.send(notification)

    # Ensure other commands still work
    await bot.process_commands(message)

# Command: Test AI ticket detection
@bot.command()
async def test_ticket(ctx, *, message):
    is_ad = await is_ticket_ad(message)
    response = "This is likely an advertisement for tickets." if is_ad else "This does not appear to be an advertisement for tickets."
    await ctx.send(response)

# Command: Add a new keyword to the ticket detection list
@bot.command()
@commands.has_permissions(manage_messages=True)
async def add_ticket_keyword(ctx, *, keyword):
    TICKET_KEYWORDS.append(keyword.lower())
    await ctx.send(f"✅ Keyword '{keyword}' has been added to the ticket detection list.")

# Command: List all ticket detection keywords
@bot.command()
async def list_ticket_keywords(ctx):
    keywords = ", ".join(TICKET_KEYWORDS)
    await ctx.send(f"📜 Current ticket-related keywords: {keywords}")

# Command: Remove a keyword from the ticket detection list
@bot.command()
@commands.has_permissions(manage_messages=True)
async def remove_ticket_keyword(ctx, *, keyword):
    if keyword.lower() in TICKET_KEYWORDS:
        TICKET_KEYWORDS.remove(keyword.lower())
        await ctx.send(f"✅ Keyword '{keyword}' has been removed from the ticket detection list.")
    else:
        await ctx.send(f"❌ Keyword '{keyword}' is not in the detection list.")

# Run the bot
bot.run("")
