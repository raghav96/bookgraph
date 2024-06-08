import React, { useState } from 'react';
import axios from 'axios';

interface Book {
    id: string,
    title: string
}

interface GraphData {
    nodes: Array<{ id: string; label: string }>;
    edges: Array<{ from: string; to: string; weight: number }>;
}

const BookSearch: React.FC = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<Book[]>([]);
    const [selectedBook, setSelectedBook] = useState<string>(``);
    const [graph, setGraph] = useState<GraphData>({ nodes: [], edges: [] });

    const searchBooks = async () => {
        const response = await axios.get(`/api/search?query=${query}`);
        setResults(response.data);
    };

    const loadGraph = async (bookId: string) => {
        const response = await axios.get(`/api/graph?bookId=${bookId}`);
        setGraph(response.data);
        setSelectedBook(bookId);
    };

    return (
        <div>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={searchBooks}>Search</button>
            <ul>
                {results.map((book) => (
                    <li key={book.id} onClick={() => loadGraph(book.id)}>
                        {book.title}
                    </li>
                ))}
            </ul>
            <div id="graph">
                {/* Render graph here using a library like D3.js or Cytoscape */}
            </div>
        </div>
    );
};

export default BookSearch;
