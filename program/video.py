# Copyright (C) 2021 By Veez Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

import asyncio
import re

from config import ASSISTANT_NAME, BOT_USERNAME, IMG_1, IMG_2
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from youtubesearchpython import VideosSearch


def ytsearch(query):
    try:
        search = VideosSearch(query, limit=1)
        for r in search.result()["result"]:
            ytid = r["id"]
            if len(r["title"]) > 34:
                songname = r["title"][:70]
            else:
                songname = r["title"]
            url = f"https://www.youtube.com/watch?v={ytid}"
        return [songname, url]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["videoplay", f"videoplay@{BOT_USERNAME}"]) & other_filters)
async def vplay(c: Client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Tùy chỉnh", callback_data="cbmenu"),
                InlineKeyboardButton(text="Đóng", callback_data="cls"),
            ]
        ]
    )
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 Để sử dụng tôi, tôi cần phải là **Quản trị viên** với **quyền** sau đây:\n\n» ❌ __Xóa tin nhắn__\n» ❌ __Cấm người dùng__\n» ❌ __Thêm người dùng__\n» ❌ __Quản lý trò chuyện thoại__\n\nDữ liệu được **cập nhật** tự động sau khi bạn **nâng quyền hạn cho tôi**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "Thiếu quyền cần thiết:" + "\n\n» ❌ __Quản lý trò chuyện thoại__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "Thiếu quyền cần thiết:" + "\n\n» ❌ __Xóa tin nhắn__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("Thiếu quyền cần thiết:" + "\n\n» ❌ __Thêm người dùng__")
        return
    if not a.can_restrict_members:
        await m.reply_text("Thiếu quyền cần thiết:" + "\n\n» ❌ __Cấm người dùng__")
        return
    try:
        ubot = await user.get_me()
        b = await c.get_chat_member(chat_id, ubot.id)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **đã bị cấm trong nhóm** {m.chat.title}\n\n» **vui lòng bỏ cấm trợ lý trước nếu bạn muốn sử dụng bot này.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **Trợ lý không tham gia được**\n\n**Lý do**:{e}")
                return
        else:
            try:
                pope = await c.export_chat_invite_link(chat_id)
                pepo = await c.revoke_chat_invite_link(chat_id, pope)
                await user.join_chat(pepo.invite_link)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **Trợ lý không tham gia được**\n\n**Lý do**:{e}"
                )

    if replied:
        if replied.video or replied.document:
            loser = await replied.reply("📥 **Đang tải video...**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await loser.edit(
                        "» __Chỉ cho phép 720, 480, 360__ \n💡 **Hiện đang phát trực tuyến video ở độ phân giải 720p**"
                    )
            try:
                if replied.video:
                    songname = replied.video.file_name[:70]
                elif replied.document:
                    songname = replied.document.file_name[:70]
            except BaseException:
                songname = "@OWOHUB"

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Bản nhạc đã được thêm vào hàng đợi**\n\n🏷 **Tên:** [{songname}]({link})\n💭 **Nhóm:** `{chat_id}`\n🎧 **Người yêu cầu:** {requester}\n🔢 **Xếp hàng ở vị trí »** `{pos}`",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        dl,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_2}",
                    caption=f"💡 **Đã bắt đầu phát trực tuyến video.**\n\n🏷 **Tên:** [{songname}]({link})\n💭 **Nhóm:** `{chat_id}`\n💡 **Trạng thái:** `Đang phát trực tiếp`\n🎧 **Bởi:** {requester}",
                    reply_markup=keyboard,
                )
        else:
            if len(m.command) < 2:
                await m.reply(
                    "» Trả lời **tệp video** hoặc **đưa ra nội dung nào đó để tìm kiếm.**"
                )
            else:
                loser = await m.reply("🔎 **Tìm kiếm...**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                Q = 720
                amaze = HighQualityVideo()
                if search == 0:
                    await loser.edit("❌ **Không tim được kêt quả.**")
                else:
                    songname = search[0]
                    url = search[1]
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await loser.edit(f"❌ Vấn đề yt-dl được phát hiện\n\n» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Video", Q
                            )
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_1}",
                                caption=f"💡 **Bản nhạc đã được thêm vào hàng đợi**\n\n🏷 **Tên:** [{songname}]({url})\n💭 **Chat:** `{chat_id}`\n🎧 **Bởi:** {requester}\n🔢 **Xếp hàng vị trí »** `{pos}`",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioVideoPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                        amaze,
                                    ),
                                    stream_type=StreamType().pulse_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                                await loser.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=f"{IMG_2}",
                                    caption=f"💡 **Đã bắt đầu phát trực tuyến video.**\n\n🏷 **Tiêu đề:** [{songname}]({url})\n💭 **Chat:** `{chat_id}`\n💡 **Trạng thái:** `Đang trực tiếp`\n🎧 **@owohub - ** {requester}",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await m.reply_text(f"🚫 Lỗi: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "» Trả lời một **tệp video** hoặc **đưa ra một cái gì đó để tìm kiếm.**"
            )
        else:
            loser = await m.reply("🔎 **Tìm kiếm...**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            amaze = HighQualityVideo()
            if search == 0:
                await loser.edit("❌ **Không tim được kêt quả.**")
            else:
                songname = search[0]
                url = search[1]
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await loser.edit(f"❌ Vấn đề yt-dl được phát hiện\n\n» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await loser.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=f"{IMG_1}",
                            caption=f"💡 **Bản nhạc đã được thêm vào hàng đợi**\n\n🏷 **Tên:** [{songname}]({url})\n💭 **Chat:** `{chat_id}`\n🎧 **@owohub :** {requester}\n🔢 **Tại vị trí »** `{pos}`",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                    amaze,
                                ),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=f"{IMG_2}",
                                caption=f"💡 **Bắt đầu phát trực tuyến video.**\n\n🏷 **Tên:** [{songname}]({url})\n💭 **Chat:** `{chat_id}`\n💡 **Trạng thái:** `Đang trực tiếp`\n🎧 **Request by:** {requester}",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await m.reply_text(f"🚫 error: `{ep}`")


@Client.on_message(command(["vstream", f"vstream@{BOT_USERNAME}"]) & other_filters)
async def vstream(c: Client, m: Message):
    m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Tùy chỉnh", callback_data="cbmenu"),
                InlineKeyboardButton(text="Đóng", callback_data="cls"),
            ]
        ]
    )
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"💡 Để sử dụng tôi, tôi cần phải là **Quản trị viên** với **quyền** sau đây:\n\n» ❌ __Xóa tin nhắn__\n» ❌ __Cấm người dùng__\n» ❌ __Thêm người dùng__\n» ❌ __Quản lý trò chuyện thoại__\n\nDữ liệu được **cập nhật** tự động sau khi bạn **quảng cáo cho tôi**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "Thiếu quyền cần thiết:" + "\n\n» ❌ __Manage voice chat__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "Thiếu quyền cần thiết:" + "\n\n» ❌ __Delete messages__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("Thiếu quyền cần thiết:" + "\n\n» ❌ __Add users__")
        return
    if not a.can_restrict_members:
        await m.reply_text("Thiếu quyền cần thiết:" + "\n\n» ❌ __Ban users__")
        return
    try:
        ubot = await user.get_me()
        b = await c.get_chat_member(chat_id, ubot.id)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **bị cấm trong nhóm** {m.chat.title}\n\n» **Bỏ cấm userbot trước nếu bạn muốn sử dụng bot này.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"❌ **Trợ lý không tham gia được**\n\n**Lý do**:{e}")
                return
        else:
            try:
                pope = await c.export_chat_invite_link(chat_id)
                pepo = await c.revoke_chat_invite_link(chat_id, pope)
                await user.join_chat(pepo.invite_link)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"❌ **Trợ lý không tham gia được**\n\n**Lý do**:{e}"
                )

    if len(m.command) < 2:
        await m.reply("» Cho tôi một liên kết trực tiếp / m3u8 url / liên kết youtube để phát trực tiếp.")
    else:
        if len(m.command) == 2:
            link = m.text.split(None, 1)[1]
            Q = 720
            loser = await m.reply("🔄 **Luồng xử lý...**")
        elif len(m.command) == 3:
            op = m.text.split(None, 1)[1]
            link = op.split(None, 1)[0]
            quality = op.split(None, 1)[1]
            if quality == "720" or "480" or "360":
                Q = int(quality)
            else:
                Q = 720
                await m.reply(
                    "» __Chỉ cho phép 720, 480, 360__ \n💡 **Hiện đang phát trực tuyến video trong 720p**"
                )
            loser = await m.reply("🔄 **processing stream...**")
        else:
            await m.reply("**/vstream {link} {720/480/360}**")

        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, link)
        if match:
            veez, livelink = await ytdl(link)
        else:
            livelink = link
            veez = 1

        if veez == 0:
            await loser.edit(f"❌ yt-dl issues detected\n\n» `{ytlink}`")
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{IMG_1}",
                    caption=f"💡 **Bản nhạc đã được thêm vào hàng đợi**\n\n💭 **Chat:** `{chat_id}`\n🎧 **@owohub:** {requester}\n🔢 **Vị trí »** `{pos}`",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                try:
                    await call_py.join_group_call(
                        chat_id,
                        AudioVideoPiped(
                            livelink,
                            HighQualityAudio(),
                            amaze,
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                    await loser.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_photo(
                        photo=f"{IMG_2}",
                        caption=f"💡 **[Video phát trực tiếp]({link}) bắt đầu.**\n\n💭 **Chat:** `{chat_id}`\n💡 **Trạng thái:** `Đang trực tiếp`\n🎧 **@owohub:** {requester}",
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await m.reply_text(f"🚫 error: `{ep}`")
