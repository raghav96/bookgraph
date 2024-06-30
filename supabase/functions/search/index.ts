import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.7.1'

const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')!;
const supabase = createClient(supabaseUrl, supabaseKey);
var session = new Supabase.ai.Session('gte-small');

Deno.serve(async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
    });
  }
  

  var input = await req.json();
  console.log(input);

  if (!input) {
    return new Response(JSON.stringify({ error: "No input provided" }), {
      status: 400,
    });
  }

  console.log(session);

  var embeddings = await session.run(input.input, {
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
    });
  }

  console.log(data);

  return new Response(JSON.stringify({ "top10Books": data }), {
    status: 200,
  });
});
