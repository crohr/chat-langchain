"""Create a ChatVectorDBChain for question/answering."""
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks.tracers import LangChainTracer
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.chat_vector_db.prompts import (CONDENSE_QUESTION_PROMPT,
                                                     QA_PROMPT)
from langchain.chains.llm import LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.vectorstores.base import VectorStore
from pprint import pprint
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

def get_chain(
    vectorstore: VectorStore, question_handler, stream_handler, tracing: bool = False
) -> ConversationalRetrievalChain:
    """Create a ConversationalRetrievalChain for question/answering."""
    # Construct a ConversationalRetrievalChain with a streaming llm for combine docs
    # and a separate, non-streaming llm for question generation
    manager = AsyncCallbackManager([])
    question_manager = AsyncCallbackManager([question_handler])
    stream_manager = AsyncCallbackManager([stream_handler])
    if tracing:
        tracer = LangChainTracer()
        tracer.load_default_session()
        manager.add_handler(tracer)
        question_manager.add_handler(tracer)
        stream_manager.add_handler(tracer)

    question_gen_llm = OpenAI(
        # model_name="gpt-3.5-turbo",
        temperature=0,
        verbose=True,
        callback_manager=question_manager,
    )
    pprint(question_gen_llm)
    streaming_llm = OpenAI(
        model_name="gpt-3.5-turbo",
        streaming=True,
        callback_manager=stream_manager,
        verbose=True,
        temperature=0,
    )
    pprint(streaming_llm)

    question_generator = LLMChain(
        llm=question_gen_llm, prompt=CONDENSE_QUESTION_PROMPT, callback_manager=manager
    )
    pprint(CONDENSE_QUESTION_PROMPT)

    pprint(QA_PROMPT)
    
    prompt=PromptTemplate(
        template="Your name is 'Assistant Dexem'. You will provide me with answers from the given info, and always reply in French. If the answer is not included, say exactly 'Désolé, je n'ai pas la réponse à cette question' and stop after that. Refuse to answer any question not about the info. Never break character. Your name is 'Assistant Dexem', you answer questions about Dexem products. Use the following pieces of context to answer the question at the end, in French. If you don't know the answer, just say that you don't know, don't try to make up an answer.\n\n{context}\n\nQuestion: {question}\nHelpful Answer:",
        input_variables=['context', 'question'],
        template_format='f-string',
        validate_template=True
    )
    pprint(prompt)
    doc_chain = load_qa_chain(
        streaming_llm, chain_type="stuff", prompt=prompt, callback_manager=manager
    )
    qa = ConversationalRetrievalChain(
        retriever=vectorstore.as_retriever(),
        combine_docs_chain=doc_chain,
        return_source_documents=True,
        question_generator=question_generator,
        callback_manager=manager,
    )
    return qa