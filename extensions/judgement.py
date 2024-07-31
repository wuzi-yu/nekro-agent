from typing import List

from nonebot.adapters.onebot.v11 import Bot

from nekro_agent.core import logger
from nekro_agent.core.bot import get_bot
from nekro_agent.schemas.agent_ctx import AgentCtx
from nekro_agent.services.chat import chat_service
from nekro_agent.services.extension import ExtMetaData
from nekro_agent.tools.collector import MethodType, agent_collector

from .basic import send_msg_text

__meta__ = ExtMetaData(
    name="judgement",
    description="Nekro-Agent 风纪委员 (群管工具集)",
    version="0.1.0",
    author="KroMiose",
    url="https://github.com/KroMiose/nekro-agent",
)


@agent_collector.mount_method(MethodType.BEHAVIOR)
async def mute_user(_ctx: AgentCtx, chat_key: str, user_qq: str, duration: int) -> str:
    """禁言用户

    Args:
        chat_key (str): 聊天的唯一标识符
        user_qq (str): 被禁言的用户的QQ号
        duration (int): 禁言时长，单位为秒，设置为 0 则解除禁言.

    Returns:
        str: 操作结果
    """
    bot: Bot = get_bot()
    chat_type, chat_id = chat_key.split("_")
    if chat_type != "group":
        logger.error(f"禁言功能不支持 {chat_type} 的会话类型")
        return f"禁言功能不支持 {chat_type} 的会话类型"

    if duration > 60 * 60 * 24:
        return f"尝试禁言用户 [qq:{user_qq}] {duration} 秒失败: 禁言时长不能超过一天"
    try:
        await bot.set_group_ban(group_id=int(chat_id), user_id=int(user_qq), duration=duration)
    except Exception as e:
        logger.error(f"[{chat_key}] 禁言用户 [qq:{user_qq}] {duration} 秒失败: {e}")
        return f"[{chat_key}] 禁言用户 [qq:{user_qq}] {duration} 秒失败: {e}"
    else:
        logger.info(f"[{chat_key}] 已禁言用户 [qq:{user_qq}] {duration} 秒")
        return f"[{chat_key}] [qq:{user_qq}] {duration} 秒"


# @agent_collector.mount_method()   # 协议端暂不支持且 Bot 需要群主权限
async def set_user_special_title(_ctx: AgentCtx, chat_key: str, user_qq: str, special_title: str, duration: int) -> bool:
    """赋予用户特殊头衔

    Args:
        chat_key (str): 聊天的唯一标识符 (仅支持群组)
        user_qq (str): 被赋予特殊头衔的用户的QQ号
        special_title (str): 特殊头衔 (不超过6个字符, 为空则移除专属头衔)
        duration (int): 有效时间，单位为秒

    Returns:
        bool: 操作是否成功
    """
    bot: Bot = get_bot()
    chat_type, chat_id = chat_key.split("_")
    if chat_type != "group":
        logger.error(f"不支持 {chat_type} 类型")
        return False

    try:
        await bot.set_group_special_title(
            group_id=int(chat_id),
            user_id=int(user_qq),
            special_title=special_title,
            duration=duration,
        )
        logger.info(f"[{chat_key}] 已授予用户 {user_qq} 头衔 {special_title} {duration} 秒")
    except Exception as e:
        logger.error(f"[{chat_key}] 授予用户 {user_qq} 头衔 {special_title} {duration} 秒失败: {e}")
        return False
    else:
        return True
