import type { NextApiRequest, NextApiResponse } from 'next';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL as string;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_KEY as string;
const supabase = createClient(supabaseUrl, supabaseKey);

interface BookEmbedding {
    book_id: string;
    title: string;
    embedding: number[];
}

interface SimilarBook {
    book_id: string;
    title: string;
    similarity: number;
}

interface GraphNode {
    id: string;
    label: string;
}

interface GraphEdge {
    from: string;
    to: string;
    weight: number;
}

interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    const { bookId } = req.query;

    // Fetch the embedding of the selected book
    const { data: book, error: bookError } = await supabase
        .from('book_embeddings')
        .select('embedding')
        .eq('book_id', bookId as string)
        .single();

    if (bookError || !book) {
        return res.status(404).json({ error: 'Book not found' });
    }

    const bookEmbedding = book.embedding;

    // Perform a similarity search to find similar books
    const { data: similarBooks, error: searchError } = await supabase.rpc('similar_books', { query_embedding: bookEmbedding });

    if (searchError) {
        return res.status(500).json({ error: searchError.message });
    }

    // Generate the graph data (nodes and edges)
    const nodes: GraphNode[] = similarBooks.map((b : SimilarBook) => ({
        id: b.book_id,
        label: b.title,
    }));

    const edges: GraphEdge[] = similarBooks.map((b : SimilarBook) => ({
        from: bookId as string,
        to: b.book_id,
        weight: b.similarity,
    }));

    const graphData: GraphData = { nodes, edges };

    res.status(200).json(graphData);
}
