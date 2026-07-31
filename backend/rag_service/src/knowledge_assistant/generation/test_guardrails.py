import sys
from knowledge_assistant.retrieval.retriever import retrieve
from knowledge_assistant.generation.generator import Generator


def run_test(scenario_name: str, query: str, mock_response: str = None):
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"QUERY: \"{query}\"")
    print(f"{'='*80}")

    print("1. Retrieving context from Qdrant...")
    chunks = retrieve(query, top_k=3)
    if chunks:
        print(f"   Top chunk score: {chunks[0]['score']:.2f}")
    else:
        print("   No chunks retrieved.")

    print("\n2. Generating response...")
    gen = Generator()

    # Mock the LLM client call to simulate a fabricated citation
    if mock_response:
        original_create = gen.client.chat.completions.create

        class MockChoice:
            def __init__(self, content):
                self.message = MockMessage(content)

        class MockMessage:
            def __init__(self, content):
                self.content = content

        class MockResponse:
            def __init__(self, content):
                self.choices = [MockChoice(content)]

        def mock_create(*args, **kwargs):
            return MockResponse(mock_response)

        gen.client.chat.completions.create = mock_create

    try:
        result = gen.generate_response(query, chunks)

        print("\n--- FINAL OUTPUT ---")
        print(result["response_text"])
        print("--------------------")
        print(f"Cited Documents: {result['cited_doc_ids']}")
        print(f"Confidence Score: {result['confidence_score']:.2f}\n")
    except Exception as e:
        print(f"Generation failed: {e}")


def main():
    # Scenario A: Unrelated query
    run_test(
        scenario_name="A) Unrelated query -> Should trigger pre-generation fallback",
        query="What's the weather like today?"
    )

    # Scenario B: Normal query
    run_test(
        scenario_name="B) Normal answerable query -> Should generate normally",
        query="I forgot my password and can't log in"
    )

    # Scenario C: Mocked fabricated citation
    run_test(
        scenario_name="C) Fabricated citation -> Should log warning and reduce confidence",
        query="What integrations do you have?",
        mock_response="We support many integrations. According to [FAQ: Fake Document That Does Not Exist], you can integrate with magic!"
    )


if __name__ == "__main__":
    main()
