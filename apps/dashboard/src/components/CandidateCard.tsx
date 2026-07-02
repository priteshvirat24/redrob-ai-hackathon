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
    <div className="bg-white border border-gray-200 shadow-sm rounded-2xl p-6 hover:shadow-md transition-all group overflow-hidden relative">
      {/* Decorative rank background */}
      <div className="absolute -right-4 -top-8 text-9xl font-black text-gray-50 select-none pointer-events-none">
        #{candidate.rank}
      </div>

      <div className="flex flex-col md:flex-row justify-between gap-6 relative z-10">
        <div className="flex-1 space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h3 className="text-xl font-bold text-gray-900">{candidate.profile?.anonymized_name || "Unknown"}</h3>
                <div className="bg-purple-100 text-purple-700 text-xs px-2.5 py-0.5 rounded-full border border-purple-200 font-bold uppercase tracking-wide">
                  Rank #{candidate.rank}
                </div>
              </div>
              <p className="text-sm text-gray-600 max-w-2xl leading-relaxed font-medium">
                {candidate.profile?.summary || "No summary available."}
              </p>
            </div>
            
            <div className="text-right">
              <div className="text-3xl font-black bg-gradient-to-br from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                {(candidate.score * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-400 uppercase tracking-wider font-bold mt-1">Match Score</div>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 text-sm text-gray-500 font-medium">
            {latestRole && (
              <div className="flex items-center gap-1.5 bg-gray-50 px-2.5 py-1 rounded-md border border-gray-100">
                <Building className="w-4 h-4 text-gray-400" />
                <span>{latestRole.title} @ <span className="text-gray-700 font-semibold">{latestRole.company}</span></span>
              </div>
            )}
            {candidate.profile?.location && (
              <div className="flex items-center gap-1.5 bg-gray-50 px-2.5 py-1 rounded-md border border-gray-100">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span>{candidate.profile.location}</span>
              </div>
            )}
            {candidate.career_history?.[0]?.start_date && (
              <div className="flex items-center gap-1.5 bg-gray-50 px-2.5 py-1 rounded-md border border-gray-100">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span>Since {new Date(candidate.career_history[0].start_date).getFullYear()}</span>
              </div>
            )}
          </div>
          
          {/* Intelligence Map Toggle */}
          <button 
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-sm font-bold text-purple-600 hover:text-purple-700 transition-colors mt-2 bg-purple-50 hover:bg-purple-100 px-3 py-1.5 rounded-lg"
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
            className="overflow-hidden mt-6 pt-6 border-t border-gray-100"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              {/* Reasoning Block */}
              <div className="bg-gradient-to-br from-purple-50 to-white rounded-xl p-5 border border-purple-100 shadow-sm">
                <div className="flex items-center gap-2 mb-3 text-purple-700">
                  <Sparkles className="w-4 h-4" />
                  <span className="font-bold text-sm uppercase tracking-wide">Agentic Reasoning</span>
                </div>
                <p className="text-sm text-gray-700 leading-relaxed font-medium">
                  {candidate.reasoning || "The DAG Orchestrator analyzed this candidate and found strong matches in backend architecture."}
                </p>
              </div>

              {/* Pseudo Knowledge Graph UI */}
              <div className="bg-gray-50 rounded-xl p-5 border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 mb-4 text-gray-900">
                  <Network className="w-4 h-4 text-purple-600" />
                  <span className="font-bold text-sm uppercase tracking-wide">Inferred Ontology</span>
                </div>
                
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-gray-300 before:to-transparent">
                  
                  {/* Node 1 */}
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full border-2 border-white bg-purple-600 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                      <CheckCircle2 className="w-3 h-3" />
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                      <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Direct Match</div>
                      <div className="text-sm text-gray-600 font-medium">Candidate explicitly lists <span className="text-purple-700 font-bold">Python</span> & <span className="text-purple-700 font-bold">FastAPI</span></div>
                    </div>
                  </div>

                  {/* Node 2 */}
                  <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full border-2 border-white bg-indigo-500 text-white shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                      <CheckCircle2 className="w-3 h-3" />
                    </div>
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                      <div className="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">Graph Traversal: BUILT_WITH</div>
                      <div className="text-sm text-gray-600 font-medium">Inferred <span className="text-indigo-600 font-bold">System Design</span> from scalable microservices experience.</div>
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
