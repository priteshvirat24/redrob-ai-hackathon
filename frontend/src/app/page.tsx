"use client"

import * as React from "react"
import { CandidateCard } from "@/components/CandidateCard"
import { Search, Filter, Loader2, Sparkles, Brain, Code, MapPin } from "lucide-react"

export default function Home() {
  const [candidates, setCandidates] = React.useState([])
  const [loading, setLoading] = React.useState(true)
  const [stats, setStats] = React.useState<any>(null)

  React.useEffect(() => {
    Promise.all([
      fetch("http://localhost:8000/api/candidates/top").then(res => res.json()),
      fetch("http://localhost:8000/api/analytics").then(res => res.json())
    ]).then(([candsData, statsData]) => {
      setCandidates(candsData.candidates)
      setStats(statsData)
      setLoading(false)
    })
  }, [])

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <header className="border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary text-primary-foreground p-1.5 rounded-md">
              <Brain className="w-5 h-5" />
            </div>
            <h1 className="font-bold text-xl tracking-tight">Redrob AI Copilot</h1>
          </div>
          <div className="flex items-center gap-4 text-sm font-medium text-muted-foreground">
            <span className="flex items-center gap-1.5"><Code className="w-4 h-4"/> Hackathon Submission</span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 mt-8">
        {/* Dashboard Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-2">Senior AI Engineer</h2>
            <p className="text-muted-foreground flex items-center gap-2">
              <MapPin className="w-4 h-4"/> Pune / Noida • Top 100 Ranked Candidates
            </p>
          </div>
          
          {stats && (
            <div className="flex gap-4">
              <div className="bg-card border rounded-lg px-4 py-2 text-center">
                <div className="text-2xl font-bold text-primary">{stats.metrics.ndcg_10}</div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">NDCG@10</div>
              </div>
              <div className="bg-card border rounded-lg px-4 py-2 text-center">
                <div className="text-2xl font-bold text-primary">{stats.total_processed.toLocaleString()}</div>
                <div className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Analyzed</div>
              </div>
            </div>
          )}
        </div>

        {/* Toolbar */}
        <div className="flex gap-3 mb-8">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search by skill, title, or reason..." 
              className="w-full pl-9 pr-4 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border rounded-md bg-card hover:bg-accent hover:text-accent-foreground text-sm font-medium transition-colors">
            <Filter className="w-4 h-4" /> Filters
          </button>
          <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors ml-auto">
            <Sparkles className="w-4 h-4" /> Generate Report
          </button>
        </div>

        {/* Grid */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
            <Loader2 className="w-8 h-8 animate-spin mb-4 text-primary" />
            <p>Analyzing 100,000 candidates...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {candidates.map((cand: any) => (
              <CandidateCard key={cand.candidate_id} candidate={cand} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
