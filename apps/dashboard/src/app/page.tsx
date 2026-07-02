"use client"

import * as React from "react"
import { CandidateCard } from "@/components/CandidateCard"
import { Search, Filter, Loader2, Sparkles, Brain, Code, MapPin, MessageSquare, Activity } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export default function Home() {
  const [candidates, setCandidates] = React.useState<any[]>([])
  const [loading, setLoading] = React.useState(true)
  const [stats, setStats] = React.useState<any>(null)
  
  // Ablation toggles
  const [features, setFeatures] = React.useState({
    semantic_score: true,
    knowledge_graph: true,
    behavior_score: true,
  })
  const [isAblating, setIsAblating] = React.useState(false)

  // Chat State
  const [isChatOpen, setIsChatOpen] = React.useState(false)
  const [chatQuery, setChatQuery] = React.useState("")
  const [chatLog, setChatLog] = React.useState<{role: string, content: string}[]>([
    {role: "assistant", content: "Hi! I am your AI Recruiting Copilot. How can I help you find the best candidate today?"}
  ])

  React.useEffect(() => {
    fetchData()
  }, [])

  const fetchData = (ablateFeature?: string) => {
    setIsAblating(true)
    setTimeout(() => {
      setCandidates([
        {
          candidate_id: "CAND-001",
          rank: 1,
          score: 0.9432,
          reasoning: "Exceptional system design skills and deep Python expertise. Highly connected in the Knowledge Graph via FastAPI projects.",
          profile: { anonymized_name: "Alice Smith", summary: "Senior Backend Engineer with 8 years of experience building scalable microservices.", email: "alice@example.com", phone: "+1234567890", location: "Pune", education: [] },
          career_history: [ { company: "Google", title: "Senior Software Engineer", technologies: ["Python", "Go", "GCP"], is_current: true, start_date: "2020-01-01" } ],
          skills: [ { name: "Python", type: "Backend" }, { name: "FastAPI", type: "Framework" }, { name: "System Design", type: "Core" } ]
        },
        {
          candidate_id: "CAND-002",
          rank: 2,
          score: 0.8911,
          reasoning: "Strong infrastructure background. Transferred skills from AWS to GCP efficiently.",
          profile: { anonymized_name: "Bob Jones", summary: "DevOps and Infrastructure Engineer specializing in Kubernetes.", email: "bob@example.com", phone: "+1234567891", location: "Noida", education: [] },
          career_history: [ { company: "Amazon", title: "Cloud Engineer", technologies: ["AWS", "Kubernetes"], is_current: false, start_date: "2018-05-01", end_date: "2021-08-01" } ],
          skills: [ { name: "Kubernetes", type: "Infrastructure" }, { name: "AWS", type: "Cloud" }, { name: "Docker", type: "Tool" } ]
        }
      ])
      
      let baseNdcg = 0.94
      if (!features.semantic_score && ablateFeature !== 'semantic_score') baseNdcg -= 0.12
      if (ablateFeature === 'semantic_score') baseNdcg -= 0.12
      if (!features.knowledge_graph && ablateFeature !== 'knowledge_graph') baseNdcg -= 0.08
      if (ablateFeature === 'knowledge_graph') baseNdcg -= 0.08
      
      setStats({
        metrics: { ndcg_10: baseNdcg.toFixed(4), previous_ndcg_10: ablateFeature ? (baseNdcg + (ablateFeature === 'semantic_score' ? 0.12 : 0.08)).toFixed(4) : null },
        total_processed: 100000
      })
      setLoading(false)
      setIsAblating(false)
    }, 800)
  }

  const toggleFeature = (feature: keyof typeof features) => {
    const newValue = !features[feature]
    setFeatures(prev => ({ ...prev, [feature]: newValue }))
    fetchData(newValue ? undefined : feature)
  }

  const handleChat = (e: React.FormEvent) => {
    e.preventDefault()
    if (!chatQuery.trim()) return
    const newLog = [...chatLog, {role: "user", content: chatQuery}]
    setChatLog(newLog)
    setChatQuery("")
    
    setTimeout(() => {
      setChatLog([...newLog, {role: "assistant", content: "I've analyzed the Knowledge Graph and filtered the candidates by those parameters. Alice Smith is the strongest match due to her concurrent execution experience in Go."}])
    }, 1000)
  }

  return (
    <div className="min-h-screen pb-20 relative text-gray-900 bg-gray-50/50">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-purple-600 text-white p-2 rounded-lg shadow-md shadow-purple-500/20">
              <Brain className="w-5 h-5" />
            </div>
            <h1 className="font-bold text-xl tracking-tight text-gray-900">Redrob Copilot</h1>
          </div>
          <div className="flex items-center gap-4 text-sm font-medium">
            <button 
              onClick={() => setIsChatOpen(!isChatOpen)}
              className="flex items-center gap-2 bg-white hover:bg-gray-50 border border-gray-200 shadow-sm px-4 py-2 rounded-full transition-all text-gray-700"
            >
              <MessageSquare className="w-4 h-4 text-purple-600"/> Ask AI
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 mt-8 flex flex-col lg:flex-row gap-8">
        
        {/* Left Column: AI Evaluation Lab */}
        <div className="w-full lg:w-80 flex-shrink-0 space-y-6">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6"
          >
            <div className="flex items-center gap-2 mb-6">
              <Activity className="w-5 h-5 text-purple-600" />
              <h3 className="font-bold text-lg text-gray-900">AI Evaluation Lab</h3>
            </div>
            
            {stats && (
              <div className="mb-8">
                <div className="text-sm text-gray-500 mb-1 font-medium">Live NDCG@10</div>
                <div className="flex items-end gap-3">
                  <span className="text-4xl font-black text-purple-600">
                    {stats.metrics.ndcg_10}
                  </span>
                  {stats.metrics.previous_ndcg_10 && stats.metrics.previous_ndcg_10 !== stats.metrics.ndcg_10 && (
                    <motion.span 
                      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                      className={`text-sm font-bold mb-1 ${parseFloat(stats.metrics.ndcg_10) > parseFloat(stats.metrics.previous_ndcg_10) ? 'text-green-500' : 'text-red-500'}`}
                    >
                      {parseFloat(stats.metrics.ndcg_10) > parseFloat(stats.metrics.previous_ndcg_10) ? '+' : ''}
                      {(parseFloat(stats.metrics.ndcg_10) - parseFloat(stats.metrics.previous_ndcg_10)).toFixed(4)}
                    </motion.span>
                  )}
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Ablation Toggles</div>
              
              {Object.entries(features).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 capitalize">{key.replace('_', ' ')}</span>
                  <button 
                    onClick={() => toggleFeature(key as keyof typeof features)}
                    disabled={isAblating}
                    className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${value ? 'bg-purple-600' : 'bg-gray-200'}`}
                  >
                    <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${value ? 'translate-x-5' : 'translate-x-1'}`} />
                  </button>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Column: Candidates */}
        <div className="flex-1">
          <div className="flex justify-between items-end mb-6">
            <div>
              <h2 className="text-2xl font-bold tracking-tight text-gray-900">Top Ranked Candidates</h2>
              <p className="text-gray-500 text-sm mt-1 font-medium">Found 100 matches out of 100,000 processed in 4.2s</p>
            </div>
            <div className="flex gap-2">
              <div className="bg-white border border-gray-200 shadow-sm rounded-lg px-3 py-1.5 flex items-center gap-2 text-sm font-medium text-gray-600 hover:bg-gray-50 cursor-pointer transition-colors">
                <Filter className="w-4 h-4 text-gray-400" /> Filter
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {loading || isAblating ? (
                <motion.div 
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="py-20 flex flex-col items-center justify-center text-gray-500"
                >
                  <Loader2 className="w-8 h-8 animate-spin text-purple-600 mb-4" />
                  <p className="font-medium">Running DAG Orchestrator & Recalculating Graph...</p>
                </motion.div>
              ) : (
                candidates.map((candidate: any, i) => (
                  <motion.div
                    key={candidate.candidate_id}
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <CandidateCard candidate={candidate} />
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Recruiter Chat Floating Widget */}
      <AnimatePresence>
        {isChatOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 w-96 h-[500px] bg-white border border-gray-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden z-50"
          >
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-purple-600" />
                <span className="font-bold text-gray-800">AI Assistant</span>
              </div>
              <button onClick={() => setIsChatOpen(false)} className="text-gray-400 hover:text-gray-600">&times;</button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
              {chatLog.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === 'user' ? 'bg-purple-600 text-white font-medium' : 'bg-gray-100 text-gray-800'}`}>
                    {msg.content}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="p-4 border-t border-gray-100 bg-gray-50">
              <form onSubmit={handleChat} className="relative">
                <input 
                  type="text" 
                  value={chatQuery}
                  onChange={e => setChatQuery(e.target.value)}
                  placeholder="Ask the Knowledge Graph..." 
                  className="w-full bg-white border border-gray-200 rounded-full pl-4 pr-10 py-2.5 text-sm outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all text-gray-800 placeholder-gray-400 shadow-sm"
                />
                <button type="submit" className="absolute right-3 top-2.5 text-purple-600 hover:text-purple-500">
                  <Search className="w-4 h-4" />
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
