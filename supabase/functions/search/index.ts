import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.7.1'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')!;
const supabase = createClient(supabaseUrl, supabaseKey);
var session = new Supabase.ai.Session('gte-small');

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, x-api-key, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
}

Deno.serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response(null, { 
      status: 204, 
      headers: corsHeaders 
    });
  }

  const url = new URL(req.url);
  const input = url.searchParams.get('input');

  if (!input) {
    return new Response(JSON.stringify({ error: "No input provided" }), {
      status: 400,
      headers: {...corsHeaders, 'Content-Type': 'application/json'}
    });
  }

  var embeddings = await session.run(input, {
    mean_pool: true,
    normalize: true
  });

  console.log(embeddings);

  var { data, error } = await supabase.rpc('match_documents', {
    query_embedding: embeddings,
    match_threshold: 0.78,
    match_count: 10
  });

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: {...corsHeaders, 'Content-Type': 'application/json'}
    });
  }

  // Remove duplicate books based on metadata.book_id
  const uniqueBooks = Array.from(
    new Map(data.map(book => [book.metadata.book_id, book])).values()
  );

  return new Response(JSON.stringify({ "top10Books": uniqueBooks }), {
    status: 200,
    headers: {...corsHeaders, 'Content-Type': 'application/json'}
  });
});
