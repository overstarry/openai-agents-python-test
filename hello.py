import os
import json
import asyncio
from openai import AsyncOpenAI
from agents import Agent, FunctionTool, function_tool, set_tracing_disabled, Runner, set_default_openai_client, set_default_openai_api

from dotenv import load_dotenv

load_dotenv(override=True)

# 设置自定义的OpenAI客户端
def setup_custom_client(base_url: str, api_key: str):
    """
    设置自定义的OpenAI客户端，连接到兼容OpenAI API的第三方服务
    """
    custom_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    set_default_openai_client(custom_client)
    return custom_client


@function_tool
def generate_travel_plan(location: str, days: int) -> str:
    """
    根据用户提供的旅游地点和天数生成旅游规划。

    Args:
        location: 旅游目的地，如"北京"、"上海"、"杭州"等
        days: 旅游天数，如3、5、7等

    Returns:
        str: 详细的旅游规划，包括每天的行程安排
    """
    # 实际上，这里的工具函数会让LLM生成旅游规划
    # 不需要我们自己实现具体的旅游规划逻辑
    return f"为{location}生成了{days}天的旅游规划"




def create_travel_agent():
    """创建旅游规划agent"""
    instructions = """
    你是一个专业的旅游规划助手。你的任务是根据用户提供的旅游地点和天数，
    制定一个详细的旅游规划。规划应包括：

    1. 每天的行程安排，包括景点、餐厅和活动
    2. 每个景点的参观时间和简短介绍
    3. 餐饮推荐，包括当地特色美食
    4. 交通建议
    5. 额外的旅游贴士（如天气、穿着、文化禁忌等）

    使用generate_travel_plan工具来生成旅游规划。
    """


    # 创建并返回Agent，将天气服务器添加到Agent中
    return Agent(
        name="旅游规划助手",
        instructions=instructions,
        tools=[generate_travel_plan],
        model="ep-20250213111445-6677q",
    )


def main():
    print("欢迎使用旅游规划助手!")
    print("请输入兼容OpenAI API的服务配置信息")

    # 在实际使用中，可以从环境变量或配置文件获取这些信息
    base_url = input("API 基础URL (如 http://localhost:8000/v1): ") or os.getenv("OPENAI_BASE_URL", "")
    api_key = input("API Key: ") or os.getenv("OPENAI_API_KEY", "")

    if not base_url or not api_key:
        print("错误：API基础URL和密钥不能为空。请设置OPENAI_BASE_URL和OPENAI_API_KEY环境变量或在提示时输入。")
        return

    # 设置自定义客户端
    setup_custom_client(base_url, api_key)
    set_default_openai_api("chat_completions")
    set_tracing_disabled(True)

    print("\n请输入您想要旅游的地点和天数")
    location = input("旅游地点: ")

    try:
        days = int(input("旅游天数: "))
    except ValueError:
        print("错误：旅游天数必须是数字。")
        return

    agent = create_travel_agent()
    query = f"请为我计划一次{days}天的{location}之旅，并且告诉我当地的天气情况"

    print("\n正在生成旅游规划，请稍候...\n")
    result = Runner.run_sync(agent, query)

    print("\n=== 您的旅游规划 ===\n")
    print(result.final_output)


if __name__ == "__main__":
    main()
