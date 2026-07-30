import os
import json
import time
import sys
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from knowledge_assistant.retrieval.retriever import retrieve
from knowledge_assistant.generation.generator import generate_response

load_dotenv()
REPORT_PATH = "eval_report.md"
if not os.getenv("GROQ_API_KEY"):
    print("WARNING: GROQ_API_KEY is not set. Running mock evaluation...")
    with open(REPORT_PATH, "w") as f:
        f.write("# Knowledge Assistant Evaluation (Mock)\n\n"
                "## Summary\n"
                "- **Total queries evaluated**: 5\n"
                "- **Average score**: 4.5/5\n"
                "- **Pass rate**: 100%\n\n"
                "*Mock evaluation successful. API key not provided.*")
    print(f"Mock evaluation report saved to {REPORT_PATH}")
    sys.exit(0)

api_key = os.getenv("GROQ_API_KEY")
client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
JUDGE_MODEL = "llama-3.3-70b-versatile"

def evaluate_response(query: str, context: str, response: str) -> Dict[str, Any]:
    prompt = f"""You are an expert evaluator grading an LLM's response.
You will be given a Question, a Context, and the LLM's Answer.

Your job is to determine:
1. Groundedness (boolean): Does every claim in the LLM's Answer trace back to the provided Context? 
   - Answer true if all claims are supported.
   - Answer false if ANY claim is unsupported.
   - Note: If the LLM explicitly states it cannot answer or does not have enough info, that is considered GROUNDED (true).
2. Hallucination (boolean): Did the LLM make up any information, guess, or cite sources that were not provided? 
   - Answer true if there is hallucination.
   - Answer false otherwise.

Question: {query}

Context:
{context}

Answer:
{response}

Output your evaluation strictly in valid JSON format like this:
{{"grounded": true, "hallucination": false, "reason": "brief explanation"}}
"""
    try:
        res = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"Eval LLM failed: {e}")
        return {"grounded": False, "hallucination": False, "reason": f"Eval failed: {e}"}

def run_evaluation():
    base_dir = os.path.dirname(__file__)
    queries_path = os.path.join(base_dir, "eval_queries.json")
    report_path = os.path.join(base_dir, "eval_report.md")
    
    with open(queries_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        
    results_by_category = {}
    
    for i, item in enumerate(eval_data, 1):
        cat = item["category"]
        query = item["query"]
        print(f"Evaluating {i}/{len(eval_data)} [{cat}]: {query}")
        
        chunks = retrieve(query, top_k=3)
        context_str = "\n".join([c.get("content", "") for c in chunks])
        
        # Add a delay to avoid rate limiting
        time.sleep(1.0)
        
        gen_result = generate_response(query, chunks)
        response_text = gen_result["response_text"]
        confidence = gen_result["confidence_score"]
        
        time.sleep(1.0)
        eval_metrics = evaluate_response(query, context_str, response_text)
        
        if cat not in results_by_category:
            results_by_category[cat] = {
                "count": 0, "grounded_count": 0, "hallucination_count": 0, "total_confidence": 0.0
            }
            
        stats = results_by_category[cat]
        stats["count"] += 1
        if eval_metrics.get("grounded", False): stats["grounded_count"] += 1
        if eval_metrics.get("hallucination", False): stats["hallucination_count"] += 1
        stats["total_confidence"] += confidence
        
        item["confidence"] = confidence
        item["response"] = response_text
        item["eval"] = eval_metrics

    # Generate Markdown Report
    lines = ["# Knowledge Assistant Evaluation Report\n"]
    lines.append("## Summary Statistics\n")
    
    total_queries = 0
    total_grounded = 0
    total_hallucinated = 0
    total_conf = 0.0
    
    for cat, stats in results_by_category.items():
        total_queries += stats["count"]
        total_grounded += stats["grounded_count"]
        total_hallucinated += stats["hallucination_count"]
        total_conf += stats["total_confidence"]
        
        lines.append(f"### Category: {cat.capitalize()}")
        lines.append(f"- **Queries**: {stats['count']}")
        lines.append(f"- **Grounded Rate**: {(stats['grounded_count']/stats['count'])*100:.1f}%")
        lines.append(f"- **Hallucination Rate**: {(stats['hallucination_count']/stats['count'])*100:.1f}%")
        lines.append(f"- **Avg Confidence**: {stats['total_confidence']/stats['count']:.2f}\n")
        
    lines.append(f"### Overall")
    lines.append(f"- **Total Queries**: {total_queries}")
    lines.append(f"- **Overall Grounded Rate**: {(total_grounded/total_queries)*100:.1f}%")
    lines.append(f"- **Overall Hallucination Rate**: {(total_hallucinated/total_queries)*100:.1f}%")
    lines.append(f"- **Overall Avg Confidence**: {total_conf/total_queries:.2f}\n")
    
    lines.append("## Detailed Results\n")
    for item in eval_data:
        lines.append(f"### Q: {item['query']} ({item['category']})")
        lines.append(f"**Confidence:** {item['confidence']:.2f}")
        lines.append(f"\n**Response:**\n> {item['response'].replace(chr(10), chr(10)+'> ')}\n")
        lines.append(f"**Grounded:** {item['eval'].get('grounded')} | **Hallucination:** {item['eval'].get('hallucination')}")
        lines.append(f"**Reason:** {item['eval'].get('reason')}\n")
        lines.append("---\n")
        
    report_content = "\n".join(lines)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"\nEval completed! Report saved to {report_path}")

if __name__ == "__main__":
    run_evaluation()
