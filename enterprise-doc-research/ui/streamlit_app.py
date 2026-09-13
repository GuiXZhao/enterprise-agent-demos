"""Demo A 界面：上传文档 → 深度研究 → SSE 流式步骤 + 报告。



运行（在 demos/enterprise-doc-research 目录下）：

  streamlit run ui/streamlit_app.py --server.port 8501

"""



import sys

from pathlib import Path



ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:

    sys.path.insert(0, str(ROOT))



import streamlit as st



from app.config import API_KEY, CHROMA_DIR

from app.ingest import get_vectorstore, ingest_file, load_sample_docs

from app.research import iter_research_events



st.set_page_config(page_title="企业文档深度研究", page_icon="🔬", layout="wide")

st.title("企业文档深度研究 Agent")

st.caption("Demo A v1.1 · LangGraph · Hybrid + Rerank · SSE 流式 trace")



if not API_KEY or API_KEY.startswith("sk-your"):

    st.error("请在项目根目录或本目录的 .env 中配置 OPENAI_API_KEY")

    st.stop()



if "messages" not in st.session_state:

    st.session_state.messages = []

if "last_research" not in st.session_state:

    st.session_state.last_research = None



with st.sidebar:

    st.header("文档库")

    uploaded = st.file_uploader("上传 PDF / TXT", type=["pdf", "txt"])

    if uploaded is not None:

        file_id = f"{uploaded.name}:{uploaded.size}"

        if st.session_state.get("processed_file_id") != file_id:

            with st.spinner("正在入库..."):

                info = ingest_file(uploaded.name, uploaded.getvalue())

            st.session_state.processed_file_id = file_id

            st.success(f"已入库 {info['filename']}（{info['chunk_count']} 段）")



    if st.button("加载 sample_docs 示例文档"):

        with st.spinner("加载示例..."):

            loaded = load_sample_docs()

        if loaded:

            st.success(f"已加载 {len(loaded)} 个示例文件")

        else:

            st.warning("sample_docs 为空")



    store = get_vectorstore()

    if store is not None:

        st.info(f"向量库路径: `{CHROMA_DIR}`")

    else:

        st.warning("尚未入库，请先上传或加载示例")



    if st.button("清空对话"):

        st.session_state.messages = []

        st.session_state.last_research = None



demo_questions = [

    "报销流程分几步？每步需要什么材料？",

    "产品 A 与产品 B 在价格和适用场景上有何区别？",

    "采购合同里关于付款周期和违约金如何规定？",

    "用 3 条 bullet 总结员工远程办公制度要点。",

    "知识库里有没有关于数据出境的规定？",

]



st.subheader("演示问题")

cols = st.columns(2)

for i, q in enumerate(demo_questions):

    if cols[i % 2].button(q, key=f"demo_{i}"):

        st.session_state.pending_question = q



for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])



question = st.chat_input("输入研究问题...")

if st.session_state.get("pending_question"):

    question = st.session_state.pop("pending_question")



if question:

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):

        st.markdown(question)



    with st.chat_message("assistant"):

        trace_box = st.status("研究进行中...", expanded=True)

        answer_placeholder = st.empty()

        answer_parts: list[str] = []

        result = None



        for event in iter_research_events(question):

            if event["type"] == "step":

                ms = event.get("elapsed_ms", 0)

                total = event.get("total_ms", 0)

                trace_box.write(

                    f"`{event['step']}` +{ms}ms（累计 {total}ms）— {event['detail']}"

                )

            elif event["type"] == "answer_chunk":

                answer_parts.append(event["content"])

                answer_placeholder.markdown("".join(answer_parts))

            elif event["type"] == "done":

                result = event["result"]

                trace_box.update(

                    label=f"研究完成 · 总耗时 {event['total_ms']}ms",

                    state="complete",

                )



        if result:

            st.session_state.last_research = result

            st.session_state.messages.append(

                {"role": "assistant", "content": result["answer"]}

            )



if st.session_state.last_research:

    result = st.session_state.last_research

    with st.expander("研究过程详情", expanded=False):

        st.markdown(f"**计划：** {result['plan']}")

        st.markdown(f"**检索词：** {', '.join(result['search_queries'])}")

        if result.get("retrieval_rounds"):

            st.markdown(f"**检索轮次：** {result['retrieval_rounds']}")

        if result.get("total_ms") is not None:

            st.markdown(f"**总耗时：** {result['total_ms']} ms")

        for step in result["trace"]:

            timing = ""

            if step.get("elapsed_ms") is not None:

                timing = f" (+{step['elapsed_ms']}ms)"

            st.write(f"- `{step['step']}`{timing} — {step['detail']}")

        if result["citations"]:

            st.markdown("**引用片段：**")

            for cite in result["citations"]:

                st.code(cite)


