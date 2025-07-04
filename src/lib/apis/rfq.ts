const API_BASE_URL = import.meta.env.VITE_VECTOR_DB_API_URL;

export async function fetchRFQs() {
    const res = await fetch(`${API_BASE_URL}/api/rfq/list`);
    if (!res.ok) throw new Error('API Error');
    return await res.json();
  }