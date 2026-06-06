import { NextResponse } from 'next/server'

export async function POST(req) {
  try {
    const { message, history } = await req.json()

    // Get the backend URL from environment variables, fallback to local FastAPI server
    const backendUrl = process.env.RAG_API_URL || 'http://127.0.0.1:8000'

    const response = await fetch(`${backendUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        history
      })
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('RAG API error:', errorText)
      return NextResponse.json({ 
        reply: "I'm having trouble retrieving answers from my knowledge base right now. Please make sure the backend is active.",
        chunks: []
      })
    }

    const data = await response.json()
    return NextResponse.json({ 
      reply: data.reply, 
      chunks: data.chunks || [] 
    })
  } catch (error) {
    console.error('Error calling RAG backend:', error)
    return NextResponse.json({ 
      reply: "I'm sorry, I'm experiencing a connection issue. Please check back shortly.",
      chunks: []
    })
  }
}
