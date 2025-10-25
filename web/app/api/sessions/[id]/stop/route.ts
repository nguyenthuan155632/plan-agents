import { NextRequest, NextResponse } from 'next/server'
import sqlite3 from 'sqlite3'
import path from 'path'

const projectRoot = path.join(process.cwd(), '..')
const dbPath = path.join(projectRoot, 'storage', 'conversations.db')

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const sessionId = params.id

  return new Promise((resolve) => {
    const db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('❌ Failed to open database:', err)
        resolve(NextResponse.json(
          { error: 'Failed to connect to database' },
          { status: 500 }
        ))
        return
      }

      // Get current timestamp
      const timestamp = new Date().toISOString()

      // Insert a special human message indicating stop request
      db.run(
        `INSERT INTO messages (session_id, role, content, signal, timestamp) 
         VALUES (?, ?, ?, ?, ?)`,
        [sessionId, 'Human', '🛑 STOP - Please summarize everything we discussed.', 'continue', timestamp],
        function (insertErr) {
          if (insertErr) {
            console.error('❌ Failed to insert stop message:', insertErr)
            db.close()
            resolve(NextResponse.json(
              { error: 'Failed to insert stop message' },
              { status: 500 }
            ))
            return
          }

          console.log(`🛑 Human requested stop for session ${sessionId}, inserted stop message`)

          // Create signal file to trigger agent processing
          const fs = require('fs')
          const signalPath = path.join(projectRoot, 'storage', `continue_${sessionId}.txt`)

          try {
            fs.writeFileSync(signalPath, timestamp)
            console.log(`📝 Created signal file: ${signalPath}`)
          } catch (fsErr) {
            console.error('❌ Failed to create signal file:', fsErr)
          }

          db.close()
          resolve(NextResponse.json({
            success: true,
            message: 'Stop request sent to agents. They will provide a summary.'
          }))
        }
      )
    })
  })
}
