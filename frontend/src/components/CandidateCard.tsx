"use client"

import * as React from "react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MapPin, Briefcase, Star, Github, Activity } from "lucide-react"

export function CandidateCard({ candidate }: { candidate: any }) {
  const p = candidate.profile
  const features = candidate.features
  
  return (
    <Card className="hover:border-primary/50 transition-colors bg-card/50 backdrop-blur-sm relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <Badge variant="outline" className="font-mono">#{candidate.rank}</Badge>
      </div>
      
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl flex items-center gap-2">
              {p.anonymized_name}
              {features.title_tier >= 4 && <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />}
            </CardTitle>
            <CardDescription className="text-base mt-1 text-primary/80 font-medium">
              {p.current_title}
            </CardDescription>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
              {(candidate.score * 100).toFixed(1)}
            </div>
            <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Match Score</div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-3 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-md">
            <Briefcase className="w-4 h-4 text-primary" />
            {p.years_of_experience} yrs exp
          </div>
          <div className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-md">
            <MapPin className="w-4 h-4 text-primary" />
            {p.location}
          </div>
          <div className="flex items-center gap-1.5 bg-secondary/50 px-2.5 py-1 rounded-md">
            <Activity className="w-4 h-4 text-green-400" />
            Resp: {(features.behavioral_score * 100).toFixed(0)}%
          </div>
        </div>
        
        <div className="bg-muted/30 p-3 rounded-lg border border-border/50 text-sm italic text-muted-foreground leading-relaxed">
          "{candidate.reasoning}"
        </div>
        
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Key Skills</div>
          <div className="flex flex-wrap gap-1.5">
            {candidate.skills.slice(0, 8).map((s: any, i: number) => {
              const isAi = ["PyTorch", "TensorFlow", "NLP", "Embeddings", "RAG", "FAISS", "Qdrant"].includes(s.name)
              return (
                <Badge key={i} variant={isAi ? "default" : "secondary"} className={isAi ? "bg-primary/20 text-primary-foreground" : ""}>
                  {s.name}
                </Badge>
              )
            })}
            {candidate.skills.length > 8 && (
              <Badge variant="outline">+{candidate.skills.length - 8} more</Badge>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
