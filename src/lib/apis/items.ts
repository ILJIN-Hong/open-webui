const RAG_BASE_URL = 'http://192.168.141.235:9000';

export async function fetchItems() {
  const res = await fetch(`${RAG_BASE_URL}/api/items/list`);
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  const data = await res.json();
  
  // RAG API 서버에서 이미 items 배열을 반환하므로 직접 사용
  return data;
}

export async function fetchItem(itemId: string) {
  const res = await fetch(`${RAG_BASE_URL}/api/items/get/${itemId}`);
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  const data = await res.json();
  
  // RAG API 서버에서 직접 아이템을 반환
  return data;
}

export async function createItem(itemData: any) {
  // RAG API 서버의 /items/add 엔드포인트 사용
  const res = await fetch(`${RAG_BASE_URL}/api/items/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: itemData.name,
      description: itemData.description,
      created_at: itemData.created_at
    })
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  const data = await res.json();
  return data;
}

export async function updateItem(itemId: string, itemData: any) {
  const requestBody = {
    name: itemData.name,
    description: itemData.description,
    status: itemData.status,
    properties: itemData.properties  // 트리 구조 데이터 포함
  };
  
  console.log('=== updateItem API 호출 ===');
  console.log('URL:', `${RAG_BASE_URL}/api/items/update/${itemId}`);
  console.log('전송 데이터:', requestBody);
  console.log('========================');
  
  const res = await fetch(`${RAG_BASE_URL}/api/items/update/${itemId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  const data = await res.json();
  return data;
}

export async function deleteItem(itemId: string) {
  const res = await fetch(`${RAG_BASE_URL}/api/items/delete/${itemId}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  return { message: 'Item deleted successfully' };
}

export async function fetchSummaryFormat(itemId: string) {
  const item = await fetchItem(itemId);
  return item.summary_format || {
    "제품명": "",
    "규격": "",
    "수량": 0,
    "단가": 0,
    "총액": 0,
    "납기": "",
    "비고": ""
  };
}

export async function updateSummaryFormat(itemId: string, summary: any) {
  const res = await fetch(`${RAG_BASE_URL}/api/items/summary/${itemId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      summary_format: summary
    })
  });
  
  if (!res.ok) {
    throw new Error(`RAG API Error: ${res.status}`);
  }
  
  return { message: 'Summary format updated successfully' };
} 