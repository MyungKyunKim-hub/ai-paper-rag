from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. State 정의
class MyState(TypedDict):
    number: int


# 2. Node A
def add_two(state: MyState):
    print("Node A 실행 전:", state)

    return {
        "number": state["number"] + 2
    }


# 3. Node B
def multiply_ten(state: MyState):
    print("Node B 실행 전:", state)

    return {
        "number": state["number"] * 10
    }


# 4. Graph 생성
graph = StateGraph(MyState)


# 5. Node 등록
graph.add_node("add_two", add_two)
graph.add_node("multiply_ten", multiply_ten)


# 6. Edge 연결
graph.add_edge(START, "add_two")
graph.add_edge("add_two", "multiply_ten")
graph.add_edge("multiply_ten", END)


# 7. Graph 완성
app = graph.compile()


# 8. 실행
result = app.invoke({
    "number": 3
})

print("최종 결과:", result)