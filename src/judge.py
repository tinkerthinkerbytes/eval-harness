"""
LLM-as-judge for Coherence and Faithfulness.

Using an LLM for these two dimensions accepts evaluation cost in exchange for
coverage that no deterministic check can provide.

Coherence
    Does the response directly and clearly answer the question?
    Rated 1–5. Pass threshold: >= 3.
    Coherence failure means the response may confuse an analyst into taking the
    wrong action — a safety-critical failure mode in incident response contexts.

Faithfulness
    Do the response's specific factual claims stay within what the retrieved
    context supports? The judge identifies any invented assertions.
    Faithfulness failure is the highest-severity mode in this harness: a
    hallucinated IOC or procedure could cause an analyst to block a legitimate
    resource or follow an incorrect remediation path.

Both dimensions use structured output (Pydantic + OpenAI response_format) so
the verdicts are machine-readable without post-hoc JSON parsing.
"""
from pydantic import BaseModel, Field
from openai import OpenAI

JUDGE_MODEL = "gpt-4.1-nano"
COHERENCE_PASS_THRESHOLD = 3


class CoherenceVerdict(BaseModel):
    score: int = Field(ge=1, le=5, description="Coherence score 1 (incoherent) to 5 (excellent)")
    rationale: str = Field(description="One-sentence explanation of the score")


class FaithfulnessVerdict(BaseModel):
    faithful: bool = Field(
        description="True if all response claims are grounded in the retrieved context"
    )
    unsupported_claims: list[str] = Field(
        description="Specific claims in the response not found in the retrieved context"
    )
    rationale: str = Field(description="One-sentence explanation of the verdict")


_COHERENCE_PROMPT = """\
You are evaluating a SOC analyst assistant response.

Rate how well the response answers the question on a scale of 1–5:
  1 = Incoherent or completely off-topic
  2 = Partially relevant but confusing or missing key points
  3 = Adequately addresses the question with reasonable clarity
  4 = Clear, well-structured, directly and completely answers the question
  5 = Excellent — precise, well-organised, immediately actionable for an analyst

Question: {query}

Response:
{response}"""

_FAITHFULNESS_PROMPT = """\
You are evaluating whether a RAG system response stays grounded in its source context.

Identify any specific factual claims in the response that are NOT supported by the \
retrieved context below. Only flag invented specifics (facts, figures, names, \
procedures) not present in the context. Do not penalise for reasonable paraphrasing \
or inference from stated facts.

Retrieved context:
{context}

Response to evaluate:
{response}"""


def judge_coherence(query: str, response: str) -> dict:
    oai = OpenAI()
    prompt = _COHERENCE_PROMPT.format(query=query, response=response)

    result = oai.beta.chat.completions.parse(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format=CoherenceVerdict,
        temperature=0,
    )
    verdict = result.choices[0].message.parsed
    passed = verdict.score >= COHERENCE_PASS_THRESHOLD

    return {
        "dimension": "coherence",
        "passed": passed,
        "score": verdict.score,
        "threshold": COHERENCE_PASS_THRESHOLD,
        "rationale": verdict.rationale,
        "reason": (
            f"Score {verdict.score}/5 below threshold {COHERENCE_PASS_THRESHOLD}: "
            f"{verdict.rationale}"
        ) if not passed else None,
    }


def judge_faithfulness(response: str, retrieved_chunks: list[dict]) -> dict:
    oai = OpenAI()
    context = "\n\n".join(
        f"[{i + 1}] (source: {chunk['source']})\n{chunk['text']}"
        for i, chunk in enumerate(retrieved_chunks)
    )
    prompt = _FAITHFULNESS_PROMPT.format(context=context, response=response)

    result = oai.beta.chat.completions.parse(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format=FaithfulnessVerdict,
        temperature=0,
    )
    verdict = result.choices[0].message.parsed

    return {
        "dimension": "faithfulness",
        "passed": verdict.faithful,
        "unsupported_claims": verdict.unsupported_claims,
        "rationale": verdict.rationale,
        "reason": (
            f"Unsupported claims: {verdict.unsupported_claims}"
        ) if not verdict.faithful else None,
    }
