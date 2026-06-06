'use client'
import { useState, useRef, useEffect } from 'react'

const suggestions = [
  "Why should Scaler hire Shahid?",
  "Tell me about Focus Guardian",
  "What is Laptolyze?",
  "Book an interview"
]

export default function Home() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi! I'm Shahid's AI persona. Ask me anything about his background, projects, or skills — or book an interview directly!"
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const msg = text || input
    if (!msg.trim()) return
    const userMessage = { role: 'user', content: msg }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, history: messages })
      })
      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }])
    }
    setIsLoading(false)
  }

  return (
    <main style={{
      minHeight: '100vh',
      background: '#0a0a0f',
      color: '#e8e6f0',
      fontFamily: "'DM Sans', sans-serif",
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '0',
    }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Syne:wght@600;700&display=swap" rel="stylesheet" />

      <style>{`
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 4px; }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 1; }
        }
        @keyframes shimmer {
          0% { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        .msg-animate { animation: fadeUp 0.3s ease forwards; }
        .dot { animation: pulse 1.2s ease-in-out infinite; }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        .send-btn:hover { background: #6c5ce7 !important; transform: scale(1.05); }
        .send-btn:active { transform: scale(0.97); }
        .suggestion:hover { background: #1a1a2e !important; border-color: #6c5ce7 !important; color: #a78bfa !important; transform: translateY(-1px); }
        .nav-link:hover { color: #a78bfa !important; }
        .chip:hover { background: #1e1e30 !important; }
        input:focus { outline: none; border-color: #6c5ce7 !important; box-shadow: 0 0 0 3px rgba(108,92,231,0.15) !important; }
      `}</style>

      {/* Top nav */}
      <nav style={{
        width: '100%',
        maxWidth: '780px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '20px 24px',
        borderBottom: '1px solid #1a1a2a',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, #6c5ce7, #a78bfa)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '14px', fontWeight: '600', color: '#fff',
            fontFamily: "'Syne', sans-serif"
          }}>SN</div>
          <span style={{ fontFamily: "'Syne', sans-serif", fontWeight: '600', fontSize: '15px', color: '#e8e6f0' }}>
            Shahid Nalwar
          </span>
          <span style={{
            background: '#1a2a1a', color: '#4ade80', fontSize: '11px',
            padding: '2px 8px', borderRadius: '20px', border: '1px solid #2a4a2a'
          }}>● Live</span>
        </div>
        <div style={{ display: 'flex', gap: '20px' }}>
          <a href="https://github.com/ShahidNalwar" target="_blank"
            className="nav-link"
            style={{ color: '#888', fontSize: '13px', textDecoration: 'none', transition: 'color 0.2s' }}>
            GitHub
          </a>
          <a href="https://cal.com/shahid-nalwar-bf5bxg/interview-with-shahid" target="_blank"
            className="nav-link"
            style={{ color: '#a78bfa', fontSize: '13px', textDecoration: 'none', fontWeight: '500', transition: 'color 0.2s' }}>
            Book Interview →
          </a>
        </div>
      </nav>

      <div style={{ width: '100%', maxWidth: '780px', padding: '0 24px', flex: 1, display: 'flex', flexDirection: 'column' }}>

        {/* Hero section */}
        <div style={{ padding: '40px 0 32px', borderBottom: '1px solid #1a1a2a' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px' }}>
            <div style={{
              width: '72px', height: '72px', borderRadius: '18px', flexShrink: 0,
              background: 'linear-gradient(135deg, #1a1a3e 0%, #2d1f6e 100%)',
              border: '1px solid #3d2fa0',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: "'Syne', sans-serif", fontSize: '24px', fontWeight: '700', color: '#a78bfa'
            }}>SN</div>
            <div style={{ flex: 1 }}>
              <h1 style={{ fontFamily: "'Syne', sans-serif", fontSize: '28px', fontWeight: '700', color: '#fff', marginBottom: '6px' }}>
                Shahid Nalwar
              </h1>
              <p style={{ color: '#888', fontSize: '14px', marginBottom: '12px' }}>
                B.Tech AI & Data Science · N.K. Orchid College of Engineering, Solapur
              </p>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {['Python', 'ML/AI', 'Flutter', 'BERT', 'GANs', 'RAG', 'FastAPI'].map(skill => (
                  <span key={skill} className="chip" style={{
                    background: '#13132a', color: '#a78bfa', fontSize: '12px',
                    padding: '4px 10px', borderRadius: '6px', border: '1px solid #2a2a4a',
                    transition: 'background 0.2s', cursor: 'default'
                  }}>{skill}</span>
                ))}
              </div>
            </div>
            <a href="tel:+19895821766" style={{
              background: '#0f1f0f', color: '#4ade80', fontSize: '12px',
              padding: '8px 14px', borderRadius: '10px', border: '1px solid #1a4a1a',
              textDecoration: 'none', display: 'flex', flexDirection: 'column',
              alignItems: 'center', gap: '2px', flexShrink: 0
            }}>
              <span style={{ fontSize: '16px' }}>📞</span>
              <span style={{ fontSize: '11px', fontWeight: '500' }}>Call AI</span>
            </a>
          </div>
        </div>

        {/* Chat window */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: '24px 0',
          display: 'flex', flexDirection: 'column', gap: '16px',
          minHeight: '360px', maxHeight: '460px',
        }}>
          {messages.map((msg, i) => (
            <div key={i} className="msg-animate" style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              gap: '10px', alignItems: 'flex-end'
            }}>
              {msg.role === 'assistant' && (
                <div style={{
                  width: '28px', height: '28px', borderRadius: '8px', flexShrink: 0,
                  background: 'linear-gradient(135deg, #6c5ce7, #a78bfa)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '11px', fontWeight: '600', color: '#fff'
                }}>SN</div>
              )}
              <div style={{
                maxWidth: '72%',
                padding: '12px 16px',
                borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                background: msg.role === 'user'
                  ? 'linear-gradient(135deg, #6c5ce7, #8b5cf6)'
                  : '#141420',
                border: msg.role === 'user' ? 'none' : '1px solid #1e1e30',
                fontSize: '14px', lineHeight: '1.6',
                color: msg.role === 'user' ? '#fff' : '#d4d0e8',
              }}>
                {msg.content}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="msg-animate" style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
              <div style={{
                width: '28px', height: '28px', borderRadius: '8px', flexShrink: 0,
                background: 'linear-gradient(135deg, #6c5ce7, #a78bfa)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '11px', fontWeight: '600', color: '#fff'
              }}>SN</div>
              <div style={{
                padding: '14px 18px', background: '#141420', border: '1px solid #1e1e30',
                borderRadius: '18px 18px 18px 4px', display: 'flex', gap: '5px', alignItems: 'center'
              }}>
                {[0,1,2].map(i => (
                  <div key={i} className="dot" style={{
                    width: '6px', height: '6px', borderRadius: '50%', background: '#6c5ce7'
                  }} />
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggestions */}
        {messages.length <= 1 && (
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
            {suggestions.map(s => (
              <button key={s} className="suggestion" onClick={() => sendMessage(s)} style={{
                background: '#0f0f1a', color: '#888', fontSize: '13px',
                padding: '8px 14px', borderRadius: '10px',
                border: '1px solid #1e1e30', cursor: 'pointer',
                transition: 'all 0.2s', fontFamily: "'DM Sans', sans-serif"
              }}>{s}</button>
            ))}
          </div>
        )}

        {/* Input bar */}
        <div style={{
          display: 'flex', gap: '10px', padding: '16px 0 24px',
          borderTop: '1px solid #1a1a2a',
        }}>
          <input
            ref={inputRef}
            style={{
              flex: 1, background: '#0f0f1a', color: '#e8e6f0',
              border: '1px solid #1e1e30', borderRadius: '14px',
              padding: '14px 18px', fontSize: '14px',
              fontFamily: "'DM Sans', sans-serif",
              transition: 'all 0.2s',
            }}
            placeholder="Ask about projects, skills, experience..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          />
          <button
            className="send-btn"
            onClick={() => sendMessage()}
            style={{
              background: '#4a3ab0', color: '#fff', border: 'none',
              borderRadius: '14px', padding: '14px 20px', cursor: 'pointer',
              fontSize: '18px', transition: 'all 0.2s', flexShrink: 0
            }}
          >→</button>
        </div>

        {/* Footer */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          paddingBottom: '24px', fontSize: '12px', color: '#444'
        }}>
          <span>Powered by Groq · Llama 3.3 70B · RAG grounded</span>
          <a href="https://cal.com/shahid-nalwar-bf5bxg/interview-with-shahid" target="_blank"
            style={{ color: '#6c5ce7', textDecoration: 'none', fontWeight: '500' }}>
            📅 Schedule Interview
          </a>
        </div>
      </div>
    </main>
  )
}