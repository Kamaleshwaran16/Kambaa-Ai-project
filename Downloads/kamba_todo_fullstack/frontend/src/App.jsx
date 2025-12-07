import React, {useEffect, useState, useRef} from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function App(){ 
  const [tasks, setTasks] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const wsRef = useRef(null)

  useEffect(()=>{
    fetchTasks()
    // connect websocket
    try {
      wsRef.current = new WebSocket((API.replace('http','ws')) + '/ws/updates')
      wsRef.current.onmessage = (e) => {
        const msg = JSON.parse(e.data)
        if(msg.action === 'init') setTasks(msg.tasks || [])
        else if(msg.action === 'created' || msg.action === 'updated' || msg.action === 'deleted') {
          // simple refresh
          fetchTasks()
        }
      }
    } catch(e){ console.warn('WS failed', e) }
    return ()=> wsRef.current && wsRef.current.close()
  },[])

  async function fetchTasks(){
    const res = await axios.get(API + '/tasks')
    setTasks(res.data)
  }

  async function addTask(e){
    e.preventDefault()
    if(!title) return
    await axios.post(API + '/tasks', {title, description})
    setTitle(''); setDescription('')
    fetchTasks()
  }

  async function toggleComplete(t){
    await axios.put(API + `/tasks/${t.id}`, {completed: !t.completed})
    fetchTasks()
  }

  async function removeTask(t){
    if(!confirm('Delete this task?')) return
    await axios.delete(API + `/tasks/${t.id}`)
    fetchTasks()
  }

  return (<div style={{fontFamily:'system-ui, Arial', maxWidth:900, margin:'30px auto'}}>
    <h1 style={{fontSize:32}}>Kamba TODO</h1>
    <form onSubmit={addTask} style={{marginBottom:20}}>
      <input placeholder='Title' value={title} onChange={e=>setTitle(e.target.value)} style={{padding:8, width:300}} />
      <input placeholder='Description' value={description} onChange={e=>setDescription(e.target.value)} style={{padding:8, width:400, marginLeft:8}} />
      <button style={{padding:'8px 12px', marginLeft:8}}>Add</button>
    </form>

    <div>
      {tasks.map(t=> (
        <div key={t.id} style={{padding:12, border:'1px solid #eee', marginBottom:8, borderRadius:8, display:'flex', justifyContent:'space-between'}}>
          <div>
            <div style={{fontWeight:700}}>{t.title} <small style={{color:'#666'}}>({t.priority})</small></div>
            <div style={{color:'#444'}}>{t.summary || (t.description||'')}</div>
            <div style={{fontSize:12, color:'#888'}}>{new Date(t.created_at).toLocaleString()}</div>
          </div>
          <div style={{display:'flex', gap:8, alignItems:'center'}}>
            <button onClick={()=>toggleComplete(t)}>{t.completed ? 'Undo' : 'Done'}</button>
            <button onClick={()=>removeTask(t)}>Delete</button>
          </div>
        </div>
      ))}
    </div>
  </div>)
}

export default App
