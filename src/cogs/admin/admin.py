import discord
from discord.ext import commands
from core.cog import Cog
from main import MyBot

class Admin(Cog):
    def __init__(self, bot: MyBot):
        self.bot=bot

    # Hidden means it won't show up on the default help.
    @commands.command(name="load", hidden=True)
    @commands.has_permissions(administrator=True)    
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        """Loads a module. Use dot path, e.g. cogs.owner"""
        try:
            await self.bot.load_extension(f"cogs.{cog}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Load Failed",
                description=f"**Error:** `{type(e).__name__}`\n{e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        else:
            embed = discord.Embed(
                title="✅ Load Success",
                description=f"Module `cogs.{cog}` loaded successfully.",
                color=discord.Color.green()
            )
            await ctx.message.reply(embed=embed, delete_after=10)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)    
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Unload Failed",
                description=f"**Error:** `{type(e).__name__}`\n{e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        else:
            embed = discord.Embed(
                title="✅ Unload Success",
                description=f"Module `cogs.{cog}` unloaded successfully.",
                color=discord.Color.green()
            )
            await ctx.reply(embed=embed, delete_after=10)

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)    
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        """Reloads a module."""
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await self.bot.load_extension(f"cogs.{cog}")
            await self.bot.tree.sync()
        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"**Error:** `{type(e).__name__}`\n{e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        else:
            embed = discord.Embed(
                title="✅ Reload Success",
                description=f"Module `cogs.{cog}` reloaded successfully.",
                color=discord.Color.green()
            )
            await ctx.message.reply(embed=embed, delete_after=10)
        
async def setup(bot):
    await bot.add_cog(Admin(bot))