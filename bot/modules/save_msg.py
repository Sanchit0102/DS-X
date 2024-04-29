#!/usr/bin/env python3

import asyncio
from typing import Dict, Any, Optional, TypeVar, Union
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.filters import regex

import bot
from bot import bot, bot_name, user_data

T = TypeVar('T')

async def save_message(query: CallbackQuery) -> None:
    """
    Save the current message to a user's chat.

    If 'save_mode' is enabled, the message will be saved to the user's chat
    specified in 'ldump'. If 'save_mode' is not enabled, the message will be
    saved to the user's chat specified in 'udump'.

    If the user doesn't have any chats to save messages to, an error message
    will be displayed.

    If the user doesn't have sufficient permissions to copy the message,
    an error message will be displayed.

    If an error occurs while saving the message, a generic error message
    will be displayed.
    """
    user_id = query.from_user.id
    user_dict: Optional[Dict[str, Any]] = user_data.get(user_id)

    if not user_dict:
        await query.answer('User not found in the database. Please start the bot again.', show_alert=True)
        return

    if query.data == "save":
        ldump = user_dict.get('ldump', {})
        udump = user_dict.get('udump', {})

        if user_dict.get('save_mode'):
            try:
                usr = next(iter(ldump.values()))
            except StopIteration:
                await query.answer('No chats found to save messages to in save mode.', show_alert=True)
                return
        else:
            try:
                usr = next(iter(udump.values()))
            except StopIteration:
                await query.answer('No chats found to save messages to in normal mode.', show_alert=True)
                return

        try:
            message = query.message
            if not message:
                raise Exception('Message not found.')

            reply_markup = message.reply_markup
            BTN = reply_markup.inline_keyboard[:-1] if reply_markup else None
            keyboard_markup = InlineKeyboardMarkup(BTN) if BTN else None
            await message.copy(usr, reply_markup=keyboard_markup)
            await query.answer("Message/Media Successfully Saved !", show_alert=True)
        except Exception as e:
            if user_dict.get('save_mode'):
                if 'POST' in str(e):
                    await query.answer('Make Bot as Admin and give Post Permissions and Try Again', show_alert=True)
                else:
                    await query.answer('An error occurred while saving the message in save mode. Please try again later.', show_alert=True)
            else:
                try:
                    await query.answer(url=f"https://t.me/{bot_name}?start=start")
                    await message.copy(usr)
                except Exception as e:
                    await query.answer('An error occurred while saving the message in normal mode. Please try again later.', show_alert=True)
