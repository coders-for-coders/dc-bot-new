import random
from discord.ext import commands

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dice", description="Roll dice like 2d6")
    async def dice(self, ctx: commands.Context, dice: str = "1d6"):
        try:
            rolls, limit = map(int, dice.lower().split("d"))

            if rolls <= 0 or limit <= 0:
                return await ctx.send("Please use positive numbers, e.g. `2d6`.")

            results = [random.randint(1, limit) for _ in range(rolls)]
            await ctx.send(f"🎲 Rolled {dice}: {', '.join(map(str, results))}")

        except ValueError:
            await ctx.send("Invalid format! Use NdM (e.g. `2d6`).")


    @commands.command(name="coinflip", aliases= ["cf"], description="Flip a coin and optionally guess the result")
    async def coinflip(self, ctx, *, guess: str = None):
        # Normalize and map common inputs
        def normalize_choice(text: str):
            text = text.strip().lower()
            mapping = {
                "h": "heads", "head": "heads", "heads": "heads",
                "t": "tails", "tail": "tails", "tails": "tails"
            }
            return mapping.get(text)

        user_guess = normalize_choice(guess) if guess else None
        if guess and user_guess is None:
            await ctx.send("❌ Please choose `heads` or `tails` (you can also use `h/head` or `t/tail`).")
            return

        # Flip the coin (result is independent of the guess)
        result = random.choice(["heads", "tails"])
        emoji = "🙂" if result == "heads" else "🙃"

        if user_guess:
            if user_guess == result:
                await ctx.send(f"🪙 The coin landed on **{result.capitalize()}** {emoji}\n✅ You guessed right!")
            else:
                await ctx.send(f"🪙 The coin landed on **{result.capitalize()}** {emoji}\n❌ Better luck next time!")
        else:
            await ctx.send(f"🪙 The coin landed on **{result.capitalize()}** {emoji}")

    @commands.command(name="rps", description="Play Rock Paper Scissors")
    async def rps(self, ctx: commands.Context, choice: str):
        options = ["rock", "paper", "scissors"]
        bot_choice = random.choice(options)
        
        if choice not in options:
            await ctx.send(f"❌ **{choice}** is not a valid choice. Pick rock, paper, or scissors.")
            return
        
        if choice.lower() == bot_choice:
            result = "It's a tie!"
        elif (choice.lower(), bot_choice) in [("rock","scissors"),("paper","rock"),("scissors","paper")]:
            result = "You win!"
        else:
            result = "I win!"
        await ctx.send(f"You chose **{choice}**, I chose **{bot_choice}**. {result}")

async def setup(bot):
    await bot.add_cog(Games(bot))