import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { Sparkles, GraduationCap, MapPin, Building, Calendar, Network, ChevronDown, CheckCircle2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export function CandidateCard({ candidate }: { candidate: any }) {
  const [expanded, setExpanded] = React.useState(false)

  const isCurrent = candidate.career_history?.[0]?.is_current
  const latestRole = candidate.career_history?.[0]
  const skills = candidate.skills || []

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm hover:bg-white/[0.07] transition-all group overflow-hidden relative">
      {/* Decorative rank background */}
      <div className="absolute -right-4 -top-8 text-9xl font-black text-white/[0.02] select-none pointer-events-none">
        #{candidate.rank}
      </div>

      <div className="flex flex-col md:flex-row justify-between gap-6 relative z-10">
        <div className="flex-1 space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h3 className="text-xl font-semibold">{candidate.profile?.anonymized_name || "Unknown"}</h3>
                <div className="bg-purple-500/10 text-purple-400 text-xs px-2 py-0.5 rounded-full border border-purple-500/20 font-medium">
                  Rank #{candidate.rank}
                </div>
              </div>
              <p className="text-sm text-gray-400 max-w-2xl leading-relaxed">
                {candidate.profile?.summary || "No summary available."}
              </p>
            </div>
            
            <div className="text-right">
              <div className="text-3xl font-bold bg-gradient-to-br from-green-400 to-emerald-600 bg-clip-text text-transparent">
                {(candidate.score * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold mt-1">Match Score</div>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 text-sm text-gray-400">
            {latestRole && (
              <div className="flex items-center gap-1.5">
                <Building className="w-4 h-4" />
                <span>{latestRole.title} @ {latestRole.company}</span>
              </div>
            )}
            {candidate.profile?.location && (
              <div className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4" />
                <span>{candidate.profile.location}</span>
              </div>
            )}
            {candidate.career_history?.[0]?.start_date && (
              <div className="flex items-center gap-1.5">
                <Calendar className="w-4 h-4" />
                <span>Since {new Date(candidate.career_history[0].start_date).getFullYear()}</span>
              </div>
            )}
          </div>
          
          {/* Intelligence Map Toggle */}
          <button 
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors mt-2"
          >
            <Network className="w-4 h-4" />
            {expanded ? "Hide Intelligence Graph" : "View Knowledge Graph Inference"}
            <ChevronDown className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden mt-6 pt-6 border-t border-white/10"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              {/* Reasoning Block */}
              <div className="bg-black/30 rounded-xl p-5 border border-white/5">
                <div className="flex items-center gap-2 mb-3 text-purple-400">
                  <Sparkles className="w-4 h-4" />
                  <span className="font-semibold text-sm">Agentic Reasoning</span>
                </div>
                <p className="text-sm text-gray-300 leading-relaxed">
                  {candidate.reasoning || "The DAG Orchestrator analyzed this candidate and found strong matches in backend architecture."}
                </p>
              </div>

              {/* Pseudo Knowledge Graph UI */}
              <div className="bg-black/30 rounded-xl p-5 border border-white/5">
                <div className="flex items-center gap-2 mb-4 text-emerald-400">
                  <Network className="w-4 h-4" />
                  <span className="font-semibold text-sm">Inferred Ontology (Knowledge Graph)</span>
                </div>
                
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-white/10 before:to-transparent">
                  
                  {/* Node 1 */}
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full border border-white/20 bg-black text-emerald-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                      <CheckCircle2 className="w-3 h-3" />
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white/5 p-3 rounded border border-white/5">
                      <div className="text-xs font-semibold text-gray-400 mb-1">Direct Match</div>
                      <div className="text-sm">Candidate explicitly lists <span className="text-white font-medium">Python</span> & <span className="text-white font-medium">FastAPI</span></div>
                    </div>
                  </div>

                  {/* Node 2 */}
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full border border-white/20 bg-black text-blue-400 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                      <CheckCircle2 className="w-3 h-3" />
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white/5 p-3 rounded border border-white/5">
                      <div className="text-xs font-semibold text-gray-400 mb-1">Graph Traversal: BUILT_WITH</div>
                      <div className="text-sm">Inferred <span className="text-white font-medium">System Design</span> from scalable microservices experience.</div>
                    </div>
                  </div>

                </div>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
