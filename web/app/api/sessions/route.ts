import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import sqlite3 from 'sqlite3'
import { promisify } from 'util'

const dbPath = path.join(process.cwd(), '..', 'storage', 'conversations.db')

function getDb() {
  return new sqlite3.Database(dbPath)
}

const dbAll = (db: sqlite3.Database, query: string, params: any[] = []) => {
  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      if (err) reject(err)
      else resolve(rows)
    })
  })
}

export async function GET() {
  try {
    // Check if database exists
    if (!fs.existsSync(dbPath)) {
      return NextResponse.json({ sessions: [] })
    }

    const db = getDb()

    const sessions = await dbAll(db, `
      SELECT s.*, 
        (SELECT COUNT(*) FROM messages WHERE session_id = s.id) as message_count
      FROM sessions s
      ORDER BY s.started_at DESC
    `)

    db.close()

    return NextResponse.json({ sessions })
  } catch (error) {
    console.error('Error fetching sessions:', error)
    return NextResponse.json(
      { error: 'Failed to fetch sessions' },
      { status: 500 }
    )
  }
}

