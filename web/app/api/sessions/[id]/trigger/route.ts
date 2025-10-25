import { NextResponse } from 'next/server'
import path from 'path'

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const sessionId = params.id

    console.log('🔄 Triggering next turn for session:', sessionId)

    // Create signal file to trigger next turn
    const fs = require('fs').promises
    const projectRoot = path.resolve(process.cwd(), '..')
    const signalPath = path.join(projectRoot, 'storage', `continue_${sessionId}.txt`)

    // Write signal file with auto-trigger marker
    await fs.writeFile(signalPath, 'auto_trigger', 'utf-8')
    console.log('✅ Created trigger signal:', signalPath)

    return NextResponse.json({
      success: true,
      sessionId
    })

  } catch (error) {
    console.error('Error triggering next turn:', error)
    return NextResponse.json(
      { error: 'Failed to trigger next turn' },
      { status: 500 }
    )
  }
}

