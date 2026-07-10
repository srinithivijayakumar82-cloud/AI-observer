import {useState} from 'react';
function ScoreBadge({label,value}){
  const color=value>=0.7? 'green':value>=0.4?'orange':'red';
  return (
    <div style={{color:color}}>
      {label}       : {value}
    </div>
  )
}
function SafetyBadge({label,value}){
  const color=value<=0.2? 'green':value<=0.5?'orange':'red';
  return (
    <div style={{color:color}}>
      {label}       : {value}
    </div>
  )
}
function Observer(){
  const [prompt, setPrompt]=useState('')
  const [response, setResponse]=useState('')
  const [model, setModel]=useState('gpt-4o')
  const [loading, setLoading]=useState(false);
  const [result, setResult]=useState(null)
  async function observe(){
    setLoading(true);
    const responsed=await fetch('https://ai-observer.onrender.com/observe', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        prompt:prompt,
        response:response,
        model:model
      })
    })
    const data=await responsed.json();
    setResult(data);
    setLoading(false);

  }
  return (
    <>
    <div>
      <p>Prompt : <textarea placeholder="Enter prompt" value={prompt} 
        onChange={(e)=>setPrompt(e.target.value)}/>
      </p><br/>
      <p>Response : <textarea placeholder="Enter response" value={response} 
      onChange={(e)=>setResponse(e.target.value)}/>
      </p><br/>
      <p>Model : <select value={model} onChange={(e)=>setModel(e.target.value)}>
        <option value="gpt-4o">GPT-4o</option>
        <option value="gpt-4o-mini">GPT-4o Mini</option>
        <option value="claude-sonnet">Claude Sonnet</option>
        <option value="claude-haiku">Claude Haiku</option>
        <option value="llama-3.3-70b">Llama 3.3 70B</option>
        <option value="llama-3.1-8b">Llama 3.1 8B</option>
        <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
        <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
      </select>
      </p><br/>
      <button onClick={observe}>Observe</button>
    </div>
    {result && (
      <div>
      <p>Prompt: {result.prompt}</p>
      <p>Response: {result.response}</p>
      <p>Model  : {result.model}</p>
      <p>Temperature  : {result.estimated_temperature}</p>
      <p>Etimated cost: {result.estimated_cost}</p>
      <p>Input tokens : {result.input_tokens}</p>
      <p>Output tokens: {result.output_tokens}</p>
      <p>Total tokens : {result.total_tokens}</p>
      <p>Latency      : {result.latency_ms}</p>
      <SafetyBadge label="Safety Score" value={result.prompt_safety_score}/>
      <ScoreBadge label="Quality score" value={result.response_quality_score}/>
      </div>
    )}
  </>
  )
}
export default Observer;