'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase'
import { testDatabase, testR2, chat, getMetabaseEmbedUrl } from '@/lib/api'
import { 
  Database, 
  Cloud, 
  MessageSquare, 
  BarChart3, 
  CheckCircle, 
  XCircle, 
  Loader2,
  LogIn,
  LogOut,
  User
} from 'lucide-react'

type TestStatus = 'idle' | 'loading' | 'success' | 'error'

interface TestResult {
  status: TestStatus
  message?: string
}

export default function Home() {
  const [user, setUser] = useState<any>(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState('')
  
  const [dbTest, setDbTest] = useState<TestResult>({ status: 'idle' })
  const [r2Test, setR2Test] = useState<TestResult>({ status: 'idle' })
  const [chatMessage, setChatMessage] = useState('')
  const [chatResponse, setChatResponse] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [metabaseUrl, setMetabaseUrl] = useState('')
  
  const supabase = createClient()

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user)
    })
  }, [])

  const handleSignUp = async () => {
    setAuthLoading(true)
    setAuthError('')
    const { error } = await supabase.auth.signUp({ email, password })
    if (error) {
      setAuthError(error.message)
    } else {
      setAuthError('Check your email for confirmation link!')
    }
    setAuthLoading(false)
  }

  const handleSignIn = async () => {
    setAuthLoading(true)
    setAuthError('')
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      setAuthError(error.message)
    } else {
      setUser(data.user)
    }
    setAuthLoading(false)
  }

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    setUser(null)
  }

  const getToken = async () => {
    const { data } = await supabase.auth.getSession()
    return data.session?.access_token || ''
  }

  const runDbTest = async () => {
    setDbTest({ status: 'loading' })
    try {
      const token = await getToken()
      const result = await testDatabase(token)
      setDbTest({ status: 'success', message: result.message })
    } catch (e: any) {
      setDbTest({ status: 'error', message: e.message })
    }
  }

  const runR2Test = async () => {
    setR2Test({ status: 'loading' })
    try {
      const token = await getToken()
      const result = await testR2(token)
      setR2Test({ status: 'success', message: result.message })
    } catch (e: any) {
      setR2Test({ status: 'error', message: e.message })
    }
  }

  const sendChat = async () => {
    if (!chatMessage.trim()) return
    setChatLoading(true)
    setChatResponse('')
    try {
      const token = await getToken()
      const result = await chat(token, chatMessage)
      setChatResponse(result.response)
    } catch (e: any) {
      setChatResponse(`Error: ${e.message}`)
    }
    setChatLoading(false)
  }

  const loadMetabase = async () => {
    try {
      const token = await getToken()
      const result = await getMetabaseEmbedUrl(token, 1)
      setMetabaseUrl(result.embed_url)
    } catch (e: any) {
      setMetabaseUrl('')
      alert(`Error: ${e.message}`)
    }
  }

  const StatusIcon = ({ status }: { status: TestStatus }) => {
    switch (status) {
      case 'loading': return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />
      default: return null
    }
  }

  if (!user) {
    return (
      <main className="min-h-screen p-8 max-w-md mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Cloud Demo</h1>
        
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5" />
            Sign In / Sign Up
          </h2>
          
          <div className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
            
            {authError && (
              <p className={`text-sm ${authError.includes('Check') ? 'text-green-600' : 'text-red-600'}`}>
                {authError}
              </p>
            )}
            
            <div className="flex gap-2">
              <button
                onClick={handleSignIn}
                disabled={authLoading}
                className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {authLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
                Sign In
              </button>
              <button
                onClick={handleSignUp}
                disabled={authLoading}
                className="flex-1 bg-gray-600 text-white py-2 rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Cloud Demo</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">{user.email}</span>
          <button
            onClick={handleSignOut}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Database Test */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-600" />
            Database Connection
          </h2>
          <p className="text-gray-600 text-sm mb-4">
            Tests connection from Render (FastAPI) to Supabase (Postgres)
          </p>
          <button
            onClick={runDbTest}
            disabled={dbTest.status === 'loading'}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <StatusIcon status={dbTest.status} />
            {dbTest.status === 'loading' ? 'Testing...' : 'Test Database'}
          </button>
          {dbTest.message && (
            <p className={`mt-3 text-sm ${dbTest.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {dbTest.message}
            </p>
          )}
        </div>

        {/* R2 Test */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Cloud className="w-5 h-5 text-orange-600" />
            R2 Storage
          </h2>
          <p className="text-gray-600 text-sm mb-4">
            Tests connection from Render (FastAPI) to Cloudflare R2
          </p>
          <button
            onClick={runR2Test}
            disabled={r2Test.status === 'loading'}
            className="w-full bg-orange-600 text-white py-2 rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <StatusIcon status={r2Test.status} />
            {r2Test.status === 'loading' ? 'Testing...' : 'Test R2 Upload'}
          </button>
          {r2Test.message && (
            <p className={`mt-3 text-sm ${r2Test.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {r2Test.message}
            </p>
          )}
        </div>

        {/* Chat Test */}
        <div className="bg-white rounded-xl shadow-lg p-6 md:col-span-2">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-purple-600" />
            Claude AI Chat
          </h2>
          <p className="text-gray-600 text-sm mb-4">
            Tests connection from Render (FastAPI) to Anthropic (Claude)
          </p>
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendChat()}
              placeholder="Ask Claude something..."
              className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 outline-none"
            />
            <button
              onClick={sendChat}
              disabled={chatLoading}
              className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
            >
              {chatLoading && <Loader2 className="w-4 h-4 animate-spin" />}
              Send
            </button>
          </div>
          {chatResponse && (
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm whitespace-pre-wrap">{chatResponse}</p>
            </div>
          )}
        </div>

        {/* Metabase Embed */}
        <div className="bg-white rounded-xl shadow-lg p-6 md:col-span-2">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-green-600" />
            Metabase Dashboard
          </h2>
          <p className="text-gray-600 text-sm mb-4">
            Tests signed embed URL generation and Metabase iframe embedding
          </p>
          <button
            onClick={loadMetabase}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 mb-4"
          >
            Load Dashboard
          </button>
          {metabaseUrl && (
            <iframe
              src={metabaseUrl}
              className="w-full h-96 border rounded-lg"
              title="Metabase Dashboard"
            />
          )}
        </div>
      </div>

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Architecture: Vercel (Frontend) → Render (Backend) → Supabase + Anthropic + R2</p>
      </div>
    </main>
  )
}
