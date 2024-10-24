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

intents = discord.Intents.default()
intents.members = True  # メンバー関連のインテントを有効化
intents.voice_states = True  # ボイスステートの取得を有効化

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.slash_command(guild_ids=[guild_id])
async def neru(ctx: discord.ApplicationContext):
    # ユーザーがボイスチャットに入っているかを確認
    if ctx.author.voice and ctx.author.voice.channel:
        vc_channel = ctx.author.voice.channel
        
        # 実際にボイスチャットに接続しているメンバーを取得
        members = vc_channel.members
        num_members = len(members)
        
        # デバッグ: チャンネルとメンバー情報を出力
        print(f"ボイスチャット '{vc_channel.name}' （ID: {vc_channel.id}）のメンバー: {[member.name for member in members]}")
        print(f"ボイスチャット '{vc_channel.name}' の参加人数: {num_members}")
        
        for member in members:
            print(f"メンバー名: {member.name}, ステータス: {member.status}, ボイス接続状態: {member.voice}")
        
        # ボイスチャットに誰もいない場合
        if num_members == 0:
            await ctx.respond("ボイスチャットに誰もいません。")
            return

        # チャンネルごとに投票状況を管理
        if vc_channel.id not in vote_counts:
            vote_counts[vc_channel.id] = {"votes": set(), "total": num_members}
            print(f"新しい投票カウントを作成しました。チャンネルID: {vc_channel.id}, 合計メンバー数: {num_members}")
        
        # 既に投票しているか確認
        if ctx.author.id in vote_counts[vc_channel.id]["votes"]:
            await ctx.respond("既に投票しています。")
            print(f"{ctx.author.name} は既に投票しています。")
            return

        # 投票をカウント
        vote_counts[vc_channel.id]["votes"].add(ctx.author.id)
        votes_count = len(vote_counts[vc_channel.id]["votes"])

        # 必要な投票数を調整（2人の場合は1票、それ以外は (num_members // 2) + 1）
        if num_members == 2:
            required_votes = 1
        else:
            required_votes = (num_members // 2) + 1

        # ログ: 投票数の状況を出力
        vote_usernames = []
        for user_id in vote_counts[vc_channel.id]['votes']:
            user = bot.get_user(user_id)
            if user is None:
                try:
                    # 非同期でユーザー情報をAPIから取得
                    user = await bot.fetch_user(user_id)
                    if user:
                        vote_usernames.append(user.name)
                    else:
                        vote_usernames.append(f"Unknown user ID: {user_id}")
                except discord.NotFound:
                    vote_usernames.append(f"Unknown user ID: {user_id}")
            else:
                vote_usernames.append(user.name)

        print(f"現在の投票者: {vote_usernames}")
        await ctx.respond(f"投票が1件入りました。現在 {votes_count} 票です。{required_votes} 票で全員が退出します。")

        # 必要な投票数に達した場合
        if votes_count >= required_votes:
            await ctx.respond("過半数の投票がありました！全員をボイスチャットから退出させます。")
            
            # ログ: 全員退出させる前にメンバーリストを出力
            print(f"投票によって退出させるメンバー: {[member.name for member in members]}")

            # チャンネル内の全員を退出させる
            for member in members:
                # メンバーが現在のチャンネルにまだいるか確認して退出させる
                if member.voice and member.voice.channel == vc_channel:
                    print(f"{member.name} をボイスチャットから退出させます。")
                    await member.move_to(None)

            # コンソールに全員が退出したことを表示
            print(f"全員がボイスチャット '{vc_channel.name}' から退出しました。")

            # 投票カウントをリセット
            del vote_counts[vc_channel.id]
            print(f"投票カウントをリセットしました。チャンネルID: {vc_channel.id}")

    else:
        await ctx.respond("まずはボイスチャットに参加してください。")
        print(f"{ctx.author.name} はボイスチャットに参加していません。")

bot.run(token)
