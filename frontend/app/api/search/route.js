// app/api/search/route.js
export async function POST(req) {
    const { query, selectedCategory, isChecked } = await req.json();
  
    // API 로직을 처리하고 응답을 반환
    return new Response(
      JSON.stringify({
        message: 'Search successfully processed',
        query,
        selectedCategory,
        isChecked,
      }),
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
  