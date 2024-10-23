import os
import dotenv
import discord
from discord.ext import commands

# アクセストークンとギルドIDを設定
dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))
guild_id = int(os.getenv("GUILD_ID"))

bot = discord.Bot()

# 辞書でボイスチャットごとの投票状況を管理
vote_counts = {}

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[guild_id])
async def neru(ctx: discord.ApplicationContext):
    # ユーザーがボイスチャットに入っているかを確認
    if ctx.author.voice and ctx.author.voice.channel:
        vc_channel = ctx.author.voice.channel
        members = vc_channel.members
        num_members = len(members)
        
        # ボイスチャットに誰もいない場合
        if num_members == 0:
            await ctx.respond("ボイスチャットに誰もいません。")
            return

        # コンソールにボイスチャットの人数を表示
        print(f"ボイスチャット '{vc_channel.name}' の参加人数: {num_members}")

        # チャンネルごとに投票状況を管理
        if vc_channel.id not in vote_counts:
            vote_counts[vc_channel.id] = {"votes": set(), "total": num_members}
        
        # 既に投票しているか確認
        if ctx.author.id in vote_counts[vc_channel.id]["votes"]:
            await ctx.respond("既に投票しています。")
            return

        # 投票をカウント
        vote_counts[vc_channel.id]["votes"].add(ctx.author.id)
        votes_count = len(vote_counts[vc_channel.id]["votes"])

        # 必要な投票数を調整（2人の場合は1票、それ以外は (num_members // 2) + 1）
        if num_members == 2:
            required_votes = 1
        else:
            required_votes = (num_members // 2) + 1

        # コンソールに投票状況を表示
        print(f"現在の投票数: {votes_count}, 必要な投票数: {required_votes}")

        await ctx.respond(f"投票が1件入りました。現在 {votes_count} 票です。{required_votes} 票で全員が退出します。")

        # 必要な投票数に達した場合
        if votes_count >= required_votes:
            await ctx.respond("過半数の投票がありました！全員をボイスチャットから退出させます。")
            
            # チャンネル内の全員を退出させる
            for member in members:
                await member.move_to(None)

            # コンソールに全員が退出したことを表示
            print(f"全員がボイスチャット '{vc_channel.name}' から退出しました。")

            # 投票カウントをリセット
            del vote_counts[vc_channel.id]

    else:
        await ctx.respond("まずはボイスチャットに参加してください。")

bot.run(token)
