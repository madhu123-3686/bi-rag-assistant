import chainlit as cl
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"


# ----------------------------
# Chat Start (Upload CSV)
# ----------------------------
@cl.on_chat_start
async def start():

    await cl.Message(
        content="👋 Welcome to the AI Business Intelligence Assistant.\n\nPlease upload a CSV file to begin."
    ).send()

    files = None

    while files is None:
        files = await cl.AskFileMessage(
            content="📂 Upload your CSV dataset",
            accept=["text/csv"],
            max_size_mb=20,
            timeout=180
        ).send()

    file = files[0]

    with open(file.path, "rb") as f:
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": f}
        )

    if response.status_code == 200:
        await cl.Message(
            content="✅ CSV uploaded successfully!\n\nYou can now ask business questions."
        ).send()

        # 👇 ADD YOUR MESSAGE HERE
        await cl.Message(
            content="""
You can ask questions like:

• Which product generated the highest revenue?
• What is the total revenue?
• Which region performs best?
• Give a business summary
"""
        ).send()

    else:
        await cl.Message(
            content="❌ Upload failed."
        ).send()

    # show action buttons
    await cl.Message(
    content="Choose an option:",
    actions=[
        cl.Action(
            name="show_chart",
            payload={"action": "chart"},
            label="📊 Revenue Chart"
        ),
        cl.Action(
            name="show_insights",
            payload={"action": "insights"},
            label="📈 Business Insights"
        )
    ]
).send()



# ----------------------------
# Chat Question Handler
# ----------------------------
@cl.on_message
async def main(message: cl.Message):

    question = message.content

    response = requests.post(
        f"{API_URL}/ask",
        params={"question": question}
    )

    if response.status_code != 200:
        await cl.Message(content="❌ Backend error").send()
        return

    data = response.json()

    # ----------------------------
    # Detect Chart Response
    # ----------------------------
    if data.get("type") == "chart":

        import plotly.graph_objects as go

        products = data["products"]
        revenues = data["revenues"]

        fig = go.Figure(
            data=[go.Bar(x=products, y=revenues)]
        )

        fig.update_layout(
            title="Revenue by Product",
            xaxis_title="Product",
            yaxis_title="Revenue",
            template="plotly_dark"
        )

        await cl.Message(
            content="📊 Revenue Chart",
            elements=[cl.Plotly(name="Revenue Chart", figure=fig)]
        ).send()

        return

    # ----------------------------
    # Normal Text Response
    # ----------------------------
    answer = data.get("answer", "")

    await cl.Message(content=answer).send()

    # ----------------------------
    # Context Display
    # ----------------------------
     
    # if "sources" in data and data["sources"]:

    #     unique_sources = list(dict.fromkeys(data["sources"]))

    #     context_text = "\n".join(unique_sources)

    #     await cl.Message(
    #         content=f"📄 **Context Used:**\n{context_text}"
    #     ).send()
    sources = data.get("sources", [])

    formatted_sources = []

    for src in sources:
        if isinstance(src, dict):
            row_text = ", ".join([f"{k}: {v}" for k, v in src.items()])
            formatted_sources.append(row_text)
        else:
            formatted_sources.append(str(src))

# remove duplicates
    unique_sources = list(dict.fromkeys(formatted_sources))

    context_text = "\n".join(unique_sources)

    await cl.Message(
        content=f"📄 **Context Used:**\n{context_text}"
    ).send()

import plotly.graph_objects as go

@cl.action_callback("show_chart")
async def show_chart(action):

    response = requests.get("http://127.0.0.1:8000/revenue-chart")

    data = response.json()

    products = data["products"]
    revenues = data["revenues"]

    fig = go.Figure(
        data=[go.Bar(x=products, y=revenues)]
    )

    fig.update_layout(
        title="Revenue by Product",
        xaxis_title="Product",
        yaxis_title="Revenue"
    )

    await cl.Message(
        content="📊 Revenue Chart",
        elements=[cl.Plotly(name="Revenue Chart", figure=fig)]
    ).send()
# ----------------------------
# Business Insights Action
# ----------------------------
@cl.action_callback("show_insights")
async def show_insights(action):

    response = requests.get(f"{API_URL}/insights")

    if response.status_code != 200:
        await cl.Message("❌ Could not fetch insights").send()
        return

    insights = response.json()["insights"]

    insight_text = "\n".join([f"• {i}" for i in insights])

    await cl.Message(
    content=f"### 📊 Business Insights\n\n{insight_text}"
).send()