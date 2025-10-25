import { NextResponse } from 'next/server'
import sqlite3 from 'sqlite3'
import path from 'path'

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
function dbRun(db: sqlite3.Database, sql: string, params: any[]): Promise<void> {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) reject(err)
      else resolve()
    })
  })
}

// Helper to get one row
function dbGet(db: sqlite3.Database, sql: string, params: any[]): Promise<any> {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) reject(err)
      else resolve(row)
    })
  })
}

export async function POST(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const { message } = await request.json()
    const sessionId = params.id

    if (!message || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    const db = await openDb()

    // Check if session exists and get last message
    const session = await dbGet(
      db,
      'SELECT status FROM sessions WHERE id = ?',
      [sessionId]
    )

    if (!session) {
      db.close()
      return NextResponse.json(
        { error: 'Session not found' },
        { status: 404 }
      )
    }

    // Get the last message to check signal
    const lastMessage = await dbGet(
      db,
      `SELECT signal FROM messages 
       WHERE session_id = ? 
       ORDER BY timestamp DESC 
       LIMIT 1`,
      [sessionId]
    )

    // Allow human to jump in at any time (not just handover)
    // This enables the "Jump In" feature
    if (!lastMessage) {
      db.close()
      return NextResponse.json(
        { error: 'No messages found in session' },
        { status: 400 }
      )
    }

    // Reactivate session if it was completed
    if (session.status === 'completed') {
      await dbRun(
        db,
        'UPDATE sessions SET status = ? WHERE id = ?',
        ['active', sessionId]
      )
    }

    // Add human message
    await dbRun(
      db,
      `INSERT INTO messages (session_id, role, content, signal, timestamp)
       VALUES (?, ?, ?, ?, ?)`,
      [
        sessionId,
        'Human',
        message,
        'continue',
        new Date().toISOString()
      ]
    )

    db.close()

    // Signal backend to continue processing
    const fs = require('fs').promises
    const projectRoot = path.resolve(process.cwd(), '..')
    const signalPath = path.join(projectRoot, 'storage', `continue_${sessionId}.txt`)
    console.log('📝 Creating signal file:', signalPath)
    await fs.writeFile(signalPath, message, 'utf-8')

    return NextResponse.json({
      success: true,
      sessionId
    })

  } catch (error) {
    console.error('Error continuing session:', error)
    return NextResponse.json(
      { error: 'Failed to continue session' },
      { status: 500 }
    )
  }
}

