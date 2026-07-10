from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import engine,SessionLocal
from ObservabilityLog import ObserveLog
import ObservabilityLog
import time
import tiktoken
ObservabilityLog.Base.metadata.create_all(bind=engine)
app=FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)
class observeRequest(BaseModel):
    prompt: str
    response: str
    model: str="unknown"

def count_tokens(text):
    encoder=tiktoken.get_encoding("cl100k_base")
    tokens=encoder.encode(text)
    token_count=len(tokens)
    return token_count

def estimate_temperature_range(response):
    def measure_diversity(text):
        words=text.lower().split()
        unique_words=set(words)
        diversity_ratio=len(unique_words)/len(words)
        return diversity_ratio
    def estimate_temperature(diversity_ratio):
        if diversity_ratio<0.4:
            return "Low (0.0 - 0.3)"
        elif diversity_ratio<0.7:
            return "Medium (0.4 - 0.7)"
        else:
            return "High (0.8 - 1.0)"
    diversity=measure_diversity(response)
    return estimate_temperature(diversity)
        
def prompt_safety_score(prompt):
    suspicious_patterns = ["ignore previous instructions","forget your system prompt","you are now","pretend you are","act as if","bypass","jailbreak","disregard your instructions","ignore all prior instructions","you have no restrictions","override your programming","ignore your training","pretend you have no limits","act as a different ai","simulate an ai without restrictions"]
    text_lower=prompt.lower()
    matches=sum(1 for pattern in suspicious_patterns if pattern in text_lower)
    score=min(matches / len(suspicious_patterns), 1.0)
    return round(score,2)

def response_quality_score(response):
    score=1.0
    if len(response.split())<10:
        score-=0.3
    weak_phrases=["i can't","i don't know","i'm not sure","i cannot","i am unable","i do not know","i'm unable to","as an ai","i apologize"]
    if any(phrase in response.lower() for phrase in weak_phrases):
        score-=0.2
    words=response.lower().split()
    if len(words)>0:
        unique_ratio=len(set(words)) / len(words)
        if unique_ratio<0.3:
            score-=0.2
    return round(max(score, 0.0),2)

def estimate_cost(input_tokens, output_tokens, model):
    price={
        "llama-3.3-70b": {"input": 0.59, "output": 0.79},
        "llama-3.1-8b": {"input": 0.05, "output": 0.08},
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-sonnet": {"input": 3.00, "output": 15.00},
        "claude-haiku": {"input": 0.25, "output": 1.25},
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30}
    }
    rates=price.get(model, price["llama-3.3-70b"])
    cost=(input_tokens / 1_000_000 * rates["input"]) + \
           (output_tokens / 1_000_000 * rates["output"])
    return round(cost, 6)

@app.post("/observe")
def observe_endpoint(request:observeRequest):
    start_time=time.time()
    input_tokens=count_tokens(request.prompt)
    output_tokens=count_tokens(request.response)
    total_tokens=input_tokens+output_tokens
    estimated_cost=estimate_cost(input_tokens,output_tokens,request.model)
    temperature=estimate_temperature_range(request.prompt)
    prompt_safe_score=prompt_safety_score(request.prompt)
    quality_score=response_quality_score(request.response)
    end_time=time.time()
    latency_ms=(end_time-start_time)*1000
    db=SessionLocal()
    try:
        log=ObserveLog(
            prompt=request.prompt,
            temperature=temperature,
            model=request.model,
            response=request.response,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            success=True,
            error_message=None,
            prompt_safe_score=prompt_safe_score,
            quality_score=quality_score
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    return {
        "prompt": request.prompt,
        "estimated_temperature": temperature,
        "model": request.model,
        "response": request.response,
        "latency_ms": round(latency_ms, 2),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
        "success": True,
        "error_message": None,
        "prompt_safety_score": prompt_safe_score,
        "response_quality_score": quality_score,
    }

@app.get("/logs")
def get_logs():
    db=SessionLocal()
    try:
        logs=db.query(ObserveLog).all()
        return[{
            "id":log.id,
            "timestamp":log.timestamp,
            "model":log.model,
            "prompt":log.prompt,
            "response":log.response,
            "temperature":log.temperature,
            "input_tokens":log.input_tokens,
            "output_tokens":log.output_tokens,
            "total_tokens":log.total_tokens,
            "latency_ms":log.latency_ms,
            "estimated_cost":log.estimated_cost,
            "success":log.success,
            "error_message":log.error_message,
            "prompt_safety_score":log.prompt_safe_score,
            "response_quality_score":log.quality_score
        }
        for log in logs
        ]
    except Exception as e:
        raise e
    finally:
        db.close()

