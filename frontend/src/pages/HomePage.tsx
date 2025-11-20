import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'

function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6">
      <div className="flex items-center gap-2">
        <Sparkles className="w-8 h-8 text-primary" />
        <h1 className="text-4xl font-bold">Welcome to Devv Builder</h1>
      </div>
      <Button size="lg" className="mt-4">
        Start Building
      </Button>
    </div>
  )
}

export default HomePage 