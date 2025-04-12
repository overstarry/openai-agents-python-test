import os
import json
import asyncio
from openai import AsyncOpenAI
from agents import Agent, FunctionTool, function_tool, set_tracing_disabled, Runner, set_default_openai_client, set_default_openai_api
from agents.mcp import MCPServerPython

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


# 创建一个天气 MCP 服务器类
class WeatherMCPServer(MCPServerPython):
    """简单的天气MCP服务器，提供城市天气查询功能"""

    def __init__(self):
        # 定义MCP服务器的名称和描述
        super().__init__(
            name="天气查询服务",
            description="提供城市天气查询服务，支持国内主要城市天气信息查询"
        )
        
        # 注册天气查询工具
        self.register_tool(
            name="query_weather",
            description="查询特定城市的天气情况",
            parameters={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询天气的城市名称，如北京、上海、广州等"
                    }
                },
                "required": ["city"]
            },
            handler=self.query_weather
        )

    async def query_weather(self, city: str) -> str:
        """
        查询城市天气的处理函数
        
        Args:
            city: 城市名称
            
        Returns:
            str: 城市天气信息的JSON字符串
        """
        # 模拟天气数据，实际应用中应该调用天气API
        weather_data = {
            "北京": {
                "temperature": "22°C",
                "condition": "晴",
                "humidity": "45%",
                "wind": "东北风3级",
                "air_quality": "良",
                "suggestion": "天气不错，适合户外活动，但请注意防晒"
            },
            "上海": {
                "temperature": "24°C",
                "condition": "多云",
                "humidity": "60%",
                "wind": "东风2级",
                "air_quality": "良",
                "suggestion": "天气较好，适合户外活动，带上伞以防突发小雨"
            },
            "广州": {
                "temperature": "28°C",
                "condition": "阵雨",
                "humidity": "80%",
                "wind": "南风3级",
                "air_quality": "良",
                "suggestion": "有阵雨，出门请携带雨具，注意防潮"
            },
            "深圳": {
                "temperature": "29°C",
                "condition": "多云",
                "humidity": "75%",
                "wind": "东南风2级",
                "air_quality": "良",
                "suggestion": "天气较热，注意防晒防暑，适量补充水分"
            },
            "杭州": {
                "temperature": "23°C",
                "condition": "晴",
                "humidity": "55%",
                "wind": "西北风2级",
                "air_quality": "优",
                "suggestion": "天气宜人，非常适合户外活动和旅游"
            },
            "成都": {
                "temperature": "20°C",
                "condition": "阴",
                "humidity": "65%",
                "wind": "微风",
                "air_quality": "良",
                "suggestion": "天气较舒适，适合户外活动，建议着薄外套"
            },
            "西安": {
                "temperature": "19°C",
                "condition": "晴",
                "humidity": "40%",
                "wind": "西北风4级",
                "air_quality": "轻度污染",
                "suggestion": "风力较大，注意添加衣物，空气质量一般"
            },
            "重庆": {
                "temperature": "25°C",
                "condition": "多云",
                "humidity": "70%",
                "wind": "微风",
                "air_quality": "良",
                "suggestion": "天气较热，注意防晒，适量补充水分"
            }
        }
        
        # 获取城市天气数据，如果城市不存在则返回提示信息
        if city in weather_data:
            result = {
                "city": city,
                "date": "2025年4月12日",  # 使用当前日期
                "weather": weather_data[city]
            }
            return json.dumps(result, ensure_ascii=False)
        else:
            return json.dumps({
                "error": f"无法找到城市 '{city}' 的天气信息，请尝试其他城市，如北京、上海、广州等。"
            }, ensure_ascii=False)


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
    使用query_weather工具来查询目的地的天气信息，以便给用户提供更好的建议。
    """
    
    # 创建天气MCP服务器实例
    weather_server = WeatherMCPServer()
    
    # 创建并返回Agent，将天气服务器添加到Agent中
    return Agent(
        name="旅游规划助手",
        instructions=instructions,
        tools=[generate_travel_plan],
        model="ep-20250213111445-6677q",
        mcp_servers=[weather_server]
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
