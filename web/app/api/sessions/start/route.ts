import { NextResponse } from 'next/server'
import sqlite3 from 'sqlite3'
import path from 'path'
import { randomUUID } from 'crypto'

// Helper to open database
function openDb(): Promise<sqlite3.Database> {
  return new Promise((resolve, reject) => {
    // Next.js runs in web/ directory, so we need to go up to project root
    const projectRoot = path.resolve(process.cwd(), '..')
    const dbPath = path.join(projectRoot, 'storage', 'conversations.db')
    console.log('📂 Database path:', dbPath)

    const db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('❌ Failed to open database:', err)
        reject(err)
      } else {
        console.log('✅ Database opened successfully')
        resolve(db)
      }
    })
  })
}

// Helper to run SQL
function dbRun(db: sqlite3.Database, sql: string, params: any[]): Promise<{ lastID: number }> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err)
      else resolve({ lastID: this.lastID })
    })
  })
}

export async function POST(request: Request) {
  try {
    const { topic } = await request.json()

    if (!topic || topic.trim().length === 0) {
      return NextResponse.json(
        { error: 'Topic is required' },
        { status: 400 }
      )
    }

    const db = await openDb()

    // Generate UUID for session ID (schema requires TEXT, not INTEGER)
    const sessionId = randomUUID()

    // Create new session with UUID and topic
    await dbRun(
      db,
      'INSERT INTO sessions (id, topic, status, started_at) VALUES (?, ?, ?, ?)',
      [sessionId, topic, 'active', new Date().toISOString()]
    )

    // Add initial human message
    await dbRun(
      db,
      `INSERT INTO messages (session_id, role, content, signal, timestamp)
       VALUES (?, ?, ?, ?, ?)`,
      [
        sessionId,
        'Human',
        `Let's discuss: ${topic}`,
        'continue',
        new Date().toISOString()
      ]
    )

    db.close()

    // Trigger backend to start processing
    // We'll use a simple file-based signal
    const fs = require('fs').promises
    const projectRoot = path.resolve(process.cwd(), '..')
    const signalPath = path.join(projectRoot, 'storage', `signal_${sessionId}.txt`)
    console.log('📝 Creating signal file:', signalPath)
    await fs.writeFile(signalPath, topic, 'utf-8')

    return NextResponse.json({
      success: true,
      sessionId: sessionId  // Already a string (UUID)
    })

  } catch (error) {
    console.error('Error starting session:', error)
    return NextResponse.json(
      { error: 'Failed to start session' },
      { status: 500 }
    )
  }
}

