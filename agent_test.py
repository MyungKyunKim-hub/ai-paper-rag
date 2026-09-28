import os
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, ToolMessage

load_dotenv()


@tool
def add(a: int, b: int) -> int:
    """두 정수를 더합니다."""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """두 정수를 곱합니다."""
    return a * b


llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0
)

tools = [add, multiply]

llm_with_tools = llm.bind_tools(tools)


# 1. 사용자 메시지 생성
user_message = HumanMessage(
    content="3과 5를 곱해줘."
)


# 2. Gemini에게 사용자 메시지 전달
response = llm_with_tools.invoke(
    [user_message]
)

print("Tool Calls:", response.tool_calls)


# 3. Gemini가 선택한 Tool 정보 가져오기
tool_call = response.tool_calls[0]

tool_name = tool_call["name"]
tool_args = tool_call["args"]

print("선택된 Tool:", tool_name)
print("Tool 인자:", tool_args)


# 4. 실제 Python Tool 실행
if tool_name == "add":
    result = add.invoke(tool_args)

elif tool_name == "multiply":
    result = multiply.invoke(tool_args)

print("Tool 실행 결과:", result)


# 5. Tool 실행 결과를 메시지로 만들기
tool_message = ToolMessage(
    content=str(result),
    tool_call_id=tool_call["id"]
)


# 6. 전체 대화 흐름을 Gemini에게 다시 전달
final_response = llm_with_tools.invoke(
    [
        user_message,
        response,
        tool_message
    ]
)

print("최종 답변:", final_response.content)