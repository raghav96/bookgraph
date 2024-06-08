import type { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY as string;
const supabase = createClient(supabaseUrl, supabaseKey);

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { query } = req.query;
    
    // Get embeddings for the query using Google Gemini model
    const response = await fetch("https://gemini.googleapis.com/v1/embeddings", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: query })
    });
    const { embeddings } = await response.json();

    // Perform a similarity search in the vector database
    const { data, error } = await supabase.rpc('similar_books', { query_embedding: embeddings });
    
    if (error) {
        return res.status(500).json({ error: error.message });
    }

    res.status(200).json(data);
}
